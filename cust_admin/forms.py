from django import forms
from store.models import *
from django.core.exceptions import ValidationError
from django.utils import timezone

class ProductVariantAssignForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label="Select Product", widget=forms.Select(attrs={'class': 'form-select', 'required': True}))
    size = forms.ModelChoiceField(queryset=Size.objects.all(), empty_label="Select Size", widget=forms.Select(attrs={'class': 'form-select', 'required': True}))
    price = forms.DecimalField(decimal_places=2, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Price', 'required': True}))
    old_price = forms.DecimalField(decimal_places=2, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Old Price', 'required': True}))
    stock = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Stock', 'required': True}))
    in_stock = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    status = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'active', 'active_date', 'expiry_date']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Coupon Code', 'required': True}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Discount Percentage', 'required': True}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'active_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date', 'required': True}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date', 'required': True}),
        }

    def clean_active_date(self):
        active_date = self.cleaned_data.get('active_date')
        if active_date and active_date < timezone.now().date():
            raise ValidationError("Active date cannot be in the past.")
        return active_date

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date and expiry_date < timezone.now().date():
            raise ValidationError("Expiry date cannot be in the past.")
        return expiry_date

    def clean(self):
        cleaned_data = super().clean()
        active_date = cleaned_data.get('active_date')
        expiry_date = cleaned_data.get('expiry_date')

        if active_date and expiry_date and active_date > expiry_date:
            raise ValidationError("Expiry date must be after the active date.")
        return cleaned_data