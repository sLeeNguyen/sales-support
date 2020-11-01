from django.utils.translation import gettext_lazy as _
from products.models import Product, Category
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


fields = ['product_code', 'product_name', 'sell_price', 'cost_price', 'available']


# define exceptions
class CategoryNotExistsError(ObjectDoesNotExist):
    pass


class ProductAlreadyExistsError(Exception):
    pass


class ProductNotExistsError(Exception):
    pass


class ProductServices:
    def __init__(self, product_code, product_name, sell_price, available, category_name,
                 barcode='',
                 description='',
                 cost_price=0,
                 unit=Product.UNIT_INT,
                 status=1,
                 mfg=None,
                 exp=None
                 ):
        self._product_code = product_code
        self._product_name = product_name
        self._barcode = barcode
        self._description = description
        self._cost_price = cost_price
        self._sell_price = sell_price
        self._available = available
        self._unit = unit
        self._status = status
        self._mfg = mfg
        self._exp = exp
        self._category = self.find_category(category_name=category_name)

    def execute(self):
        """
        This function will validate data.
        New product will be created if there is no error
        """
        self.valid_data()
        product = Product.objects.create(
            product_code=self._product_code,
            barcode=self._barcode,
            product_name=self._product_name,
            description=self._description,
            cost_price=self._cost_price,
            sell_price=self._sell_price,
            available=self._available,
            unit=self._unit,
            status=self._status,
            mfg=self._mfg,
            exp=self._exp,
            category=self._category
        )
        return product

    def valid_data(self):
        """
        Valid product name and code, if exists, an error will be thrown
        """
        if self._product_code:
            product_qs = Product.objects.find_by_code(product_code=self._product_code)
            if product_qs.exists():
                error_msg = (
                    "Mã sản phẩm '{}' đã tồn tại".format(self._product_code)
                )
                raise ProductAlreadyExistsError(_(error_msg))

        product_qs2 = Product.objects.find_by_name(product_name=self._product_name)
        if product_qs2.exists():
            error_msg = (
                "Tên sản phẩm '{}' đã tồn tại".format(self._product_name)
            )
            raise ProductAlreadyExistsError(_(error_msg))

    @classmethod
    def find_category(cls, category_name):
        try:
            category = Category.objects.get(category_name=category_name)
            return category
        except ObjectDoesNotExist:
            raise CategoryNotExistsError(
                _("Nhóm hàng '{}' không tồn tại".format(category_name))
            )

    @classmethod
    def get_products_datatables(cls, post):
        """
        Get list products from database base on properties in POST request
        """
        start = int(post['start'])
        length = int(post['length'])
        field_order = fields[int(post['order[0][column]'])]
        order_type = post['order[0][dir]']
        search_val = post['search[value]']

        results = Product.objects.all()
        if search_val:
            results = results.filter(
                Q(product_code__icontains=search_val) | Q(product_name__icontains=search_val)
            )
        if order_type == 'asc':
            results = results.order_by(field_order)
        else:  # order_type = 'desc'
            results = results.order_by('-' + field_order)
        return results[start:length]
