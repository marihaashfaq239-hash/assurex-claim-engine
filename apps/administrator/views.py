"""
AssureX — Administrator Views
Handles: admin dashboard, user management, warranty policies, analytics,
         model versions, AI thresholds, audit logs, monitoring, reports.
"""
import json
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User, AuditLog
from apps.claims.models import Claim, ModelVersion, Review
from apps.products.models import Product, ProductCategory
from apps.warranties.models import Warranty, WarrantyPolicy
from apps.notifications.models import Notification
from apps.accounts.decorators import admin_required
from .models import SystemConfiguration


# ─────────────────────────────────────────────────────────────────
# Admin Dashboard
# ─────────────────────────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    """System-wide overview dashboard."""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # Claim stats
    all_claims      = Claim.objects.all()
    total_claims    = all_claims.count()
    valid_claims    = all_claims.filter(final_decision='likely_valid').count()
    invalid_claims  = all_claims.filter(final_decision='likely_invalid').count()
    manual_claims   = all_claims.filter(status='manual').count()
    pending_claims  = all_claims.filter(status__in=['submitted', 'evaluation']).count()
    approved_claims = all_claims.filter(status='approved').count()
    rejected_claims = all_claims.filter(status='rejected').count()
    duplicate_alerts= all_claims.filter(is_duplicate=True).count()

    # Model disagreements (predictions don't match)
    model_disagreements = all_claims.filter(
        model_consistency_status__in=['model_disagreement', 'uncertain_result']
    ).count()

    # Users
    total_users    = User.objects.filter(is_active=True).count()
    customers      = User.objects.filter(role=User.CUSTOMER).count()
    employees      = User.objects.filter(role=User.EMPLOYEE).count()
    reviewers      = User.objects.filter(role=User.REVIEWER).count()

    # This week's claims (for trend chart)
    claims_this_week = []
    for i in range(7):
        day = today - timedelta(days=6 - i)
        cnt = all_claims.filter(created_at__date=day).count()
        claims_this_week.append({'date': str(day), 'count': cnt})

    # Recent claims
    recent_claims = all_claims.select_related(
        'product', 'claimant'
    ).order_by('-created_at')[:8]

    # System config snapshot
    confidence_threshold = SystemConfiguration.get('confidence_threshold_min', 0.70)

    context = {
        'page_title':         'Administrator Dashboard',
        'total_claims':       total_claims,
        'valid_claims':       valid_claims,
        'invalid_claims':     invalid_claims,
        'manual_claims':      manual_claims,
        'pending_claims':     pending_claims,
        'approved_claims':    approved_claims,
        'rejected_claims':    rejected_claims,
        'duplicate_alerts':   duplicate_alerts,
        'model_disagreements':model_disagreements,
        'total_users':        total_users,
        'customers':          customers,
        'employees':          employees,
        'reviewers':          reviewers,
        'claims_this_week':   json.dumps(claims_this_week),
        'recent_claims':      recent_claims,
        'confidence_threshold': confidence_threshold,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


# ─────────────────────────────────────────────────────────────────
# User Management
# ─────────────────────────────────────────────────────────────────

@admin_required
def user_management(request):
    """List, search, filter, activate/deactivate users. Change roles."""
    users = User.objects.all().order_by('-date_joined')

    search      = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone__icontains=search)
        )
    if role_filter:
        users = users.filter(role=role_filter)
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    context = {
        'page_title':   'User Management',
        'users':        users,
        'search':       search,
        'role_filter':  role_filter,
        'status_filter':status_filter,
        'role_choices': User.ROLE_CHOICES,
        'total':        users.count(),
    }
    return render(request, 'administrator/user_management.html', context)


@admin_required
def toggle_user_status(request, pk):
    """Activate or deactivate a user account."""
    user = get_object_or_404(User, pk=pk)
    if user.pk == request.user.pk:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('administrator:users')
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    action = 'activated' if user.is_active else 'deactivated'
    AuditLog.objects.create(
        user=request.user, action_type='user_managed',
        description=f'Admin {request.user.email} {action} user {user.email}',
        object_type='User', object_id=str(user.pk),
    )
    messages.success(request, f'User {user.email} has been {action}.')
    return redirect('administrator:users')


@admin_required
def change_user_role(request, pk):
    """Change a user's role."""
    user     = get_object_or_404(User, pk=pk)
    new_role = request.POST.get('role', '')
    valid    = [r[0] for r in User.ROLE_CHOICES]
    if new_role not in valid:
        messages.error(request, 'Invalid role selected.')
        return redirect('administrator:users')
    old_role = user.role
    user.role = new_role
    user.save(update_fields=['role'])
    AuditLog.objects.create(
        user=request.user, action_type='user_managed',
        description=f'Role changed for {user.email}: {old_role} → {new_role}',
        object_type='User', object_id=str(user.pk),
    )
    messages.success(request, f'Role updated for {user.get_full_name()}.')
    return redirect('administrator:users')


# ─────────────────────────────────────────────────────────────────
# All Claims (Admin View)
# ─────────────────────────────────────────────────────────────────

@admin_required
def all_claims(request):
    """Admin view of all claims in the system with full filters."""
    claims = Claim.objects.select_related(
        'product', 'claimant', 'submitted_by'
    ).order_by('-created_at')

    search         = request.GET.get('q', '')
    status_filter  = request.GET.get('status', '')
    decision_filter= request.GET.get('decision', '')
    dup_filter     = request.GET.get('duplicate', '')

    if search:
        claims = claims.filter(
            Q(claim_reference__icontains=search) |
            Q(claimant__email__icontains=search) |
            Q(product__serial_number__icontains=search)
        )
    if status_filter:
        claims = claims.filter(status=status_filter)
    if decision_filter:
        claims = claims.filter(final_decision=decision_filter)
    if dup_filter == '1':
        claims = claims.filter(is_duplicate=True)

    context = {
        'page_title':      'All Claims',
        'claims':          claims[:200],   # paginate in production
        'search':          search,
        'status_filter':   status_filter,
        'decision_filter': decision_filter,
        'dup_filter':      dup_filter,
        'status_choices':  Claim.STATUS_CHOICES,
        'decision_choices':Claim.FINAL_DECISION,
        'total':           claims.count(),
    }
    return render(request, 'administrator/all_claims.html', context)


# ─────────────────────────────────────────────────────────────────
# Analytics
# ─────────────────────────────────────────────────────────────────

@admin_required
def analytics(request):
    """Charts and stats: outcome distribution, model performance, trends."""
    all_claims = Claim.objects.all()

    # Decision distribution
    decision_dist = {
        'likely_valid':   all_claims.filter(final_decision='likely_valid').count(),
        'likely_invalid': all_claims.filter(final_decision='likely_invalid').count(),
        'manual_review':  all_claims.filter(final_decision='manual_review').count(),
        'pending':        all_claims.filter(final_decision='pending').count(),
    }

    # Status distribution
    status_dist = dict(all_claims.values('status').annotate(cnt=Count('pk')).values_list('status', 'cnt'))

    # Damage type distribution
    damage_dist = dict(
        all_claims.values('damage_type').annotate(cnt=Count('pk')).values_list('damage_type', 'cnt')
    )

    # Model consistency stats
    consistency_dist = dict(
        all_claims.exclude(model_consistency_status='').values(
            'model_consistency_status'
        ).annotate(cnt=Count('pk')).values_list('model_consistency_status', 'cnt')
    )

    # AI overrides
    total_overrides = Review.objects.filter(is_ai_override=True).count()

    # Average confidence — mean of python_confidence_valid across evaluated claims
    from django.db.models import Avg
    avg_conf_result = all_claims.exclude(python_confidence_valid=None).aggregate(
        avg=Avg('python_confidence_valid')
    )
    avg_confidence_raw = avg_conf_result.get('avg')
    avg_confidence = round(avg_confidence_raw * 100, 1) if avg_confidence_raw is not None else None

    # Claims trend (last 30 days)
    today = timezone.now().date()
    trend = []
    for i in range(30):
        day = today - timedelta(days=29 - i)
        cnt = all_claims.filter(created_at__date=day).count()
        trend.append({'date': str(day), 'count': cnt})

    context = {
        'page_title':       'Analytics & Reports',
        'decision_dist':    json.dumps(decision_dist),
        'status_dist':      json.dumps(status_dist),
        'damage_dist':      json.dumps(damage_dist),
        'consistency_dist': json.dumps(consistency_dist),
        'trend_data':       json.dumps(trend),
        'total_overrides':  total_overrides,
        'total_claims':     all_claims.count(),
        'avg_confidence':   avg_confidence,  # e.g. 84.3 (as %) or None if no predictions yet
    }
    return render(request, 'administrator/analytics.html', context)


# ─────────────────────────────────────────────────────────────────
# Model Versions
# ─────────────────────────────────────────────────────────────────

@admin_required
def model_versions(request):
    versions = ModelVersion.objects.all().order_by('-created_at')
    context  = {'page_title': 'Model Versions', 'versions': versions}
    return render(request, 'administrator/model_versions.html', context)


# ─────────────────────────────────────────────────────────────────
# AI Thresholds (SystemConfiguration)
# ─────────────────────────────────────────────────────────────────

@admin_required
def manage_thresholds(request):
    configs = SystemConfiguration.objects.all().order_by('key')

    if request.method == 'POST':
        for config in configs:
            new_val = request.POST.get(f'val_{config.pk}', '').strip()
            if new_val and new_val != config.value:
                config.value      = new_val
                config.updated_by = request.user
                config.save()
        AuditLog.objects.create(
            user=request.user, action_type='threshold_updated',
            description=f'Admin {request.user.email} updated system configuration.',
        )
        messages.success(request, 'Configuration updated successfully.')
        return redirect('administrator:thresholds')

    context = {'page_title': 'AI Thresholds & Configuration', 'configs': configs}
    return render(request, 'administrator/thresholds.html', context)


# ─────────────────────────────────────────────────────────────────
# Warranty Policies
# ─────────────────────────────────────────────────────────────────

@admin_required
def warranty_policies(request):
    policies = WarrantyPolicy.objects.select_related('product_category').order_by('product_category__name')
    context  = {'page_title': 'Warranty Policies', 'policies': policies}
    return render(request, 'administrator/warranty_policies.html', context)


# ─────────────────────────────────────────────────────────────────
# Audit Logs
# ─────────────────────────────────────────────────────────────────

@admin_required
def audit_logs(request):
    logs = AuditLog.objects.select_related('user').order_by('-created_at')

    search     = request.GET.get('q', '')
    action_filter = request.GET.get('action', '')

    if search:
        logs = logs.filter(
            Q(user__email__icontains=search) |
            Q(description__icontains=search)
        )
    if action_filter:
        logs = logs.filter(action_type=action_filter)

    action_choices = AuditLog.ACTION_TYPES

    context = {
        'page_title':     'Audit Logs',
        'logs':           logs[:300],
        'search':         search,
        'action_filter':  action_filter,
        'action_choices': action_choices,
    }
    return render(request, 'administrator/audit_logs.html', context)


# ─────────────────────────────────────────────────────────────────
# Reports Export
# ─────────────────────────────────────────────────────────────────

@admin_required
def export_reports(request):
    """
    SRS §1.6.xlv — Data Export.
    Export claims, products, warranties, or analytics records in CSV format.
    Supports ?export= query param: claims_csv | products_csv | warranties_csv | analytics_csv
    """
    export_type = request.GET.get('export', '')

    # ── Claims CSV ──────────────────────────────────────────────
    if export_type == 'claims_csv':
        claims = Claim.objects.select_related(
            'product', 'claimant', 'warranty', 'submitted_by'
        ).prefetch_related('rule_results').order_by('-created_at')

        # Optional filters
        status_filter   = request.GET.get('status', '')
        decision_filter = request.GET.get('decision', '')
        date_from       = request.GET.get('date_from', '')
        date_to         = request.GET.get('date_to', '')
        if status_filter:
            claims = claims.filter(status=status_filter)
        if decision_filter:
            claims = claims.filter(final_decision=decision_filter)
        if date_from:
            claims = claims.filter(created_at__date__gte=date_from)
        if date_to:
            claims = claims.filter(created_at__date__lte=date_to)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="assurex_claims_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow([
            'Claim Reference', 'Claim ID',
            'Customer Name', 'Customer Email',
            'Product', 'Brand', 'Model Number', 'Serial Number',
            'Damage Type', 'Fault Date', 'Days Since Fault',
            'Warranty Status', 'Warranty Expiry',
            'Status', 'Final Decision',
            'Python Prediction',
            'Python Conf. Valid (%)', 'Python Conf. Invalid (%)', 'Python Conf. Manual (%)',
            'TM Prediction',
            'TM Conf. Valid (%)', 'TM Conf. Invalid (%)', 'TM Conf. Manual (%)',
            'Confidence Difference (%)', 'Model Consistency',
            'Rules Passed', 'Rules Failed', 'Rules Warning',
            'Missing Documents', 'Is Duplicate',
            'Submission Date', 'Evaluated At', 'Created At',
        ])
        for c in claims:
            warranty_status = ''
            warranty_expiry = ''
            if c.warranty:
                warranty_status = c.warranty.get_status_display()
                warranty_expiry = str(c.warranty.expiry_date)
            writer.writerow([
                c.claim_reference, str(c.claim_id),
                c.claimant.get_full_name(), c.claimant.email,
                f'{c.product.brand} {c.product.product_name}',
                c.product.brand, c.product.model_number, c.product.serial_number,
                c.get_damage_type_display(), c.fault_date,
                c.days_since_fault,
                warranty_status, warranty_expiry,
                c.get_status_display(), c.get_final_decision_display(),
                c.python_prediction,
                round(c.python_confidence_valid or 0, 2),
                round(c.python_confidence_invalid or 0, 2),
                round(c.python_confidence_manual or 0, 2),
                c.tm_prediction,
                round(c.tm_confidence_valid or 0, 2),
                round(c.tm_confidence_invalid or 0, 2),
                round(c.tm_confidence_manual or 0, 2),
                round(c.confidence_difference or 0, 2),
                c.model_consistency_status,
                c.rules_passed, c.rules_failed, c.rules_warning,
                ','.join(c.missing_document_types) if c.missing_document_types else '',
                'Yes' if c.is_duplicate else 'No',
                c.submission_date, c.evaluated_at, c.created_at,
            ])
        AuditLog.objects.create(
            user=request.user, action_type='report_exported',
            description=f'Admin {request.user.email} exported claims CSV ({claims.count()} records).',
        )
        return response

    # ── Products CSV ─────────────────────────────────────────────
    if export_type == 'products_csv':
        products = Product.objects.select_related(
            'owner', 'category'
        ).order_by('-created_at')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="assurex_products_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow([
            'Product ID', 'Product Name', 'Brand', 'Category',
            'Model Number', 'Serial Number',
            'Purchase Date', 'Purchase Price', 'Retailer',
            'Warranty Duration (months)', 'Product Age (months)',
            'Owner Name', 'Owner Email',
            'Created At',
        ])
        for p in products:
            writer.writerow([
                str(p.product_id), p.product_name, p.brand,
                p.category.name if p.category else '',
                p.model_number, p.serial_number,
                p.purchase_date, p.purchase_price, p.retailer,
                p.warranty_duration_months,
                p.product_age_months,
                p.owner.get_full_name(), p.owner.email,
                p.created_at,
            ])
        AuditLog.objects.create(
            user=request.user, action_type='report_exported',
            description=f'Admin exported products CSV ({products.count()} records).',
        )
        return response

    # ── Warranties CSV ────────────────────────────────────────────
    if export_type == 'warranties_csv':
        warranties = Warranty.objects.select_related(
            'product', 'product__owner'
        ).order_by('expiry_date')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="assurex_warranties_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow([
            'Warranty ID', 'Product', 'Serial Number',
            'Warranty Type', 'Provider', 'Service Center',
            'Start Date', 'Expiry Date', 'Remaining Days',
            'Status', 'Owner Name', 'Owner Email',
        ])
        for w in warranties:
            w.update_status()
            writer.writerow([
                str(w.warranty_id),
                f'{w.product.brand} {w.product.product_name}',
                w.product.serial_number,
                w.get_warranty_type_display(), w.warranty_provider, w.service_center,
                w.start_date, w.expiry_date, w.remaining_days,
                w.get_status_display(),
                w.product.owner.get_full_name(), w.product.owner.email,
            ])
        AuditLog.objects.create(
            user=request.user, action_type='report_exported',
            description=f'Admin exported warranties CSV ({warranties.count()} records).',
        )
        return response

    # ── Analytics CSV ─────────────────────────────────────────────
    if export_type == 'analytics_csv':
        all_claims = Claim.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="assurex_analytics_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Claims', all_claims.count()])
        writer.writerow(['Likely Valid', all_claims.filter(final_decision='likely_valid').count()])
        writer.writerow(['Likely Invalid', all_claims.filter(final_decision='likely_invalid').count()])
        writer.writerow(['Manual Review', all_claims.filter(final_decision='manual_review').count()])
        writer.writerow(['Pending', all_claims.filter(final_decision='pending').count()])
        writer.writerow(['Approved', all_claims.filter(status='approved').count()])
        writer.writerow(['Rejected', all_claims.filter(status='rejected').count()])
        writer.writerow(['Duplicate Flags', all_claims.filter(is_duplicate=True).count()])
        writer.writerow(['Model Disagreements',
                         all_claims.filter(model_consistency_status='model_disagreement').count()])
        writer.writerow(['Total Users', User.objects.filter(is_active=True).count()])
        writer.writerow(['Customers', User.objects.filter(role=User.CUSTOMER).count()])
        writer.writerow(['Employees', User.objects.filter(role=User.EMPLOYEE).count()])
        writer.writerow(['Reviewers', User.objects.filter(role=User.REVIEWER).count()])
        writer.writerow(['Total Products', Product.objects.count()])
        writer.writerow(['Active Warranties', Warranty.objects.filter(status='active').count()])
        writer.writerow(['Expiring Warranties', Warranty.objects.filter(status='expiring').count()])
        writer.writerow(['Expired Warranties', Warranty.objects.filter(status='expired').count()])
        AuditLog.objects.create(
            user=request.user, action_type='report_exported',
            description='Admin exported analytics summary CSV.',
        )
        return response

    # ── Reports Page (GET — no export param) ──────────────────────
    context = {
        'page_title':     'Export Reports',
        'total_claims':   Claim.objects.count(),
        'total_products': Product.objects.count(),
        'total_warranties': Warranty.objects.count(),
        'status_choices': Claim.STATUS_CHOICES,
        'decision_choices': Claim.FINAL_DECISION,
    }
    return render(request, 'administrator/reports.html', context)


# ─────────────────────────────────────────────────────────────────
# Monitoring
# ─────────────────────────────────────────────────────────────────

@admin_required
def monitoring(request):
    """System health: failed uploads, duplicate alerts, model disagreements, anomalies."""
    today    = timezone.now().date()
    week_ago = today - timedelta(days=7)

    duplicate_claims    = Claim.objects.filter(is_duplicate=True).count()
    model_disagreements = Claim.objects.filter(
        model_consistency_status__in=['model_disagreement', 'uncertain_result']
    ).count()
    low_confidence      = Claim.objects.filter(
        python_confidence_valid__lt=0.7,
        python_confidence_invalid__lt=0.7,
        python_confidence_manual__lt=0.7,
    ).exclude(python_prediction='').count()

    recent_anomalies = AuditLog.objects.filter(
        action_type='anomaly_detected'
    ).order_by('-created_at')[:10]

    recent_errors = AuditLog.objects.filter(
        action_type__in=['model_predicted'],
        extra_data__error__isnull=False
    ).order_by('-created_at')[:10]

    context = {
        'page_title':         'System Monitoring',
        'duplicate_claims':   duplicate_claims,
        'model_disagreements':model_disagreements,
        'low_confidence':     low_confidence,
        'recent_anomalies':   recent_anomalies,
        'recent_errors':      recent_errors,
    }
    return render(request, 'administrator/monitoring.html', context)
