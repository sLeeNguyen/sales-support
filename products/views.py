import json

from django.shortcuts import render, HttpResponse
from django.views import View

from core.views import LoginRequire
from products.models import Product
from products.services import ProductServices


class ProductView(LoginRequire, View):
    def get(self, request):
        table_columns = ['Mã sản phẩm', 'Tên sản phẩm', 'Giá bán', 'Giá vốn', 'Tồn kho']
        context = {'table_columns': table_columns, }
        return render(request, template_name='product/products.html', context=context)

    def post(self, request):
        """
        Handle operations sorting, paging, getting of datatables.
        Return json response to datatables
        """
        # get products
        query_set = ProductServices.get_products_datatables(request.POST)

        # make response
        data = []
        for p in query_set:
            if p.unit == Product.UNIT_INT:
                available = int(p.available)
            else:
                available = p.available
            data.append({
                "0": p.product_code,
                "1": p.product_name,
                "2": p.sell_price,
                "3": p.cost_price,
                "4": available,
                "DT_RowId": p.id
            })

        response = {
            "draw": int(request.POST['draw']),
            "recordsTotal": query_set.count(),
            "recordsFiltered": query_set.count(),
            "data": data
        }
        print(json.dumps(response))
        return HttpResponse(json.dumps(response))
