from django.contrib import admin

from .models import Store, Product, Receipt, ReceiptProduct

admin.site.register(Store)
admin.site.register(Product)
admin.site.register(Receipt)
admin.site.register(ReceiptProduct)
