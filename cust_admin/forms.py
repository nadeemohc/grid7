from django import forms
from store.models import *
from decimal import Decimal



class ProductVariantForm(forms.ModelForm):
      # Add this line for the new image field
    class Meta:
        model = ProductVariant
        fields = ['product', 'size' ,'price','old_price', 'stock_count','image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    
    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is not None and price < Decimal('0'):
            raise forms.ValidationError("Price cannot be negative.")

        return price
