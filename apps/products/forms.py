from django import forms
from .models import Product, Category, Warehouse, Location


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Raw Materials'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
        }


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'short_code', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Main Warehouse'
            }),
            'short_code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. WH'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Warehouse address'
            }),
        }


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'short_code', 'warehouse']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Rack A'
            }),
            'short_code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. RACK-A'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-input',
            }),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'unit_of_measure',
            'cost_price', 'initial_stock', 'reorder_level',
            'warehouse', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Steel Rods'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. SKU-0001'
            }),
            'category': forms.Select(attrs={
                'class': 'form-input'
            }),
            'unit_of_measure': forms.Select(attrs={
                'class': 'form-input'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'initial_stock': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0'
            }),
            'reorder_level': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['is_active'].initial = True

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        # On edit, exclude current instance
        qs = Product.objects.filter(sku=sku)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                'A product with this SKU already exists.'
            )
        return sku.upper()