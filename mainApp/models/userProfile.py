# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class UserProfile(models.Model):
    """
    User Profile model
    """

    user = models.OneToOneField(User, primary_key=True, related_name='profile', on_delete= models.CASCADE)

    phone_number = models.CharField(
        verbose_name="Phone Number",
        max_length=14
    )

    photo = models.ImageField(
        blank=True,
        verbose_name=u"Avatar",
        upload_to=user_directory_path,
        null=True)

    chat_id = models.CharField(
        max_length=256,
        blank=True,
        verbose_name=u"Telegram Chat ID",
        null=True
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name=u"Verified user"
    )

    def __str__(self):
        return u"User: %s" % self.user.get_full_name()