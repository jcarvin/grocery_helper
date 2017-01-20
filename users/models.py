from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MessageManager(models.Manager):
    def read_message(self, message_id):
        # This won't fail quietly it'll raise an ObjectDoesNotExist exception
        message = super(MessageManager, self).get(pk=message_id)
        message.read = True
        message.read_time = timezone.now()
        message.save()
        return message

class Message(models.Model):
    """
    Simple text based messages.
    """

    objects = MessageManager()

    from_user = models.ForeignKey(User, related_name='User1')
    to_user = models.ForeignKey(User, related_name='User2')
    subj = models.CharField(max_length=150, null=True, blank=True)
    text = models.CharField(max_length=2000)
    time = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)
    read_time = models.DateTimeField(blank=True, null=True)
