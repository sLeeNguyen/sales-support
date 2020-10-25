from django.db import models
from django.contrib.auth.models import AbstractUser
from sales_support_website import constants


class Staff(AbstractUser):
    display_name = models.CharField(max_length=50, blank=False, null=False)
    gender = models.IntegerField(default=0, choices=constants.GENDER_CHOICES)
    birthday = models.DateField(blank=True)
    phone_number = models.CharField(max_length=10, blank=True)
