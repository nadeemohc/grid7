from django import forms
from store.models import *
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

class ProductVariantAssignForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        empty_label="Select Product",
        widget=forms.Select(attrs={'class': 'form-select', 'required': True})
    )
    size = forms.ModelChoiceField(
        queryset=Size.objects.all(),
        empty_label="Select Size",
        widget=forms.Select(attrs={'class': 'form-select', 'required': True})
    )
    price = forms.DecimalField(
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Price', 'required': True})
    )
    old_price = forms.DecimalField(
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Old Price', 'required': True})
    )
    stock = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Stock', 'required': True})
    )
    in_stock = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    status = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        initial_data = kwargs.pop('initial_data', None)
        super().__init__(*args, **kwargs)
        if initial_data:
            for field, value in initial_data.items():
                if field in self.fields:
                    self.fields[field].initial = value
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

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount is not None and (discount < 1 or discount > 99):
            raise ValidationError("Discount must be between 1 and 99 percent.")
        return discount

    def clean(self):
        cleaned_data = super().clean()
        active_date = cleaned_data.get('active_date')
        expiry_date = cleaned_data.get('expiry_date')

        if active_date and expiry_date and active_date > expiry_date:
            raise ValidationError("Expiry date must be after the active date.")
        return cleaned_data


class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['category', 'discount_percentage', 'start_date', 'end_date']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Category', 'required': True}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Discount Percentage', 'required': True}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date', 'required': True}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date', 'required': True}),
        }

    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage is not None and (discount_percentage <= 0 or discount_percentage >= 100):
            raise ValidationError("Discount percentage must be between 1 and 99.")
        return discount_percentage

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < date.today():
            raise ValidationError("Start date cannot be in the past.")
        return start_date

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date should be after start date.")

            # Check for duplicate offers
            if CategoryOffer.objects.filter(category=category, start_date=start_date, end_date=end_date).exists():
                raise ValidationError("An offer for this category with the same dates already exists.")

        return cleaned_data



class ProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = ['product', 'discount_percentage', 'start_date', 'end_date']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Product', 'required': True}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Discount Percentage', 'required': True}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date', 'required': True}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date', 'required': True}),
        }

    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage is not None and (discount_percentage <= 0 or discount_percentage >= 100):
            raise ValidationError("Discount percentage must be between 1 and 99.")
        return discount_percentage

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < date.today():
            raise ValidationError("Start date cannot be in the past.")
        return start_date

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date should be after start date.")

            # Check for duplicate offers
            if ProductOffer.objects.filter(product=product, start_date=start_date, end_date=end_date).exists():
                raise forms.ValidationError("An offer for this product with the same dates already exists.")

        return cleaned_data
