from django import forms
from store.models import Product, Size

class ProductVariantAssignForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label="Select Product", widget=forms.Select(attrs={'class': 'form-select', 'required': True}))
    size = forms.ModelChoiceField(queryset=Size.objects.all(), empty_label="Select Size", widget=forms.Select(attrs={'class': 'form-select', 'required': True}))
    price = forms.DecimalField(decimal_places=2, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Price', 'required': True}))
    old_price = forms.DecimalField(decimal_places=2, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Old Price', 'required': True}))
    stock = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Stock', 'required': True}))
    featured = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    popular = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    latest = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    in_stock = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    status = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
