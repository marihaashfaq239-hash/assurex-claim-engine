"""
AssureX — Service Center Employee Views
Handles: employee dashboard, customer search, claim list, claim creation on behalf of customer.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse

from .models import Claim, ClaimDocument, RepairHistory
from apps.accounts.models import User, AuditLog
from apps.products.models import Product
from apps.warranties.models import Warranty
from apps.accounts.decorators import employee_required, employee_or_admin


def _log(request, action, desc, obj_type='', obj_id=''):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    AuditLog.objects.create(
        user=request.user, action_type=action, description=desc,
        ip_address=ip or None, object_type=obj_type, object_id=str(obj_id),
    )


# ─────────────────────────────────────────────────────────────────
# Employee Dashboard
# ─────────────────────────────────────────────────────────────────

@employee_required
def employee_dashboard(request):
    """Employee home — today's activity, recent claims created by this employee."""
    today = timezone.now().date()

    # Claims created BY this employee
    my_claims = Claim.objects.filter(submitted_by=request.user).order_by('-created_at')

    total_created  = my_claims.count()
    submitted_today = my_claims.filter(created_at__date=today).count()
    pending        = my_claims.filter(
        status__in=['submitted', 'evaluation', 'manual', 'additional']
    ).count()
    approved       = my_claims.filter(status='approved').count()

    recent_claims  = my_claims.select_related('product', 'claimant')[:8]

    context = {
        'page_title':      'Employee Dashboard',
        'total_created':   total_created,
        'submitted_today': submitted_today,
        'pending_claims':  pending,
        'approved_claims': approved,
        'recent_claims':   recent_claims,
    }
    return render(request, 'dashboard/employee_dashboard.html', context)


# ─────────────────────────────────────────────────────────────────
# Customer Search
# ─────────────────────────────────────────────────────────────────

@employee_required
def customer_search(request):
    """
    Employee searches for a customer by name/email/phone.
    Results show customer's products and their warranty status.
    """
    query    = request.GET.get('q', '').strip()
    customers = []

    if query:
        customers = User.objects.filter(
            role=User.CUSTOMER, is_active=True
        ).filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query)
        ).prefetch_related('products')[:20]

    context = {
        'page_title': 'Search Customer',
        'query':      query,
        'customers':  customers,
    }
    return render(request, 'employee/customer_search.html', context)


@employee_required
def customer_detail_employee(request, customer_pk):
    """
    Employee views a specific customer's products, warranties, and claims.
    Used before creating a claim on their behalf.
    """
    customer  = get_object_or_404(User, pk=customer_pk, role=User.CUSTOMER, is_active=True)
    products  = Product.objects.filter(owner=customer, is_active=True).select_related('category')
    claims    = Claim.objects.filter(claimant=customer).order_by('-created_at')[:10]
    warranties = Warranty.objects.filter(product__owner=customer)
    for w in warranties:
        w.update_status()

    context = {
        'page_title':    f'{customer.get_full_name()} — Customer Details',
        'customer':      customer,
        'products':      products,
        'claims':        claims,
        'warranties':    warranties,
    }
    return render(request, 'employee/customer_detail.html', context)


# ─────────────────────────────────────────────────────────────────
# Employee Claim List
# ─────────────────────────────────────────────────────────────────

@employee_required
def employee_claim_list(request):
    """All claims created by this employee."""
    claims = Claim.objects.filter(
        submitted_by=request.user
    ).select_related('product', 'claimant').order_by('-created_at')

    status_filter = request.GET.get('status', '')
    search        = request.GET.get('q', '')

    if status_filter:
        claims = claims.filter(status=status_filter)
    if search:
        claims = claims.filter(
            Q(claim_reference__icontains=search) |
            Q(claimant__email__icontains=search) |
            Q(claimant__first_name__icontains=search) |
            Q(product__serial_number__icontains=search)
        )

    context = {
        'page_title':     'Claims — Created by Me',
        'claims':         claims,
        'status_filter':  status_filter,
        'search':         search,
        'status_choices': Claim.STATUS_CHOICES,
    }
    return render(request, 'employee/employee_claim_list.html', context)


# ─────────────────────────────────────────────────────────────────
# Employee Create Claim (on behalf of customer)
# ─────────────────────────────────────────────────────────────────

@employee_required
def employee_create_claim(request):
    """
    Multi-step: Employee selects customer → product → fills claim details.
    The claim is created with submitted_by = employee, claimant = customer.
    """
    from apps.claims.forms import EmployeeClaimForm

    step         = request.GET.get('step', '1')
    customer_pk  = request.GET.get('customer', '')
    product_pk   = request.GET.get('product', '')

    customer = None
    product  = None
    products = []

    if customer_pk:
        customer = get_object_or_404(User, pk=customer_pk, role=User.CUSTOMER)
        products = Product.objects.filter(owner=customer, is_active=True).select_related('category')

    if product_pk:
        product = get_object_or_404(Product, pk=product_pk, owner=customer) if customer else None

    if request.method == 'POST':
        form = EmployeeClaimForm(request.POST, customer=customer, product=product)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.claimant     = customer
            claim.submitted_by = request.user
            claim.status       = 'submitted'
            claim.submission_date = timezone.now()
            claim.save()

            _log(request, 'claim_submitted',
                 f'Employee {request.user.email} created claim for {customer.email}. '
                 f'Product: {product.serial_number if product else "?"}',
                 'Claim', claim.pk)

            messages.success(
                request,
                f'Claim {claim.claim_reference} created successfully for {customer.get_full_name()}.'
            )
            return redirect('claims:employee_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeClaimForm(customer=customer, product=product)

    context = {
        'page_title': 'Create Claim for Customer',
        'form':       form,
        'step':       step,
        'customer':   customer,
        'product':    product,
        'products':   products,
    }
    return render(request, 'employee/employee_create_claim.html', context)


@employee_required
def customer_products_ajax(request):
    """AJAX: returns products for a selected customer (used in claim form)."""
    customer_pk = request.GET.get('customer_id')
    if not customer_pk:
        return JsonResponse({'products': []})
    products = Product.objects.filter(
        owner_id=customer_pk, is_active=True
    ).values('pk', 'product_name', 'brand', 'serial_number', 'model_number')
    return JsonResponse({'products': list(products)})
