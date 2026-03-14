from django import forms
from django.forms import inlineformset_factory
from .models import Receipt, ReceiptItem, Delivery, DeliveryItem, Adjustment
from apps.products.models import Product, Warehouse, Location


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = [
            'supplier', 'receive_from', 'warehouse',
            'schedule_date', 'notes'
        ]
        widgets = {
            'supplier': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Supplier name'
            }),
            'receive_from': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Receiving from'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-input'
            }),
            'schedule_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Optional notes'
            }),
        }


class ReceiptItemForm(forms.ModelForm):
    class Meta:
        model = ReceiptItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-input'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'placeholder': '0'
            }),
        }


# Inline formset — links ReceiptItems to a Receipt
ReceiptItemFormSet = inlineformset_factory(
    Receipt,
    ReceiptItem,
    form=ReceiptItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = [
            'delivery_address', 'warehouse', 'schedule_date',
            'operation_type', 'notes'
        ]
        widgets = {
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Delivery address'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-input'
            }),
            'schedule_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'operation_type': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Outgoing Shipment'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Optional notes'
            }),
        }


class DeliveryItemForm(forms.ModelForm):
    class Meta:
        model = DeliveryItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-input'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'placeholder': '0'
            }),
        }


DeliveryItemFormSet = inlineformset_factory(
    Delivery,
    DeliveryItem,
    form=DeliveryItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class AdjustmentForm(forms.ModelForm):
    class Meta:
        model = Adjustment
        fields = [
            'product', 'location', 'counted_qty',
            'reason', 'notes'
        ]
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-input'
            }),
            'location': forms.Select(attrs={
                'class': 'form-input'
            }),
            'counted_qty': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Physical count'
            }),
            'reason': forms.Select(attrs={
                'class': 'form-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Optional notes'
            }),
        }