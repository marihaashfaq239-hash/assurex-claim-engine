"""
AssureX — Product Registration Forms
"""
from django import forms
from .models import Product, ProductCategory


class ProductRegistrationForm(forms.ModelForm):
    class Meta:
        model  = Product
        fields = [
            'product_name', 'brand', 'category', 'model_number',
            'serial_number', 'purchase_date', 'purchase_price',
            'retailer', 'purchase_city', 'warranty_duration_months', 'notes',
        ]
        widgets = {
            'product_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Split Air Conditioner'}),
            'brand':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Samsung, LG, Haier'}),
            'category':      forms.Select(attrs={'class': 'form-select'}),
            'model_number':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AR18TV3QAWK'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Found on product label'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_price':forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'retailer':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hafeez Centre'}),
            'purchase_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lahore'}),
            'warranty_duration_months': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 120}),
            'notes':         forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ProductCategory.objects.filter(is_active=True)
        self.fields['notes'].required = False

    def clean_serial_number(self):
        sn = self.cleaned_data.get('serial_number', '').strip()
        if not sn:
            raise forms.ValidationError('Serial number is required.')
        return sn


class ProductEditForm(ProductRegistrationForm):
    """Same fields, used for editing — serial number shown read-only."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['serial_number'].widget.attrs['readonly'] = True
