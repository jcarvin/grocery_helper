from django.conf.urls import url
from . import views

urlpatterns = [
    # purchase_log/
    url(r'^$', views.index, name='index'),

    # purchase_log/receipts/
    url(r'^receipts/$', views.receipts, name='receipts'),

    # purchase_log/receipts/<receipt id>
    url(r'^receipts/(?P<receipt_id>\d+)/$', views.receipt_details, name='receipt_details'),

    # purchase_log/receipts/add_receipt_product/<receipt_id>
    url(r'^receipts/add_receipt_product/(?P<receipt_id>\d+)/$', views.add_receipt_product, name='add_product'),

    # purchase_log/receipts/delete_receipt_product/<receipt_product_id>
    url(r'^receipts/delete_receipt_product/(?P<receipt_id>\d+)/(?P<pk>\d+)/$', views.delete_receipt_product,
        name="delete_receipt_product"),

    # purchase_log/receipts/add_product_type>
    url(r'^receipts/add_product_type/(?P<receipt_id>\d+)/$', views.add_product_type, name='add_product_type'),

    # purchase_log/receipts/add_receipt>
    url(r'^receipts/add_receipt/$', views.add_receipt, name='add_receipt'),

    # purchase_log/receipts/add_store>
    url(r'^receipts/add_store/$', views.add_store, name='add_store'),

    # purchase_log/products/<item_id>
    url(r'^products/(?P<product_id>\d+)/$', views.product_details, name='product_details'),
]