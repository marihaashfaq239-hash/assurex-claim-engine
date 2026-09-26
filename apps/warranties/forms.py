"""
AssureX — Warranty Forms
"""
from django import forms
from .models import Warranty
from apps.products.models import Product


class WarrantyAddForm(forms.ModelForm):
    """
    Allows a customer to manually add an extended / third-party warranty
    to one of their registered products.
    """
    class Meta:
        model  = Warranty
        fields = [
            'product', 'warranty_type', 'warranty_provider',
            'service_center', 'start_date', 'expiry_date',
            'coverage_description', 'exclusions', 'warranty_card',
        ]
        widgets = {
            'product':              forms.Select(attrs={'class': 'form-select'}),
            'warranty_type':        forms.Select(attrs={'class': 'form-select'}),
            'warranty_provider':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Samsung Care, SquareTrade'}),
            'service_center':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Authorized service center name (optional)'}),
            'start_date':           forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date':          forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'coverage_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What is covered under this warranty?'}),
            'exclusions':           forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'What is NOT covered?'}),
            'warranty_card':        forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'warranty_card': 'Warranty Card / Certificate (PDF or Image, optional)',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['product'].queryset = Product.objects.filter(
                owner=user, is_active=True
            ).order_by('brand', 'product_name')
        self.fields['service_center'].required = False
        self.fields['coverage_description'].required = False
        self.fields['exclusions'].required = False
        self.fields['warranty_card'].required = False

    def clean(self):
        cleaned = super().clean()
        start  = cleaned.get('start_date')
        expiry = cleaned.get('expiry_date')
        if start and expiry and expiry <= start:
            self.add_error('expiry_date', 'Expiry date must be after the start date.')
        return cleaned
