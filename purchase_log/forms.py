from django import forms
from django.forms import ModelForm

from .models import Receipt, ReceiptProduct, Product, Store


class AddItemForm(ModelForm):
    class Meta:
        model = ReceiptProduct
        fields = ['product', 'price', 'description', 'sale']
        labels = {'sale': 'On Sale'}


class AddReceiptForm(ModelForm):
    class Meta:
        model = Receipt
        fields = ['store', 'date']


class AddStoreForm(ModelForm):
    class Meta:
        model = Store
        fields = ['name']


class AddProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['type']