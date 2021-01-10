from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, Http404
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.template.loader import render_to_string
from django.views import View

from core.views import LoginRequire
from customers.forms import CustomerForm
from customers.models import Customer
from customers.services import CustomerManagement
from products.models import Product
from sales import services
from sales.exceptions import OrderDoesNotExists, SalesException
from sales.models import Invoice
from sales.services import SalesManagement, TransactionManagement
from stores.exceptions import UserNotInStoreException
from stores.services import StoreManagement


class SalesView(LoginRequire, View):

    def get(self, request, store_name, *args, **kwargs):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        request.session['orders'] = [{'id': 1, 'data': []}]
        customer_form = CustomerForm()
        context = {
            'oid': 1,
            'form': customer_form,
            'store_name': store_name
        }
        return render(request, template_name='sales/sales.html', context=context)


class OrderSessionView(LoginRequire, View):
    service_class = SalesManagement

    def get(self, request, store_name, oid):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        oid = int(oid)
        try:
            service = self.service_class(request, store, oid)
        except OrderDoesNotExists:
            return HttpResponse(status=400)
        index, order = service.get_order_dict()
        context = {'oid': order['id'], 'list_items': order['data']}
        html = render_to_string(template_name='sales/cart.html', context=context)
        response = {
            "order": html,
            "payment": service.make_payment()
        }
        if "customer" in order:
            response.update({"customer": order["customer"]})
        return JsonResponse(data=response, status=200)

    def post(self, request, store_name):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        orders = request.session['orders']
        if len(orders) == 15:
            response = {"status": "failed", "msg": "Không thể vượt quá 15 hoá đơn cùng lúc."}
            return JsonResponse(data=response, status=200)
        list_oids = [o['id'] for o in orders]
        list_oids.sort()

        new_id = 1
        for x in list_oids:
            if x == new_id:
                new_id += 1
        orders.append({'id': new_id, 'data': []})
        response = {
            "status": "success",
            "oid": new_id,
        }
        request.session.modified = True
        return JsonResponse(data=response, status=200)

    def delete(self, request, store_name, oid):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        oid = int(oid)
        try:
            service = self.service_class(request, store, oid)
        except OrderDoesNotExists:
            return HttpResponse(status=400)
        service.remove_order_dict()
        request.session.modified = True
        return HttpResponse(status=200)


class OrderView(LoginRequire, View):
    service_class = SalesManagement

    def post(self, request, store_name, oid):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        oid = int(oid)
        try:
            service = self.service_class(request, oid)
        except OrderDoesNotExists:
            return HttpResponse(status=400)
        try:
            service.create_new_order(note=request.POST.get("note"), status=2)
        except SalesException as e:
            response = {
                "status": "failed",
                "msg": str(e)
            }
            return JsonResponse(data=response, status=200)
        response = {
            "status": "success",
        }
        return JsonResponse(data=response, status=200)


class SearchProductView(LoginRequire, View):
    def get(self, request, store_name):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        query = request.GET.get('q')
        products = services.search_products(query)
        html = render(request, template_name='sales/product_search_item.html', context={'data': products})
        return HttpResponse(html)


class SearchCustomerView(LoginRequire, View):
    service_class = CustomerManagement

    def get(self, request, store_name):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        key_search = request.GET.get('q')
        result = self.service_class(request, store).search_customer_by_key(key_search)
        if result["num_of_results"] == 0:
            context = {"empty": True}
        else:
            context = {
                "list_customers": result["list_customers"]
            }
        return render(request=request, template_name="sales/customer_search_item.html", context=context)


class CartView(LoginRequire, View):
    service_class = SalesManagement

    def get(self, request, oid):
        pass
        # order = self.__get_order(oid)
        # html = render_to_string(template_name='sales/cart.html', context={'list_items': order['data']})
        # response = {
        #     "order": html,
        #     "payment": self.__make_payment(order['data'])
        # }
        # return JsonResponse(data=response, status=200)

    def post(self, request, store_name, oid):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        try:
            service = self.service_class(request, store, oid)
        except OrderDoesNotExists:
            return HttpResponse(status=404)

        pid = request.POST.get('productId')
        product = get_object_or_404(Product, pk=pid)
        context = service.add_product_to_order(product)
        request.session.modified = True
        print(request.session['orders'])

        html = render_to_string(template_name='sales/product_item.html', context=context)
        response = {
            "eid": product.id,
            "order": html,
            "payment": service.make_payment()
        }
        return JsonResponse(response, status=200)

    def patch(self, request, store_name, oid):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        pid = request.PATCH.get('productId')
        quantity = float(request.PATCH.get('quantity'))
        try:
            service = self.service_class(request, store, oid)
            pdict = service.update_quantity_product_item(product_id=int(pid), quantity=quantity)
        except OrderDoesNotExists:
            return HttpResponse(status=404)
        except (ObjectDoesNotExist, SalesException) as e:
            response = {
                "status": "failed",
                "msg": str(e)
            }
            return JsonResponse(data=response, status=200)
        request.session.modified = True
        response = {
            "status": "success",
            "subtotal": int(pdict['quantity'] * pdict['product']['sell_price']),
            "payment": service.make_payment()
        }
        return JsonResponse(data=response, status=200)

    def delete(self, request, store_name, oid):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        try:
            service = self.service_class(request, store, oid)
        except OrderDoesNotExists:
            return HttpResponse(status=404)
        pid = request.DELETE.get('productId')
        order_data = service.remove_product_item(int(pid))
        request.session.modified = True
        html = render_to_string(template_name='sales/cart.html', context={'list_items': order_data})
        response = {
            "order": html,
            "payment": service.make_payment()
        }
        return JsonResponse(data=response, status=200)


class OrderCustomerView(LoginRequire, View):
    service_class = SalesManagement

    def patch(self, request, store_name, oid):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        try:
            service = self.service_class(request, store, oid)
        except OrderDoesNotExists:
            return HttpResponse(status=404)
        customer_id = request.PATCH.get("customerId")
        customer = get_object_or_404(Customer, pk=customer_id)
        service.add_customer_to_order(customer)
        request.session.modified = True
        response = {
            "id": customer.id,
            "name": customer.customer_name
        }
        return JsonResponse(data=response, status=200)

    def delete(self, request, store_name, oid):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        try:
            service = self.service_class(request, store, oid)
            service.remove_customer()
            request.session.modified = True
        except OrderDoesNotExists:
            return HttpResponse(status=404)
        return HttpResponse(status=200)


class PaymentView(LoginRequire, View):
    service_class = SalesManagement

    def get(self, request, iid):
        pass
        # context = {}
        # return render(request, template_name="sales/invoice.html", context=context)

    def post(self, request, store_name, iid):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        response = {
            "status": "failed"
        }
        try:
            service = self.service_class(request=request, store=store, oid=iid)
        except OrderDoesNotExists:
            return HttpResponse(status=404)

        try:
            invoice = service.pay_order()
        except SalesException as e:
            response["msg"] = str(e)
            return JsonResponse(data=response, status=200)

        request.session.modified = True
        response["status"] = "success"
        context = {
            "invoice": invoice,
            "list_product_items": invoice.order.get_list_product_items(),
            "customer": invoice.order.customer,
            "store": store
        }
        html = render_to_string(template_name="sales/invoice.html", context=context)
        response["data"] = html
        return JsonResponse(data=response, status=200)


class InvoiceListView(LoginRequire, View):
    service_class = TransactionManagement

    def get(self, request, store_name):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        table_columns = ['', 'Mã hoá đơn', 'Thời gian', 'Khách hàng', 'Giảm giá', 'Tổng hoá đơn']
        context = {
            "table_columns": table_columns,
            "active": "transactions",
            "store_name": store_name
        }
        return render(request, template_name="invoice/invoice.html", context=context)

    def post(self, request, store_name):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()
        service = self.service_class(request, store)
        response = service.get_invoices_datatables()
        return JsonResponse(response)


class InvoiceDetailUpdateView(LoginRequire, View):
    service_class = TransactionManagement
    template_name = "invoice/invoice_detail.html"

    def get(self, request, store_name, pk):
        """
        Get invoice detail
        """
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        invoice = get_object_or_404(Invoice, pk=pk)
        context = {
            "invoice": invoice,
            "store_name": store_name
        }
        return render(request, template_name=self.template_name, context=context)

    def patch(self, request, store_name, pk):
        """
        Method for updating invoice status
        """
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        new_status = int(request.PATCH["status"])
        self.service_class(request, store).change_invoice_status(pk, new_status)
        return HttpResponse(200)
