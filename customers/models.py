from django.db import models
from django.utils.translation import gettext_lazy as _

from sales_support_website import constants


class CustomerManager(models.Manager):
    prefix = 'KH'

    def gen_default_code(self):
        query_set = self.get_queryset()
        postfix = str(query_set.count())
        return self.prefix + '0' * (6 - len(postfix)) + postfix


class Customer(models.Model):
    GROUP_CHOICES = [
        (0, 'Khách thường'),
        (1, 'Khách VIP'),
    ]

    customer_code = models.CharField(_("Mã khách hàng"), max_length=10, blank=False, null=False)
    customer_name = models.CharField(_("Tên khách hàng"), max_length=50, blank=False, null=False)
    birthday = models.DateField(_("Ngày sinh"), blank=True, null=True)
    gender = models.IntegerField(_("Giới tính"), default=0, choices=constants.GENDER_CHOICES)
    phone_number = models.CharField(_("Số điện thoại"), max_length=10, blank=True, null=True)
    email = models.EmailField(_("Email"), max_length=50, blank=True, null=True)
    address = models.CharField(_("Địa chỉ"), max_length=255, blank=True, null=True)
    note = models.TextField(_("Ghi chú"), blank=True, default='')
    group_type = models.IntegerField(_("Nhóm"), default=0, choices=GROUP_CHOICES)
    points = models.PositiveIntegerField(_("Điểm tích luỹ"), blank=True, default=0)

    objects = CustomerManager()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.customer_code = Customer.objects.gen_default_code()
        super().save(force_insert, force_update, using, update_fields)
