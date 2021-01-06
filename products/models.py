from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class ProductManager(models.Manager):
    prefix = 'SP'

    def find_by_code(self, product_code):
        query_set = self.get_queryset()
        return query_set.filter(product_code=product_code)

    def find_by_name(self, product_name):
        query_set = self.get_queryset()
        return query_set.filter(product_name=product_name)

    def gen_default_code(self):
        query_set = self.get_queryset()
        postfix = str(query_set.filter(Q(product_code__startswith=self.prefix)).count())
        return self.prefix + '0'*(6 - len(postfix)) + postfix


class Category(models.Model):
    category_name = models.CharField(_("Tên nhóm"), max_length=255, unique=True, blank=False, null=False)
    description = models.TextField(_("Mô tả"), default='', blank=True)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    UNIT_GRAM = 'GR'
    UNIT_KILOGRAM = 'KG'
    UNIT_INT = 'INT'

    UNIT_CHOICES = [
        (UNIT_GRAM, 'gram'),
        (UNIT_KILOGRAM, 'kilogram'),
        (UNIT_INT, 'chiếc/cái')
    ]

    STATUS_CHOICES = [
        (0, 'xoá'),
        (1, 'đang bán'),
        (2, 'ngừng bán')
    ]

    product_code = models.CharField(_('Mã hàng'), max_length=30, blank=False, null=False)
    barcode = models.CharField(_('Mã vạch'), max_length=30, blank=True, null=True)
    product_name = models.CharField(_('Tên hàng'), max_length=255, blank=False, null=False)
    description = models.TextField(_('Mô tả'), default='', blank=True)
    image1 = models.ImageField(_('Ảnh 1'), upload_to='images/', blank=True, null=True)
    image2 = models.ImageField(_('Ảnh 2'), upload_to='images/', blank=True, null=True)
    image3 = models.ImageField(_('Ảnh 3'), upload_to='images/', blank=True, null=True)
    image4 = models.ImageField(_('Ảnh 4'), upload_to='images/', blank=True, null=True)
    image5 = models.ImageField(_('Ảnh 5'), upload_to='images/', blank=True, null=True)
    cost_price = models.PositiveIntegerField(_('Giá nhập'), default=0, blank=True, null=False)
    sell_price = models.PositiveIntegerField(_('Giá bán'), blank=False, null=False)
    available = models.FloatField(_('Số lượng'), default=0, blank=False, null=False)
    unit = models.CharField(_('Đơn vị'), default='INT', choices=UNIT_CHOICES, max_length=3)
    status = models.IntegerField(_('Trạng thái'), default=1, choices=STATUS_CHOICES)
    mfg = models.DateField(_('Ngày sản xuất'), blank=True, null=True)
    exp = models.DateField(_('Ngày hết hạn'), blank=True, null=True)

    category = models.ForeignKey(verbose_name=_('Nhóm hàng'), to=Category, on_delete=models.CASCADE)

    objects = ProductManager()

    def __str__(self):
        return self.product_name.strip()

    def get_list_images(self):
        list_url = []
        if self.image1:
            list_url.append(self.image1.url)
        if self.image2:
            list_url.append(self.image2.url)
        if self.image3:
            list_url.append(self.image3.url)
        if self.image4:
            list_url.append(self.image4.url)
        if self.image5:
            list_url.append(self.image5.url)
        return list_url

    def get_available(self):
        if self.unit == self.UNIT_INT:
            return int(self.available)
        return self.available

    def get_thumbnail(self):
        list_url = self.get_list_images()
        if not list_url:
            return '/resource/images/default_product.jpg'
        else:
            return list_url[0]

    def to_dict(self):
        return {
            'id': self.id,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'sell_price': self.sell_price,
            'available': self.get_available(),
            'unit': self.get_unit_display()
        }
