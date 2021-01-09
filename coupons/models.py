from django.db import models
from django.utils import timezone

from stores.models import Store


class Coupon(models.Model):
    SCOPE_CHOICES = [
        ('I', 'Toàn bộ hoá đơn'),
        ('P', 'Sản phẩm'),
    ]

    BENEFICIARY_CHOICES = [
        ('E', 'Mọi khách hàng'),
        ('N', 'Khách hàng hệ thống'),
        ('V', 'Khách hàng VIP')
    ]

    title = models.CharField(max_length=100, blank=False, null=False)
    scope = models.CharField(max_length=1, choices=SCOPE_CHOICES, blank=False, null=False)
    beneficiary = models.IntegerField(choices=BENEFICIARY_CHOICES, default='E')
    discount_percent = models.FloatField(blank=True)
    max_discount_money = models.PositiveIntegerField(blank=True)
    app_date = models.DateTimeField(default=timezone.now)
    exp_date = models.DateTimeField(blank=False, null=False)
    note = models.TextField(default='')
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)
