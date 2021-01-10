from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404

from core.utils import client_timezone
from customers.models import Customer
from elasticsearch_client import es as elasticsearch
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
    _store = None

    def __init__(self, request, store, oid=None):
        self.request = request
        self.__get_list_orders()
        self._store = store
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
        customer = None
        if "customer" in self.current_order:
            try:
                customer = Customer.objects.get(pk=self.current_order["customer"]["id"])
            except ObjectDoesNotExist:
                raise SalesException("Khách hàng '%s' không tồn tại!" % self.current_order["customer"]["name"])
        order = Order(staff=self.request.user, status=status, store=self._store)
        if note is not None:
            order.note = note
        if customer is not None:
            order.customer = customer

        products = []
        for product_item in self.current_order['data']:
            if product_item['quantity'] == 0:
                continue
            product = Product.objects.get(pk=product_item['product']['id'])
            quantity = self.valid_product_quantity(product, product_item['quantity'])
            product.available -= quantity
            products.append(product)
            order.add_item(product, quantity, product.sell_price)

        if len(products) == 0:
            raise SalesException("Đơn hàng rỗng")

        order.save()
        Product.objects.bulk_update(products, fields=['available'])
        # save list items to elasticsearch
        elasticsearch.bulk_index_product_item(order.get_list_product_items(), store_id=order.store.id)
        self.order = order
        return order

    def __valid_order(self, products, quantities):
        if products is None or len(products) == 0:
            raise SalesException("Đơn hàng rỗng")
        for i in range(len(products)):
            self.valid_product_quantity(products[i], quantities[i])

    def pay_order(self):
        customer_pay = int(self.request.POST.get("customerGiven"))
        if customer_pay < self.calc_total_fees():
            raise SalesException(
                "Khách hàng thanh toán chưa đủ."
            )
        self.create_new_order(self.request.POST.get("note"))
        invoice = Invoice(total_products=self.order.get_total_products(),
                          total=self.order.calc_total_money(),
                          discount=self.order.calc_discount(),
                          customer_given=customer_pay,
                          order=self.order,
                          staff=self.request.user,
                          store=self._store)
        self.invoice = invoice.save()
        # save to elasticsearch
        elasticsearch.index_invoice(invoice_id=invoice.id,
                                    invoice_code=invoice.invoice_code,
                                    total=invoice.must_pay,
                                    total_product=invoice.total_products,
                                    time_created=client_timezone(invoice.time_create),
                                    staff=invoice.staff.username,
                                    order_id=invoice.order.id,
                                    status=invoice.status,
                                    store_id=invoice.store.id)
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

    def add_customer_to_order(self, customer):
        self.current_order["customer"] = {
            "id": customer.id,
            "name": customer.customer_name,
            "code": customer.customer_code,
            "points": customer.points
        }
        return self.current_order

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

    def remove_customer(self):
        if "customer" in self.current_order:
            self.current_order.pop("customer")

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

    def calc_total_fees(self):
        total_fees = 0
        for product_item in self.current_order['data']:
            total_fees += product_item['product']['sell_price'] * product_item['quantity']
        total_fees = int(total_fees)
        return total_fees


class TransactionManagement:
    request = None
    fields = ['invoice_code', 'time_create', 'customer_name', 'discount', 'total']
    store = None
    invoice = None

    def __init__(self, request, store):
        self.request = request
        self.store = store

    def get_invoices_datatables(self):
        post = self.request.POST
        start = int(post['start'])
        end = start + int(post['length'])
        field_order = self.fields[int(post['order[0][column]']) - 1]
        order_type = post['order[0][dir]']
        search_val = post['search[value]']
        invoice_status = int(post.get('invoiceStatus', 1))
        from_time = post['intervalTime[from]']
        to_time = post['intervalTime[to]']
        time_format = "%Y-%m-%d"
        from datetime import datetime
        from django.utils.timezone import make_aware, timedelta
        aware_from_time = make_aware(datetime.strptime(from_time, time_format))
        aware_to_time = make_aware(datetime.strptime(to_time, time_format)) + timedelta(days=1)

        results = Invoice.objects.filter(
            store=self.store,
            status=invoice_status,
            time_create__range=[aware_from_time, aware_to_time])
        if search_val:
            results = results.filter(
                Q(invoice_code__icontains=search_val) |
                Q(order__customer__customer_name__icontains=search_val)
            )
        if order_type == 'asc':
            results = results.order_by(field_order)
        else:
            results = results.order_by('-' + field_order)

        data = []
        for item in results[start:end]:
            data.append({
                "0": "",
                "1": item.invoice_code,
                "2": item.get_time_create_format(),
                "3": item.order.get_customer(),
                "4": '{:20,d}'.format(item.discount),
                "5": '{:20,d}'.format(item.total),
                "DT_RowId": item.id
            })
        return {
            "draw": int(post["draw"]),
            "recordsTotal": results.count(),
            "recordsFiltered": results.count(),
            "data": data
        }

    def change_invoice_status(self, invoice_id, new_status):
        self.invoice = get_object_or_404(Invoice, pk=invoice_id)
        self.invoice.status = new_status
        elasticsearch.update_invoice_status(self.invoice.id, new_status)
        self.invoice.save()
