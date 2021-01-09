from django.db import models
from django.utils import timezone


class Store(models.Model):
    store_name = models.CharField(max_length=150, unique=True, blank=False, null=False)
    date_create = models.DateTimeField(default=timezone.now)
