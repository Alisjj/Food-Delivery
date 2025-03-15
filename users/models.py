from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    delivery_location = models.CharField(max_length=255, null=True, blank=True)
    delivery_latitude = models.FloatField(null=True, blank=True)
    delivery_longitude = models.FloatField(null=True, blank=True)
