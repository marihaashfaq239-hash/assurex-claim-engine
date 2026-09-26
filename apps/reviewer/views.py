"""
AssureX — Claim Reviewer Views
Handles: reviewer dashboard, manual review queue, claim review detail,
         approve/reject/request-more-info, AI override with audit trail.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.claims.models import Claim, Review
from apps.accounts.models import User, AuditLog
from apps.accounts.decorators import reviewer_required, reviewer_or_admin
from apps.notifications.models import Notification


def _log(request, action, desc, obj_type='', obj_id='', extra=None):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    AuditLog.objects.create(
        user=request.user, action_type=action, description=desc,
        ip_address=ip or None, object_type=obj_type, object_id=str(obj_id),
        extra_data=extra or {},
    )


# ─────────────────────────────────────────────────────────────────
# Reviewer Dashboard
# ─────────────────────────────────────────────────────────────────

@reviewer_required
def reviewer_dashboard(request):
    """Reviewer home — queue stats, urgent items, recent decisions."""
    # Queue = claims in manual review status not yet reviewed
    queue_qs = Claim.objects.filter(status='manual').select_related('product', 'claimant')

    # Stats
    total_queue       = queue_qs.count()
    high_priority     = queue_qs.filter(is_duplicate=False).count()
    reviewed_by_me    = Review.objects.filter(
        reviewer=request.user, decision__in=['approved', 'rejected', 'more_info']
    ).count()
    ai_overrides      = Review.objects.filter(reviewer=request.user, is_ai_override=True).count()
    pending_decisions = Review.objects.filter(reviewer=request.user, decision='pending').count()

    # Oldest unreviewed claim (most urgent)
    oldest_in_queue = queue_qs.order_by('created_at').first()

    # Recent reviews by this reviewer
    recent_reviews = Review.objects.filter(
        reviewer=request.user
    ).select_related('claim', 'claim__product', 'claim__claimant').order_by('-reviewed_at')[:6]

    # Queue preview (top 5)
    queue_preview = queue_qs.order_by('submission_date')[:5]

    context = {
        'page_title':       'Reviewer Dashboard',
        'total_queue':      total_queue,
        'high_priority':    high_priority,
        'reviewed_by_me':   reviewed_by_me,
        'ai_overrides':     ai_overrides,
        'pending_decisions':pending_decisions,
        'oldest_in_queue':  oldest_in_queue,
        'recent_reviews':   recent_reviews,
        'queue_preview':    queue_preview,
    }
    return render(request, 'dashboard/reviewer_dashboard.html', context)


# ─────────────────────────────────────────────────────────────────
# Manual Review Queue
# ─────────────────────────────────────────────────────────────────

@reviewer_required
def review_queue(request):
    """Full list of claims awaiting manual review."""
    claims = Claim.objects.filter(
        status='manual'
    ).select_related('product', 'claimant').order_by('submission_date')

    # Optional filters
    search = request.GET.get('q', '')
    if search:
        claims = claims.filter(
            Q(claim_reference__icontains=search) |
            Q(claimant__email__icontains=search) |
            Q(product__serial_number__icontains=search)
        )

    # Annotate with whether already reviewed
    for c in claims:
        c.already_reviewed = hasattr(c, 'review') and c.review.decision != 'pending'

    context = {
        'page_title': 'Manual Review Queue',
        'claims':     claims,
        'search':     search,
        'total':      claims.count(),
    }
    return render(request, 'reviewer/review_queue.html', context)


# ─────────────────────────────────────────────────────────────────
# Review Detail — Full claim info for reviewer
# ─────────────────────────────────────────────────────────────────

@reviewer_required
def review_detail(request, pk):
    """
    Reviewer views full claim details, AI results, rule engine output,
    then makes a decision: Approve / Reject / Request More Info / Override AI.
    """
    claim       = get_object_or_404(Claim, pk=pk, status='manual')
    documents   = claim.documents.all()
    rule_results = claim.rule_results.all()
    predictions  = claim.predictions.all()
    repair_hist  = claim.repair_history.all()
    ocr_results  = claim.ocr_results.all()

    # Get or create Review record for this claim
    review, created = Review.objects.get_or_create(
        claim=claim,
        defaults={
            'reviewer':           request.user,
            'python_prediction':  claim.python_prediction,
            'tm_prediction':      claim.tm_prediction,
            'model_consistency':  claim.model_consistency_status,
            'decision':           'pending',
        }
    )
    if created:
        _log(request, 'reviewer_action',
             f'Reviewer {request.user.email} opened claim {claim.claim_reference} for review.',
             'Claim', claim.pk)

    if request.method == 'POST':
        return _process_review(request, claim, review)

    context = {
        'page_title':  f'Review — {claim.claim_reference}',
        'claim':       claim,
        'review':      review,
        'documents':   documents,
        'rule_results':rule_results,
        'predictions': predictions,
        'repair_hist': repair_hist,
        'ocr_results': ocr_results,
    }
    return render(request, 'reviewer/review_detail.html', context)


def _process_review(request, claim, review):
    """Handle reviewer form submission."""
    decision   = request.POST.get('decision', '')
    comments   = request.POST.get('reviewer_comments', '').strip()
    more_info  = request.POST.get('additional_info_request', '').strip()
    is_override = request.POST.get('is_ai_override') == 'on'
    override_reason = request.POST.get('override_reason', '').strip()

    valid_decisions = ['approved', 'rejected', 'more_info']
    if decision not in valid_decisions:
        messages.error(request, 'Please select a valid decision.')
        return redirect('reviewer:detail', pk=claim.pk)

    if not comments:
        messages.error(request, 'Reviewer comments are required.')
        return redirect('reviewer:detail', pk=claim.pk)

    if decision == 'more_info' and not more_info:
        messages.error(request, 'Please specify what additional information is required.')
        return redirect('reviewer:detail', pk=claim.pk)

    if is_override and not override_reason:
        messages.error(request, 'Please provide a reason for overriding the AI result.')
        return redirect('reviewer:detail', pk=claim.pk)

    # Save review
    review.decision             = decision
    review.reviewer_comments    = comments
    review.additional_info_request = more_info
    review.is_ai_override       = is_override
    review.ai_original_result   = claim.final_decision if is_override else ''
    review.override_reason      = override_reason if is_override else ''
    review.reviewer             = request.user
    review.reviewed_at          = timezone.now()
    review.save()

    # Update claim status & final decision
    status_map = {
        'approved':  ('approved',  'likely_valid'),
        'rejected':  ('rejected',  'likely_invalid'),
        'more_info': ('additional','pending'),
    }
    new_status, new_decision = status_map[decision]
    claim.status         = new_status
    claim.final_decision = new_decision if decision != 'more_info' else claim.final_decision
    claim.save(update_fields=['status', 'final_decision', 'updated_at'])

    # Audit log
    _log(request, 'reviewer_action',
         f'Reviewer {request.user.email} → {decision} on {claim.claim_reference}.'
         + (f' AI Override: {override_reason}' if is_override else ''),
         'Claim', claim.pk,
         extra={'decision': decision, 'is_override': is_override})

    # Notify customer
    notif_msgs = {
        'approved':  ('Claim Approved', f'Your claim {claim.claim_reference} has been approved.', 'claim_approved'),
        'rejected':  ('Claim Rejected', f'Your claim {claim.claim_reference} has been rejected. See reviewer comments.', 'claim_rejected'),
        'more_info': ('Additional Information Required',
                      f'Your claim {claim.claim_reference} requires additional information.', 'additional_info'),
    }
    title, msg, ntype = notif_msgs[decision]
    Notification.send(
        recipient=claim.claimant,
        notification_type=ntype,
        title=title,
        message=msg,
        link=f'/claims/{claim.pk}/',
        object_type='Claim',
        object_id=claim.pk,
    )

    messages.success(request, f'Claim {claim.claim_reference} — decision saved: {decision.replace("_", " ").title()}')
    return redirect('reviewer:queue')


# ─────────────────────────────────────────────────────────────────
# Reviewed Claims History
# ─────────────────────────────────────────────────────────────────

@reviewer_required
def reviewed_claims(request):
    """All claims already reviewed by this reviewer."""
    reviews = Review.objects.filter(
        reviewer=request.user,
        decision__in=['approved', 'rejected', 'more_info']
    ).select_related('claim', 'claim__product', 'claim__claimant').order_by('-reviewed_at')

    search = request.GET.get('q', '')
    if search:
        reviews = reviews.filter(
            Q(claim__claim_reference__icontains=search) |
            Q(claim__claimant__email__icontains=search)
        )

    context = {
        'page_title': 'Reviewed Claims',
        'reviews':    reviews,
        'search':     search,
    }
    return render(request, 'reviewer/reviewed_claims.html', context)


# ─────────────────────────────────────────────────────────────────
# AI Override History
# ─────────────────────────────────────────────────────────────────

@reviewer_required
def override_history(request):
    """All claims where this reviewer overrode the AI result."""
    overrides = Review.objects.filter(
        reviewer=request.user, is_ai_override=True
    ).select_related('claim', 'claim__product', 'claim__claimant').order_by('-reviewed_at')

    context = {
        'page_title': 'AI Override History',
        'overrides':  overrides,
    }
    return render(request, 'reviewer/override_history.html', context)
