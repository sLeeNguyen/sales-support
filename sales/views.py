from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.template.loader import render_to_string
from django.views import View

from core.views import LoginRequire
from products.models import Product
from sales import services
from sales.exceptions import OrderDoesNotExists, SalesException
from sales.services import SalesManagement


class SalesView(LoginRequire, View):

    def get(self, request, *args, **kwargs):
        request.session['orders'] = [{'id': 1, 'data': []}]
        return render(request, template_name='sales/sales.html', context={'oid': 1})


class OrderSessionView(LoginRequire, View):
    service_class = SalesManagement

    def get(self, request, oid):
        oid = int(oid)
        try:
            service = self.service_class(request, oid)
        except OrderDoesNotExists:
            return HttpResponse(status=400)
        index, order = service.get_order_dict()
        context = {'oid': order['id'], 'list_items': order['data']}
        html = render_to_string(template_name='sales/cart.html', context=context)
        response = {
            "order": html,
            "payment": service.make_payment()
        }
        return JsonResponse(data=response, status=200)

    def post(self, request):
        orders = request.session['orders']
        list_oids = [o['id'] for o in orders]
        list_oids.sort()

        new_id = 1
        for x in list_oids:
            if x == new_id:
                new_id += 1
        orders.append({'id': new_id, 'data': []})
        response = {
            'oid': new_id,
        }
        request.session.modified = True
        return JsonResponse(data=response, status=200)

    def delete(self, request, oid):
        oid = int(oid)
        try:
            service = self.service_class(request, oid)
        except OrderDoesNotExists:
            return HttpResponse(status=400)
        service.remove_order_dict()
        request.session.modified = True
        return HttpResponse(status=200)


class OrderView(LoginRequire, View):
    service_class = SalesManagement

    def post(self, request, oid):
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


class SearchView(LoginRequire, View):
    def get(self, request):
        query = request.GET.get('q')
        products = services.search_products(query)
        html = render(request, template_name='sales/product_search_item.html', context={'data': products})
        return HttpResponse(html)


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

    def post(self, request, oid):
        try:
            service = self.service_class(request, oid)
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

    def patch(self, request, oid):
        pid = request.PATCH.get('productId')
        quantity = float(request.PATCH.get('quantity'))
        try:
            service = self.service_class(request, oid)
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

    def delete(self, request, oid):
        try:
            service = self.service_class(request, oid)
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


class InvoiceView(LoginRequire, View):
    service_class = SalesManagement

    def get(self, request, iid):
        context = {}
        return render(request, template_name="sales/invoice.html", context=context)

    def post(self, request, iid):
        response = {
            "status": "failed"
        }
        try:
            service = self.service_class(request=request, oid=iid)
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
        }
        html = render_to_string(template_name="sales/invoice.html", context=context)
        response["data"] = html
        return JsonResponse(data=response, status=200)
