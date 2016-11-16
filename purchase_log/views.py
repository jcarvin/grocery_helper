from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views import generic
from .forms import AddItemForm, AddSplitItemForm, AddReceiptForm, AddStoreForm, AddProductForm, ShareItemForm
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.forms import modelformset_factory
from functools import partial, wraps
from django.utils.functional import curry
from django.contrib.auth.forms import User

from .models import Store, Product, ReceiptProduct, Receipt, ShareItem
from users.models import Message


def get_common_context(user, receipt_id=None):
    # Retrieves commonly re-used data for certain views.
    common_context = {}
    receipt_list = []  # Always in common_context
    total_dict = {}  # Always in common_context
    new_messages = [message for message in Message.objects.filter(to_user=user) if message.read is False]
    num_of_new_messages = len(new_messages)
    common_context['num_of_new_messages'] = num_of_new_messages
    for receipt in Receipt.objects.all():
        if receipt.owner == user:
            receipt_list.append(receipt)
            temp_list = [item.price for item in receipt.receiptproduct_set.all()]
            taxed_items = [item.price for item in receipt.receiptproduct_set.all() if item.tax == True]
            total_dict[receipt.id] = format(((sum(taxed_items)*receipt.tax)+(sum(temp_list))), '.2f')
            common_context["total_dict"] = total_dict
            common_context["receipt_list"] = receipt_list
    if receipt_id:
        # only
        current_receipt = get_object_or_404(Receipt, pk=receipt_id)
        if current_receipt.owner != user:
            raise Http404
        items = current_receipt.receiptproduct_set.all()
        for item in items:
            if item.description == 'None':
                description = ''
            else:
                description = item.description
        total = sum([item.price for item in items])
        taxed_items = [item.price for item in items if item.tax == True]
        tax = (sum(taxed_items)*current_receipt.tax)
        total_and_tax = (total + tax)
        common_context['total'] = ("%.2f" % total)
        common_context['tax'] = ("%.2f" % tax)
        common_context['current_receipt'] = current_receipt
        common_context['items'] = items
        common_context['total_and_tax'] = ("%.2f" % total_and_tax)
    return common_context


def index(request):
    if request.user.is_authenticated:
        common_context = get_common_context(request.user)
    else:
        common_context = {}
    return render(request, 'purchase_log/index.html', common_context)


@login_required
def receipts(request):
    common_context = get_common_context(request.user)
    return render(request, 'purchase_log/receipts.html', common_context)


@login_required
def receipt_details(request, receipt_id):
    common_context = get_common_context(request.user, receipt_id)

    context = {}
    for key, value in common_context.items():
        context[key] = value

    return render(request, 'purchase_log/receipt_details.html', context)


@login_required
def add_receipt_product(request, receipt_id):
    ShareItemFormSet = formset_factory(wraps(ShareItemForm)(partial(ShareItemForm, user=request.user)), extra=3)
    current_receipt = get_object_or_404(Receipt, pk=receipt_id)
    if current_receipt.owner != request.user:
        raise Http404
    if request.method != 'POST':
        if current_receipt.split:
            # No data submitted; create a blank form.
            form = AddSplitItemForm(user=request.user, initial={'split': True, 'receipt': current_receipt})
        else:
            form = AddItemForm(user=request.user, initial={'receipt': current_receipt})
        formset = ShareItemFormSet()
    else:
        # POST data submitted; process data.
        form = AddItemForm(user=request.user, data=request.POST)
        formset = ShareItemFormSet(request.POST)
        share_item_form = ShareItemForm(user=request.user)
        if all([form.is_valid(), formset.is_valid()]):
            new_product = form.save(commit=False)
            new_product.owner = request.user
            new_product.receipt = current_receipt
            new_product.save()
            initial_purchaser = share_item_form.save(commit=False)
            initial_purchaser.receipt_product = new_product
            initial_purchaser.purchasers = request.user
            initial_purchaser.save()
            for inline_form in formset:
                if inline_form.cleaned_data:
                    share_item = inline_form.save(commit=False)
                    share_item.receipt_product = ReceiptProduct.objects.get(id=new_product.id)
                    share_item.save()
            return HttpResponseRedirect(reverse('purchase_log:receipt_details', args=[receipt_id]))
    common_context = get_common_context(request.user, receipt_id)

    context = {'current_receipt': current_receipt, 'form': form, 'formset': formset}

    for key, value in common_context.items():
        context[key] = value

    return render(request, 'purchase_log/add_receipt_product_form.html', context)


@login_required
def product_details(request, product_id):
    current_product = get_object_or_404(Product, pk=product_id)
    if current_product.owner != request.user:
        raise Http404
    purchase_list = [purchase for purchase in ReceiptProduct.objects.all().filter(product=current_product)]
    context = {'purchase_list': purchase_list, 'current_product': current_product}

    common_context = get_common_context(request.user)
    for key, value in common_context.items():
        context[key] = value

    return render(request, 'purchase_log/product_details.html', context)


@login_required
def add_receipt(request):
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = AddReceiptForm(user=request.user, initial={'tax': 0.00})
    else:
        # POST data submitted; process data.
        form = AddReceiptForm(user=request.user, data=request.POST, files=request.FILES or None)
        if form.is_valid():
            new_receipt = form.save(commit=False)
            new_receipt.owner = request.user
            new_receipt.save()
            return HttpResponseRedirect(reverse('purchase_log:receipt_details', args=[Receipt.objects.last().pk]))

    context = {'form': form}
    common_context = get_common_context(request.user)
    for key, value in common_context.items():
        context[key] = value
    return render(request, 'purchase_log/add_receipt_form.html', context)


@login_required
def add_store(request):
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = AddStoreForm
    else:
        # POST data submitted; process data.
        form = AddStoreForm(data=request.POST)
        if form.is_valid():
            new_store = form.save(commit=False)
            new_store.owner = request.user
            new_store.save()
            return HttpResponseRedirect(reverse('purchase_log:add_receipt'))

    common_context = get_common_context(request.user)
    context = {'form': form}
    for key, value in common_context.items():
        context[key] = value

    return render(request, 'purchase_log/add_store_form.html', context)


@login_required
def add_product_type(request, receipt_id):
    current_receipt = Receipt.objects.get(id=receipt_id)
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = AddProductForm
    else:
        # POST data submitted; process data.
        form = AddProductForm(data=request.POST)
        if form.is_valid():
            new_product = form.save(commit=False)
            new_product.owner = request.user
            new_product.save()
            return HttpResponseRedirect(reverse('purchase_log:add_product', args=[receipt_id]))

    common_context = get_common_context(request.user, receipt_id)
    context = {'current_receipt': current_receipt, 'form': form}

    for key, value in common_context.items():
        context[key] = value
    return render(request, 'purchase_log/add_product_type_form.html', context)


@login_required
def delete_receipt_product(request, receipt_id, pk):
    receipt_product = get_object_or_404(ReceiptProduct, pk=pk)
    if receipt_product.owner == request.user:
        receipt_product.delete()
    return HttpResponseRedirect(reverse('purchase_log:receipt_details', args=[receipt_id]))

@login_required
def delete_receipt(request, receipt_id):
    receipt = get_object_or_404(Receipt, pk=receipt_id)
    if receipt.owner == request.user:
        receipt.delete()
    return HttpResponseRedirect(reverse('purchase_log:receipts'))


def edit_receipt_product(request, receipt_product_id):
    """Edit an existing entry."""
    item = ReceiptProduct.objects.get(id=receipt_product_id)
    receipt = item.receipt
    if item.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry.
        form = AddItemForm(user=request.user, instance=item)
    else:
        # POST data submitted; process data.
        form = AddItemForm(user=request.user, instance=item, data=request.POST, files=request.FILES or None)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('purchase_log:receipt_details',
                                        args=[receipt.id]))

    common_context = get_common_context(request.user, ReceiptProduct.objects.get(id=receipt_product_id).receipt.id)
    context = {'item': item, 'receipt': receipt, 'form': form}
    for key, value in common_context.items():
        context[key] = value


    return render(request, 'purchase_log/edit_receipt_product.html', context)


def edit_split_receipt_product(request, receipt_product_id):
    """Edit an existing entry."""
    item = ReceiptProduct.objects.get(id=receipt_product_id)
    receipt = item.receipt
    share_item = ShareItem.objects.filter(receipt_product=item)
    ShareItemFormSet = modelformset_factory(ShareItem, form=ShareItemForm)
    ShareItemFormSet.form = staticmethod(curry(ShareItemForm, user=request.user))  # <-This confused the shit out of me.
    if item.owner != request.user:                                                 # But it worked.
        raise Http404

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry.
        form = AddSplitItemForm(user=request.user, instance=item)
        formset = ShareItemFormSet(queryset=share_item)
    else:
        # POST data submitted; process data.
        form = AddSplitItemForm(user=request.user, instance=item, data=request.POST)
        formset = ShareItemFormSet(request.POST)
        if all([form.is_valid(), formset.is_valid()]):
            form.save()
            for inline_form in formset:
                if inline_form.cleaned_data:
                    share_item = inline_form.save(commit=False)
                    share_item.receipt_product = ReceiptProduct.objects.get(id=item.id)
                    share_item.save()
            return HttpResponseRedirect(reverse('purchase_log:receipt_details',
                                        args=[receipt.id]))

    common_context = get_common_context(request.user, ReceiptProduct.objects.get(id=receipt_product_id).receipt.id)
    context = {'item': item, 'receipt': receipt, 'form': form, 'formset': formset}
    for key, value in common_context.items():
        context[key] = value


    return render(request, 'purchase_log/edit_split_receipt_product.html', context)


def edit_receipt(request, receipt_id):
    """Edit an existing entry."""
    receipt = Receipt.objects.get(id=receipt_id)
    if receipt.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry.
        form = AddReceiptForm(user=request.user, instance=receipt, files=request.FILES or None)
    else:
        # POST data submitted; process data.
        form = AddReceiptForm(user=request.user, instance=receipt, files=request.FILES or None, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('purchase_log:receipt_details', args=[receipt_id]))

    context = {'receipt': receipt, 'form': form}
    common_context = get_common_context(request.user)
    for key, value in common_context.items():
        context[key] = value
    return render(request, 'purchase_log/edit_receipt.html', context)