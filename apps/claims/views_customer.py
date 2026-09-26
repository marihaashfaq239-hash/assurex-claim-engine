"""
AssureX — Customer Claim Views
Handles: customer dashboard, my claims list, claim detail/tracking.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q

from .models import Claim
from apps.products.models import Product
from apps.warranties.models import Warranty
from apps.notifications.models import Notification
from apps.accounts.decorators import customer_required


@login_required
def customer_dashboard(request):
    """
    Customer home — stats, active warranties, recent claims, expiring products.
    Accessible to both customers AND employees (who may also view their own).
    """
    user = request.user

    # Products
    products = Product.objects.filter(owner=user, is_active=True).select_related('category')
    total_products = products.count()

    # Warranties
    warranties = Warranty.objects.filter(product__owner=user)
    today = timezone.now().date()
    for w in warranties:
        w.update_status()

    active_warranties  = warranties.filter(status='active').count()
    expiring_soon      = warranties.filter(status='expiring')
    expired_warranties = warranties.filter(status='expired').count()

    # Claims
    claims = Claim.objects.filter(claimant=user).order_by('-created_at')
    total_claims    = claims.count()
    pending_claims  = claims.filter(status__in=['submitted', 'evaluation', 'manual', 'additional']).count()
    approved_claims = claims.filter(status='approved').count()
    rejected_claims = claims.filter(status='rejected').count()

    recent_claims = claims[:5]

    # Notifications (unread)
    recent_notifications = Notification.objects.filter(
        recipient=user, is_read=False
    ).order_by('-created_at')[:5]

    context = {
        'page_title':          'My Dashboard',
        'total_products':      total_products,
        'active_warranties':   active_warranties,
        'expired_warranties':  expired_warranties,
        'expiring_soon':       expiring_soon,
        'total_claims':        total_claims,
        'pending_claims':      pending_claims,
        'approved_claims':     approved_claims,
        'rejected_claims':     rejected_claims,
        'recent_claims':       recent_claims,
        'recent_notifications':recent_notifications,
        'products':            products[:6],
    }
    return render(request, 'dashboard/customer_dashboard.html', context)


@login_required
def my_claims(request):
    """Customer's full claim list with search + filter."""
    claims = Claim.objects.filter(claimant=request.user).select_related(
        'product', 'warranty'
    ).order_by('-created_at')

    # Filters
    status_filter = request.GET.get('status', '')
    search        = request.GET.get('q', '')

    if status_filter:
        claims = claims.filter(status=status_filter)
    if search:
        claims = claims.filter(
            Q(claim_reference__icontains=search) |
            Q(product__product_name__icontains=search) |
            Q(product__serial_number__icontains=search)
        )

    context = {
        'claims':         claims,
        'status_filter':  status_filter,
        'search':         search,
        'status_choices': Claim.STATUS_CHOICES,
        'page_title':     'My Claims',
    }
    return render(request, 'claims/my_claims.html', context)


@login_required
def claim_detail(request, pk):
    """
    Full claim detail — AI results, rule engine, reviewer comments, status timeline.
    SRS §1.6.xxxii — AI-Generated Claim Summary
    SRS §1.6.xxviii — Contradiction Detection (shown on detail page)
    """
    claim = get_object_or_404(
        Claim,
        pk=pk,
        claimant=request.user
    )
    documents    = claim.documents.all()
    ocr_results  = claim.ocr_results.all()
    rule_results = claim.rule_results.all()
    predictions  = claim.predictions.all()
    repair_hist  = claim.repair_history.all()
    review       = getattr(claim, 'review', None)

    # ── AI-Generated Claim Summary (SRS §1.6.xxxii) ──
    ai_summary = _build_ai_claim_summary(claim, documents, ocr_results, rule_results, repair_hist)

    # ── Contradiction Detection (SRS §1.6.xxviii) ──
    # Import locally to avoid circular import
    from apps.claims.views_submit import _detect_contradictions
    contradictions      = _detect_contradictions(claim)
    hard_contradictions = [c for c in contradictions if c['severity'] == 'hard']
    warn_contradictions = [c for c in contradictions if c['severity'] == 'warning']

    # ── Model confidence display ──
    py_confidences = None
    tm_confidences = None
    if claim.python_prediction:
        py_confidences = {
            'valid':   claim.python_confidence_valid or 0,
            'invalid': claim.python_confidence_invalid or 0,
            'manual':  claim.python_confidence_manual or 0,
        }
    if claim.tm_prediction:
        tm_confidences = {
            'valid':   claim.tm_confidence_valid or 0,
            'invalid': claim.tm_confidence_invalid or 0,
            'manual':  claim.tm_confidence_manual or 0,
        }

    context = {
        'claim':               claim,
        'documents':           documents,
        'ocr_results':         ocr_results,
        'rule_results':        rule_results,
        'predictions':         predictions,
        'repair_hist':         repair_hist,
        'review':              review,
        'ai_summary':          ai_summary,
        'contradictions':      contradictions,
        'hard_contradictions': hard_contradictions,
        'warn_contradictions': warn_contradictions,
        'py_confidences':      py_confidences,
        'tm_confidences':      tm_confidences,
        'page_title':          f'Claim {claim.claim_reference}',
    }
    return render(request, 'claims/claim_detail.html', context)


@login_required
def download_claim_report(request, pk):
    """
    SRS §1.6.xliv — Downloadable Claim Report.
    Generates a detailed HTML report for a claim that can be printed or saved as PDF.
    Contains: claim details, uploaded evidence, warranty status, Python model result,
    Google TM result, confidence comparison, rule-validation result, contradictions,
    final recommendation, and reviewer comments.
    """
    claim = get_object_or_404(Claim, pk=pk, claimant=request.user)

    documents    = claim.documents.all()
    ocr_results  = claim.ocr_results.all()
    rule_results = claim.rule_results.all()
    predictions  = claim.predictions.all()
    repair_hist  = claim.repair_history.all()
    review       = getattr(claim, 'review', None)

    # AI Summary
    ai_summary = _build_ai_claim_summary(claim, documents, ocr_results, rule_results, repair_hist)

    # Contradictions
    from apps.claims.views_submit import _detect_contradictions
    contradictions      = _detect_contradictions(claim)
    hard_contradictions = [c for c in contradictions if c['severity'] == 'hard']
    warn_contradictions = [c for c in contradictions if c['severity'] == 'warning']

    # Log export action
    from apps.accounts.models import AuditLog
    AuditLog.objects.create(
        user=request.user,
        action_type='report_exported',
        description=f'{request.user.email} downloaded report for claim {claim.claim_reference}.',
        object_type='Claim',
        object_id=str(claim.pk),
    )

    context = {
        'claim':               claim,
        'documents':           documents,
        'ocr_results':         ocr_results,
        'rule_results':        rule_results,
        'predictions':         predictions,
        'repair_hist':         repair_hist,
        'review':              review,
        'ai_summary':          ai_summary,
        'contradictions':      contradictions,
        'hard_contradictions': hard_contradictions,
        'warn_contradictions': warn_contradictions,
        'generated_at':        timezone.now(),
        'page_title':          f'Claim Report — {claim.claim_reference}',
    }
    return render(request, 'claims/claim_report.html', context)


def _build_ai_claim_summary(claim, documents, ocr_results, rule_results, repair_hist) -> dict:
    """
    SRS §1.6.xxxii — AI-Generated Claim Summary.
    Builds a structured summary dict of the claim covering:
    product, warranty coverage, reported fault, repair history,
    uploaded evidence, detected issues, and claim status.
    """
    from django.utils import timezone

    today = timezone.now().date()
    product = claim.product

    # Warranty info
    warranty = claim.warranty
    warranty_info = None
    if warranty:
        warranty_info = {
            'provider':      warranty.warranty_provider,
            'type':          warranty.get_warranty_type_display(),
            'start':         warranty.start_date,
            'expiry':        warranty.expiry_date,
            'remaining_days':warranty.remaining_days,
            'is_expired':    warranty.is_expired,
            'status':        warranty.get_status_display(),
        }

    # Document summary
    doc_types_uploaded = [d.get_doc_type_display() for d in documents]
    missing_docs       = list(claim.missing_document_types)

    # OCR extraction summary
    ocr_summary = []
    for ocr in ocr_results:
        if ocr.status != 'failed':
            ocr_summary.append({
                'doc':        str(ocr.document),
                'invoice':    ocr.invoice_number or '—',
                'serial':     ocr.serial_number or '—',
                'purchase':   str(ocr.purchase_date) if ocr.purchase_date else '—',
                'verified':   ocr.is_verified,
                'confidence': round((ocr.confidence or 0) * 100, 0),
            })

    # Repair summary
    repair_summary = []
    for r in repair_hist:
        repair_summary.append({
            'date':       r.repair_date,
            'center':     r.repair_center,
            'authorized': r.is_authorized,
            'outcome':    r.get_outcome_display(),
        })

    # Rule engine summary
    rules_passed  = [rr for rr in rule_results if rr.outcome == 'pass']
    rules_failed  = [rr for rr in rule_results if rr.outcome == 'fail']
    rules_warning = [rr for rr in rule_results if rr.outcome == 'warning']

    # Model decision summary
    model_info = {}
    if claim.python_prediction:
        top_py = max(
            claim.python_confidence_valid  or 0,
            claim.python_confidence_invalid or 0,
            claim.python_confidence_manual  or 0,
        )
        model_info['python'] = {
            'prediction': claim.python_prediction.replace('_', ' ').title(),
            'confidence': round(top_py, 1),
        }
    if claim.tm_prediction:
        top_tm = max(
            claim.tm_confidence_valid   or 0,
            claim.tm_confidence_invalid or 0,
            claim.tm_confidence_manual  or 0,
        )
        model_info['teachable_machine'] = {
            'prediction': claim.tm_prediction.replace('_', ' ').title(),
            'confidence': round(top_tm, 1),
        }
    if claim.model_consistency_status:
        model_info['consistency'] = claim.model_consistency_status.replace('_', ' ').title()
        model_info['conf_diff']   = claim.confidence_difference

    return {
        'product': {
            'name':         f'{product.brand} {product.product_name}',
            'model':        product.model_number,
            'serial':       product.serial_number,
            'purchased':    product.purchase_date,
            'age_months':   product.product_age_months,
        },
        'warranty':          warranty_info,
        'fault': {
            'date':          claim.fault_date,
            'type':          claim.get_damage_type_display(),
            'description':   claim.fault_description,
        },
        'repair_history':     repair_summary,
        'documents_uploaded': doc_types_uploaded,
        'missing_documents':  missing_docs,
        'ocr_extractions':    ocr_summary,
        'rules_passed':       [r.rule_name for r in rules_passed],
        'rules_failed':       [r.rule_name for r in rules_failed],
        'rules_warning':      [r.rule_name for r in rules_warning],
        'model_results':      model_info,
        'final_decision':     claim.get_final_decision_display() if claim.final_decision else None,
        'decision_reason':    claim.decision_reason or None,
        'claim_status':       claim.get_status_display(),
        'is_duplicate':       claim.is_duplicate,
    }
