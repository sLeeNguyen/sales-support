from django.shortcuts import render, HttpResponse, get_object_or_404
from django.views import View

from products.models import Product
from sales import services


class SalesView(View):
    def get(self, request, *args, **kwargs):
        request.session['orders'] = [[]]
        return render(request, template_name='sales/sales.html')


class SearchView(View):
    def get(self, request):
        query = request.GET.get('q')
        products = services.search_products(query)
        html = render(request, template_name='sales/product_search_item.html', context={'data': products})
        return HttpResponse(html)


class CardView(View):
    def get(self, request, id):
        order = request.session['orders'][id]
        return render(request, template_name='sales/cart.html', context={'list_items': order})

    def post(self, request, id):
        pid = request.POST.get('productId')
        order = request.session['orders'][id]
        product = get_object_or_404(Product, pk=pid)
        order.append({'product': product.to_dict(), 'quantity': 1})
        request.session[id] = order
        context = order[-1]
        context['index'] = len(order)
        return render(request, template_name='sales/product_item.html', context=context)
