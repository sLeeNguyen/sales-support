from django.db import models
from django.utils import timezone

from core.utils import server_timezone
from customers.models import Customer
from coupons.models import Coupon
from users.models import User
from products.models import Product


class InvoiceManager(models.Manager):
    prefix = 'HD'

    def gen_default_code(self):
        query_set = self.get_queryset()
        postfix = str(query_set.count())
        return self.prefix + '0'*(6 - len(postfix)) + postfix


class OrderManager(models.Manager):
    prefix = 'DH'

    def gen_default_code(self):
        query_set = self.get_queryset()
        postfix = str(query_set.count())
        return self.prefix + '0'*(6 - len(postfix)) + postfix


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

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, blank=True, null=True)
    staff = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = OrderManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_product_items = []

    def add_item(self, product, quantity, price) -> 'ProductItem':
        product_item = ProductItem(product=product, price=price, quantity=quantity)
        self.list_product_items.append(product_item)
        return product_item

    def save_list_items(self):
        # list product items must be saved after its order be saved
        for item in self.get_list_product_items():
            item.order = self
        res = ProductItem.objects.bulk_create(self.list_product_items)
        return res

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.order_code = Order.objects.gen_default_code()
        super().save(force_insert, force_update, using, update_fields)
        self.save_list_items()

    def get_list_product_items(self):
        if len(self.list_product_items) == 0 and self.id:
            self.list_product_items = list(ProductItem.objects.filter(order=self))
        return self.list_product_items

    def calc_total_money(self):
        total = 0
        for product_item in self.list_product_items:
            total += product_item.get_sub_total()
        return total

    def calc_discount(self):
        return 0

    def get_total_products(self):
        num_of_products = 0
        for product_item in self.list_product_items:
            num_of_products += product_item.quantity
        return num_of_products

    def get_customer(self):
        if self.customer is not None:
            return self.customer.customer_name
        return "Khách lẻ"


class Invoice(models.Model):
    STATUS_CHOICES = [
        (0, 'Huỷ'),
        (1, 'Hoàn thành'),
    ]

    invoice_code = models.CharField(max_length=10, blank=True, null=True)
    time_create = models.DateTimeField(auto_now_add=timezone.now())
    status = models.PositiveIntegerField(default=1, choices=STATUS_CHOICES)
    total_products = models.FloatField(blank=False, null=False)
    total = models.PositiveIntegerField(blank=False, null=False)
    customer_given = models.PositiveIntegerField(blank=True, null=True)
    discount = models.PositiveIntegerField(default=0, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = InvoiceManager()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.invoice_code = Invoice.objects.gen_default_code()
        super().save(force_insert, force_update, using, update_fields)
        return self

    def get_time_create_format(self):
        return server_timezone(self.time_create).strftime("%d/%m/%Y %H:%M")

    def get_staff_name(self):
        return self.staff.get_display_name()

    @property
    def must_pay(self):
        return self.total - self.discount

    @property
    def refund(self):
        return self.customer_given - self.must_pay


class ProductItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=0)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def get_sub_total(self):
        return int(self.price * self.quantity)
