from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation

from customers.models import Customer
from coupons.models import Coupon
from users.models import Staff
from products.models import ProductItem


class Invoice(models.Model):
    STATUS_CHOICES = [
        (0, 'Xoá'),
        (1, 'Hoàn thành'),
    ]

    invoice_code = models.CharField(max_length=10, blank=False, null=False)
    time_create = models.DateTimeField(auto_now_add=timezone.now())
    note = models.TextField(default='')
    status = models.PositiveIntegerField(default=1, choices=STATUS_CHOICES)
    total_products = models.PositiveIntegerField(blank=False, null=False)
    total = models.PositiveIntegerField(blank=False, null=False)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    product_items = GenericRelation(ProductItem, related_query_name='invoice')


class Order(models.Model):
    STATUS_CHOICES = [
        (0, 'Xoá'),
        (1, 'Hoàn thành'),
        (2, 'Chưa xử lý'),
    ]

    order_code = models.CharField(max_length=10, blank=False, null=False)
    time_create = models.DateTimeField(auto_now_add=timezone.now())
    note = models.TextField(default='')
    status = models.PositiveIntegerField(default=2, choices=STATUS_CHOICES)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    product_items = GenericRelation(ProductItem, related_query_name='order')
