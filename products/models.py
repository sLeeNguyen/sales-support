from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class CategoryManager(models.Manager):
    pass


class ProductManager(models.Manager):
    def find_by_code(self, product_code):
        query_set = self.get_queryset()
        return query_set.filter(product_code=product_code)

    def find_by_name(self, product_name):
        query_set = self.get_queryset()
        return query_set.filter(product_name=product_name)


class Category(models.Model):
    category_name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    description = models.TextField(default='', blank=True)

    def __str__(self):
        return self.category_name.strip()


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
    barcode = models.CharField(max_length=30, unique=True, blank=True)
    product_name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(default='', blank=True)
    images = models.CharField(max_length=255, default='', blank=True)
    cost_price = models.PositiveIntegerField(default=0, blank=True, null=False)
    sell_price = models.PositiveIntegerField(blank=False, null=False)
    available = models.FloatField(default=0, blank=False, null=False)
    unit = models.CharField(default='INT', choices=UNIT_CHOICES, max_length=3)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)
    mfg = models.DateField(blank=True, null=True)
    exp = models.DateField(blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    objects = ProductManager()

    def __str__(self):
        return self.product_name.strip()


class ProductItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    sales_object_id = models.IntegerField()
    sales_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey('sales_content_type', 'sales_object_id')
