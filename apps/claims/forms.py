"""
AssureX — Claim Forms
"""
from django import forms
from django.utils import timezone
from .models import Claim, ClaimDocument, RepairHistory
from apps.products.models import Product
from apps.warranties.models import Warranty


class ClaimSubmitForm(forms.ModelForm):
    """
    Step 1 of claim submission — basic claim info.
    Used by both customers and (via EmployeeClaimForm) employees.
    """
    class Meta:
        model  = Claim
        fields = [
            'product', 'warranty', 'fault_date', 'damage_type',
            'fault_description', 'fault_location', 'additional_notes',
        ]
        widgets = {
            'product':           forms.Select(attrs={'class': 'form-select'}),
            'warranty':          forms.Select(attrs={'class': 'form-select'}),
            'fault_date':        forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'damage_type':       forms.Select(attrs={'class': 'form-select'}),
            'fault_description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Describe the fault in detail — what happened, when it started, symptoms...'
            }),
            'fault_location':    forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. compressor, display, battery'
            }),
            'additional_notes':  forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Any additional context or observations'
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['additional_notes'].required = False
        self.fields['fault_location'].required   = False
        self.fields['warranty'].required         = False

        if user:
            self.fields['product'].queryset = Product.objects.filter(
                owner=user, is_active=True
            ).select_related('category')
            self.fields['warranty'].queryset = Warranty.objects.filter(
                product__owner=user
            )
        else:
            self.fields['product'].queryset  = Product.objects.none()
            self.fields['warranty'].queryset = Warranty.objects.none()

    def clean_fault_date(self):
        fd = self.cleaned_data.get('fault_date')
        if fd and fd > timezone.now().date():
            raise forms.ValidationError('Fault date cannot be in the future.')
        return fd

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get('product')
        warranty = cleaned.get('warranty')
        # If warranty is selected, make sure it belongs to the chosen product
        if product and warranty and warranty.product != product:
            self.add_error('warranty', 'Selected warranty does not belong to this product.')
        return cleaned


class RepairHistoryForm(forms.ModelForm):
    """Inline form for adding repair history entries during claim submission."""
    class Meta:
        model  = RepairHistory
        fields = ['repair_date', 'repair_center', 'is_authorized',
                  'replaced_parts', 'repair_description', 'repair_cost', 'outcome']
        widgets = {
            'repair_date':        forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'repair_center':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service center name'}),
            'is_authorized':      forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'replaced_parts':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Compressor, PCB Board'}),
            'repair_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'repair_cost':        forms.NumberInput(attrs={'class': 'form-control'}),
            'outcome':            forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['replaced_parts'].required = False
        self.fields['repair_cost'].required    = False


class DocumentUploadForm(forms.ModelForm):
    """Single document upload — used multiple times in the claim wizard."""
    class Meta:
        model  = ClaimDocument
        fields = ['doc_type', 'file', 'description']
        widgets = {
            'doc_type':    forms.Select(attrs={'class': 'form-select'}),
            'file':        forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional note'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if f:
            max_size = 5 * 1024 * 1024  # 5 MB
            if f.size > max_size:
                raise forms.ValidationError('File size must be under 5 MB.')
            allowed = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
            if hasattr(f, 'content_type') and f.content_type not in allowed:
                raise forms.ValidationError('Only PDF, JPG, and PNG files are allowed.')
        return f


class EmployeeClaimForm(ClaimSubmitForm):
    """
    Extended claim form used by employees — product/warranty querysets
    are scoped to the selected customer, not the logged-in employee.
    """
    def __init__(self, *args, customer=None, product=None, **kwargs):
        # Pass customer as 'user' so parent scopes querysets correctly
        super().__init__(*args, user=customer, **kwargs)
        if product:
            self.fields['product'].initial  = product
            self.fields['warranty'].queryset = Warranty.objects.filter(product=product)
        if customer is None:
            # No customer selected yet — hide product/warranty
            self.fields['product'].queryset  = Product.objects.none()
            self.fields['warranty'].queryset = Warranty.objects.none()
