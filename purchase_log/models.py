from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
    tax = models.FloatField()
    split = models.BooleanField(default=False)
    pic = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.store.name + ': ' + str(self.date)


class ReceiptProduct(models.Model):
    receipt = models.ForeignKey(Receipt)
    product = models.ForeignKey(Product)
    price = models.FloatField()
    sale = models.BooleanField()
    description = models.CharField(max_length=500, null=True, blank=True)
    tax = models.BooleanField(default=True)
    owner = models.ForeignKey(User)
    purchaser = models.ForeignKey(User, related_name='purchaser1')
    split = models.BooleanField(default=False)

    def __str__(self):
        return self.product.type


class ShareItem(models.Model):
    receipt_product = models.ForeignKey(ReceiptProduct)
    purchasers = models.ForeignKey(User)

    def __str__(self):
        return self.purchasers.username + ' - ' + \
               self.receipt_product.product.type + ' from ' + \
               self.receipt_product.receipt.store.name + ' on ' + \
               str(self.receipt_product.receipt.date)


class ShareNotificationManager(models.Manager):
    def read_notification(self, notification_id):
        # This won't fail quietly it'll raise an ObjectDoesNotExist exception
        notification = super(ShareNotificationManager, self).get(pk=notification_id)
        notification.read = True
        notification.read_time = timezone.now()
        notification.save()
        return notification


class ShareNotification(models.Model):
    """
    Notifies a user of a new receipt with their name on it.
    """

    objects = ShareNotificationManager()

    to_user = models.ForeignKey(User, related_name='to_user')
    from_user = models.ForeignKey(User, related_name='from_user')
    response = models.NullBooleanField()
    receipt = models.ForeignKey(Receipt)
    time = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)
    response_read = models.NullBooleanField()
    read_time = models.DateTimeField(blank=True, null=True)