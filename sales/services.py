from django.db.models import Q

from products.models import Product
from sales.exceptions import OrderDoesNotExists, SalesException
from sales.models import Order, Invoice


def search_products(search_val):
    products = Product.objects.filter(Q(product_code__icontains=search_val) | Q(product_name__icontains=search_val))
    return products


class SalesManagement:
    list_orders = None
    order = None
    invoice = None
    request = None

    def __init__(self, request, oid=None):
        self.request = request
        self.__get_list_orders()
        if oid is not None:
            self.index, self.current_order = self.get_order_dict(oid)
            print(self.list_orders)
            if self.current_order is None:
                raise OrderDoesNotExists()

    def __get_list_orders(self):
        self.list_orders = self.request.session["orders"]
        return self.list_orders

    def get_order_dict(self, oid=None):
        if oid is None:
            return self.index, self.current_order
        orders = self.request.session['orders']
        for index, order in enumerate(orders, start=0):
            if order['id'] == oid:
                return index, order
        return None, None

    def create_new_order(self, note=None, status=1):
        order = Order(staff=self.request.user, status=status)
        if note is not None:
            order.note = note
        order.save()
        product_ids = []
        quantities = []
        for product_item in self.current_order['data']:
            if product_item['quantity'] == 0:
                continue
            product_ids.append(product_item['product']['id'])
            quantities.append(product_item['quantity'])
        products = Product.objects.filter(id__in=product_ids)

        self.__valid_order(products, quantities)
        for i in range(len(products)):
            product = products[i]
            product.available -= quantities[i]
            order.add_item(product, quantities[i])
        Product.objects.bulk_update(products, fields=['available'])
        order.save_list_items()
        self.order = order
        return order

    def __valid_order(self, products, quantities):
        if products is None or len(products) == 0:
            raise SalesException("Đơn hàng rỗng")
        for i in range(len(products)):
            self.valid_product_quantity(products[i], quantities[i])

    def pay_order(self):
        self.create_new_order(self.request.POST.get("note"))
        invoice = Invoice(total_products=self.order.get_total_products(),
                          total=self.order.calc_total_money(),
                          discount=self.order.calc_discount(),
                          order=self.order,
                          staff=self.request.user)
        self.invoice = invoice.save()
        # self.remove_order_dict()
        return invoice

    def add_product_to_order(self, product):
        order_data = self.current_order['data']
        for index, data in enumerate(order_data, start=1):
            if data['product']['id'] == product.id:
                data['quantity'] += 1
                context = data.copy()
                context['index'] = index
                break
        else:
            order_data.append({'product': product.to_dict(), 'quantity': 1})
            context = order_data[-1].copy()
            context['index'] = len(order_data)
        return context

    def update_quantity_product_item(self, product_id, quantity):
        product = Product.objects.get(pk=product_id)
        quantity = self.valid_product_quantity(product, quantity)
        order_data = self.current_order["data"]

        for pdict in order_data:
            if pdict['product']['id'] == product_id:
                pdict['quantity'] = quantity
                return pdict
        raise SalesException("Sản phẩm không tồn tại")

    def valid_product_quantity(self, product, quantity):
        """
        Validate quantity of product item
        """
        if product.available < quantity:
            raise SalesException(
                "Sản phẩm \"%s\" chỉ còn: %s %s" %
                (product.product_name, str(product.get_available()), product.get_unit_display())
            )
        if product.unit == Product.UNIT_INT:
            # quantity must be integer
            if (quantity < 0) or (quantity - int(quantity) > 0.00001):
                raise SalesException(
                    'Sản phẩm "%s" có số lượng không hợp lệ' % product.product_name
                )
            return int(quantity)
        return quantity

    def delete_order(self):
        pass

    def remove_product_item(self, product_id):
        order_data = self.current_order['data']
        for index, pdict in enumerate(order_data, start=0):
            if pdict['product']['id'] == product_id:
                del order_data[index]
        return order_data

    def remove_order_dict(self):
        if self.current_order:
            del self.list_orders[self.index]
        if len(self.list_orders) == 0:
            self.list_orders.append({'id': 1, 'data': []})

    def make_payment(self):
        total_fees = 0
        num_of_products = 0
        discount = 0
        for product_item in self.current_order['data']:
            total_fees += product_item['product']['sell_price'] * product_item['quantity']
            num_of_products += product_item['quantity']
        total_fees = int(total_fees)
        return {
            "numOfProducts": num_of_products,
            "total": total_fees,
            "mustPay": total_fees - discount,
        }
