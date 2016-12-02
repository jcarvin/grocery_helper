from django import forms
from django.forms import ModelForm
from django.utils import timezone
from django.forms import extras
from django.contrib.auth.models import User
from friendship.models import Friend

from .models import Receipt, ReceiptProduct, Product, Store, ShareItem


class AddSplitItemForm(ModelForm):

    def __init__(self, user, *args, **kwargs):
        pk_list = [friend.id for friend in Friend.objects.friends(user)]
        pk_list.append(user.id)
        super(AddSplitItemForm, self).__init__(*args, **kwargs)
        self.fields['purchaser'] = forms.ModelChoiceField(queryset=User.objects.filter(pk__in=pk_list))
        self.fields['purchaser'].label = 'Who Purchased This Item?'
        self.fields['product'] = forms.ModelChoiceField(queryset=Product.objects.filter(owner=user))

    class Meta:
        model = ReceiptProduct
        fields = [
            'product',
            'purchaser',
            'price',
            'description',
            'split',
            'sale',
            'tax',
        ]
        labels = {
            'sale': 'On Sale',
            'tax': 'Is This Item Taxed?',
        }


class AddItemForm(ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(AddItemForm, self).__init__(*args, **kwargs)
        self.fields['product'] = forms.ModelChoiceField(queryset=Product.objects.filter(owner=user))

    class Meta:
        model = ReceiptProduct
        fields = [
            'product',
            'price',
            'description',
            'sale',
            'tax',
        ]
        labels = {
            'sale': 'On Sale',
            'tax': 'Is This Item Taxed?',
        }


class ShareItemForm(ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(ShareItemForm, self).__init__(*args, **kwargs)
        # user = kwargs.pop('user')
        pk_list = [friend.id for friend in Friend.objects.friends(user)]
        pk_list.append(user.id)
        self.fields['purchasers'] = forms.ModelChoiceField(queryset=User.objects.filter(pk__in=pk_list))

    class Meta:
        model = ShareItem
        fields = ['purchasers']


class AddReceiptForm(ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(AddReceiptForm, self).__init__(*args, **kwargs)
        self.fields['store'] = forms.ModelChoiceField(queryset=Store.objects.filter(owner=user))

    date = forms.DateField(widget=extras.SelectDateWidget, initial=timezone.now())

    class Meta:
        model = Receipt
        fields = [
            'store',
            'date',
            'split',
            'tax',
            'pic',
        ]


class AddStoreForm(ModelForm):
    class Meta:
        model = Store
        fields = [
            'name',
        ]


class AddProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            'type',
        ]