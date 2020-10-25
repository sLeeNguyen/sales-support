from django.db import models
from sales_support_website import constants


class Customer(models.Model):
    GROUP_CHOICES = [
        (0, 'Normal'),
        (1, 'VIP'),
    ]

    customer_code = models.CharField(max_length=10, blank=False, null=False)
    customer_name = models.CharField(max_length=50, blank=False, null=False)
    birthday = models.DateField(blank=True, null=True)
    gender = models.IntegerField(default=0, choices=constants.GENDER_CHOICES)
    phone_number = models.CharField(max_length=10, blank=False, null=False)
    email = models.EmailField(max_length=50, default='')
    address = models.CharField(max_length=255, default='')
    note = models.TextField(default='')
    group_type = models.IntegerField(default=0, choices=GROUP_CHOICES)
    points = models.PositiveIntegerField(default=0)
