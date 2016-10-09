from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views import generic
from .models import Store, Product, ReceiptProduct, Receipt
from .forms import AddItemForm, AddReceiptForm, AddStoreForm, AddProductForm
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'purchase_log/index.html')


@login_required
def receipts(request):
    receipt_list = []
    item_list = []
    total_dict = {}
    for receipt in Receipt.objects.all():
        if receipt.owner == request.user:
            receipt_list.append(receipt)
            temp_list = [item.price for item in receipt.receiptproduct_set.all()]
            total_dict[receipt.id] = format(((sum(temp_list)*receipt.tax)+(sum(temp_list))), '.2f')
    total = sum([item.price for item in item_list])
    tax = (total*.07)
    total_and_tax = (total + tax)

    context = {'receipt_list': receipt_list, 'total_dict': total_dict}
    return render(request, 'purchase_log/receipts.html', context)


@login_required
def receipt_details(request, receipt_id):
    current_receipt = Receipt.objects.get(id=receipt_id)
    if current_receipt.owner != request.user:
        raise Http404
    items = current_receipt.receiptproduct_set.all()
    for item in items:
        if item.description == 'None':
            description = ''
        else:
            description = item.description
    total = sum([item.price for item in items])
    tax = (total*.07)
    total_and_tax = (total + tax)
    context = {
        'current_receipt': current_receipt,
        'items': items,
        'total': ("%.2f" % total),
        'tax': ("%.2f" % tax),
        'total_and_tax': ("%.2f" % total_and_tax),
        }
    return render(request, 'purchase_log/receipt_details.html', context)


@login_required
def add_receipt_product(request, receipt_id):
    current_receipt = Receipt.objects.get(id=receipt_id)
    if current_receipt.owner != request.user:
        raise Http404
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = AddItemForm(initial={'receipt': current_receipt})
    else:
        # POST data submitted; process data.
        form = AddItemForm(data=request.POST)
        if form.is_valid():
            new_product = form.save(commit=False)
            new_product.owner = request.user
            new_product.receipt = current_receipt
            new_product.save()
            return HttpResponseRedirect(reverse('purchase_log:receipt_details', args=[receipt_id]))

    context = {'current_receipt': current_receipt, 'form': form}
    return render(request, 'purchase_log/add_receipt_product_form.html', context)


@login_required
def product_details(request, product_id):
    current_product = Product.objects.get(id=product_id)
    if current_product.owner != request.user:
        raise Http404
    purchase_list = [purchase for purchase in ReceiptProduct.objects.all().filter(product=current_product)]
    context = {'purchase_list': purchase_list, 'current_product': current_product}
    return render(request, 'purchase_log/product_details.html', context)


@login_required
def add_receipt(request):
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = AddReceiptForm
    else:
        # POST data submitted; process data.
        form = AddReceiptForm(data=request.POST)
        if form.is_valid():
            new_receipt = form.save(commit=False)
            new_receipt.owner = request.user
            new_receipt.save()
            return HttpResponseRedirect(reverse('purchase_log:receipt_details', args=[Receipt.objects.last().pk]))

    context = {'form': form}
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

    context = {'form': form}
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

    context = {'current_receipt': current_receipt, 'form': form}
    return render(request, 'purchase_log/add_product_type_form.html', context)


@login_required
def delete_receipt_product(request, receipt_id, pk):
    receipt_product = ReceiptProduct.objects.get(pk=pk)
    receipt_product.delete()
    return HttpResponseRedirect(reverse('purchase_log:receipt_details', args=[receipt_id]))