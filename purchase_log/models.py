from django.db import models
from django.contrib.auth.models import User


class Store(models.Model):
    name = models.CharField(max_length=250)
    owner = models.ForeignKey(User)


    def __str__(self):
        return self.name


class Product(models.Model):
    type = models.CharField(max_length=250)
    owner = models.ForeignKey(User)

    def __str__(self):
        return self.type


class Receipt(models.Model):
    store = models.ForeignKey(Store)
    date = models.DateField()
    owner = models.ForeignKey(User)

    def __str__(self):
        return self.store.name + ': ' + str(self.date)


class ReceiptProduct(models.Model):
    receipt = models.ForeignKey(Receipt)
    product = models.ForeignKey(Product)
    price = models.FloatField()
    sale = models.BooleanField()
    description = models.CharField(max_length=500, null=True, blank=True)
    owner = models.ForeignKey(User)

    def __str__(self):
        return self.product.type