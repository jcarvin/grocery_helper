from django import forms
from django.forms import ModelForm
from django.utils import timezone
from django.forms import extras


from .models import Receipt, ReceiptProduct, Product, Store


class AddItemForm(ModelForm):
    class Meta:
        model = ReceiptProduct
        fields = ['product', 'price', 'description', 'sale', 'tax']
        labels = {'sale': 'On Sale', 'tax': 'Is This Item Taxed?'}


class AddReceiptForm(ModelForm):
    date = forms.DateField(widget=extras.SelectDateWidget, initial=timezone.now())

    class Meta:
        model = Receipt
        fields = ['store', 'date', 'tax']



class AddStoreForm(ModelForm):
    class Meta:
        model = Store
        fields = ['name']


class AddProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['type']