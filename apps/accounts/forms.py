"""
AssureX — Authentication & Profile Forms
"""
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm,
    PasswordResetForm, SetPasswordForm,
)
from django.core.validators import RegexValidator
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'you@example.com',
            'autofocus':   True,
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'Enter your password',
        })
    )
    remember_me = forms.BooleanField(required=False, label='Keep me signed in')

    error_messages = {
        'invalid_login': 'Incorrect email or password. Please try again.',
        'inactive':      'This account has been deactivated.',
    }


class RegisterForm(forms.ModelForm):
    # ── Role selection (Customer + Employee only; Reviewer/Admin set by admin) ──
    REGISTER_ROLE_CHOICES = [
        (User.CUSTOMER,  'Customer — Register & manage product warranty claims'),
        (User.EMPLOYEE,  'Service Center Employee — Process & submit claims on behalf of customers'),
    ]

    role = forms.ChoiceField(
        choices=REGISTER_ROLE_CHOICES,
        label='I am registering as',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id':    'id_role',
        }),
        help_text='Select the role that best describes your purpose on AssureX.'
    )

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Create a strong password'
        }),
        min_length=8,
        help_text='Minimum 8 characters.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Re-enter password'
        })
    )
    agree_terms = forms.BooleanField(
        required=True,
        label='I agree to the Terms of Service and Privacy Policy'
    )

    phone_validator = RegexValidator(
        regex=r'^\+?[\d\s\-]{7,20}$',
        message='Enter a valid phone number.'
    )

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'country']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+92 300 0000000'}),
            'city':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'country':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_role(self):
        """Only customer and employee can self-register."""
        role = self.cleaned_data.get('role')
        allowed = [User.CUSTOMER, User.EMPLOYEE]
        if role not in allowed:
            raise forms.ValidationError('Invalid role selection.')
        return role

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        # Use the role selected in the form
        user.role = self.cleaned_data.get('role', User.CUSTOMER)
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'phone', 'address', 'city', 'country', 'profile_pic']
        widgets = {
            'first_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'phone':       forms.TextInput(attrs={'class': 'form-control'}),
            'address':     forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city':        forms.TextInput(attrs={'class': 'form-control'}),
            'country':     forms.TextInput(attrs={'class': 'form-control'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class CustomPasswordResetForm(PasswordResetForm):
    """Password reset form — only allow existing active users."""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'Enter your registered email',
            'autofocus':   True,
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Set new password form after clicking reset link."""
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'Enter new password',
        }),
        min_length=8,
        help_text='Minimum 8 characters.',
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'Re-enter new password',
        })
    )
