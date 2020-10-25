from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Category(models.Model):
    category_name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(default='')


class Product(models.Model):
    UNIT_GRAM = 'GR'
    UNIT_KILOGRAM = 'KG'
    UNIT_INT = 'INT'

    UNIT_CHOICES = [
        (UNIT_GRAM, '100 gram'),
        (UNIT_KILOGRAM, 'kilogram'),
        (UNIT_INT, 'chiếc/cái')
    ]

    STATUS_CHOICES = [
        (0, 'xoá'),
        (1, 'đang bán'),
        (2, 'ngừng bán')
    ]

    product_code = models.CharField(max_length=30, blank=False, null=False)
    barcode = models.CharField(max_length=30, unique=True, default='')
    product_name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(default='')
    images = models.CharField(max_length=255, default='')
    cost_price = models.PositiveIntegerField(blank=False, null=False)
    sell_price = models.PositiveIntegerField(blank=False, null=False)
    available = models.FloatField(blank=False, null=False)
    unit = models.CharField(default='INT', choices=UNIT_CHOICES, max_length=3)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)
    mfg = models.DateField(blank=False, null=False)
    exp = models.DateField(blank=False, null=False)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class ProductItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    sales_object_id = models.IntegerField()
    sales_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey('sales_content_type', 'sales_object_id')
