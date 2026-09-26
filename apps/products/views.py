"""
AssureX — Products Views
Handles: list, register, detail, edit for customer-owned products.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Product
from .forms import ProductRegistrationForm, ProductEditForm
from apps.warranties.models import Warranty
from apps.claims.models import Claim
from apps.accounts.models import AuditLog


def _log(request, action, desc, obj_type='', obj_id=''):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    AuditLog.objects.create(
        user=request.user, action_type=action, description=desc,
        ip_address=ip or None, object_type=obj_type, object_id=str(obj_id),
    )


@login_required
def product_list(request):
    """Show all products owned by the logged-in customer."""
    products = Product.objects.filter(
        owner=request.user, is_active=True
    ).select_related('category').prefetch_related('warranties', 'claims')

    # Annotate each product with active warranty
    for p in products:
        p.active_warranty = p.warranties.filter(
            status__in=['active', 'expiring']
        ).order_by('-expiry_date').first()
        p.open_claims = p.claims.filter(
            status__in=['draft', 'submitted', 'evaluation', 'manual', 'additional']
        ).count()

    context = {
        'products':   products,
        'page_title': 'My Products',
    }
    return render(request, 'products/product_list.html', context)


@login_required
def product_register(request):
    """Register a new product."""
    form = ProductRegistrationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.save()
        # Auto-create a warranty record from the duration specified
        Warranty.objects.create(
            product=product,
            warranty_type='standard',
            warranty_provider='Manufacturer',
            start_date=product.purchase_date,
            expiry_date=(
                product.purchase_date + __import__('datetime').timedelta(
                    days=30 * product.warranty_duration_months
                )
            ) if product.warranty_duration_months else product.purchase_date,
            status='active',
        )
        _log(request, 'product_registered',
             f'Product registered: {product.brand} {product.product_name} SN:{product.serial_number}',
             'Product', product.pk)
        messages.success(request, f'Product "{product.product_name}" registered successfully!')
        return redirect('products:list')

    return render(request, 'products/product_register.html', {
        'form': form, 'page_title': 'Register Product',
    })


@login_required
def product_detail(request, pk):
    """Product detail — warranties, claims, documents."""
    product = get_object_or_404(Product, pk=pk, owner=request.user, is_active=True)
    warranties = product.warranties.all().order_by('-start_date')
    claims = product.claims.all().order_by('-created_at')

    context = {
        'product':    product,
        'warranties': warranties,
        'claims':     claims,
        'page_title': f'{product.brand} {product.product_name}',
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user, is_active=True)
    form = ProductEditForm(request.POST or None, instance=product)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product updated.')
        return redirect('products:detail', pk=pk)

    return render(request, 'products/product_register.html', {
        'form': form, 'page_title': 'Edit Product', 'is_edit': True,
    })


@login_required
def product_deactivate(request, pk):
    """Soft-delete a product by marking it inactive. POST only."""
    product = get_object_or_404(Product, pk=pk, owner=request.user, is_active=True)

    if request.method == 'POST':
        # Prevent deactivation if there are open claims
        open_claims = product.claims.filter(
            status__in=['draft', 'submitted', 'evaluation', 'manual', 'additional']
        ).count()
        if open_claims:
            messages.error(
                request,
                f'Cannot deactivate this product — it has {open_claims} open '
                f'claim{"s" if open_claims > 1 else ""}. Close or withdraw all claims first.'
            )
            return redirect('products:detail', pk=pk)

        product.is_active = False
        product.save(update_fields=['is_active'])
        _log(request, 'product_registered',
             f'Product deactivated: {product.brand} {product.product_name} SN:{product.serial_number}',
             'Product', product.pk)
        messages.success(request, f'"{product.product_name}" has been removed from your products.')
        return redirect('products:list')

    # GET → redirect back (deactivate is POST-only for safety)
    return redirect('products:detail', pk=pk)
