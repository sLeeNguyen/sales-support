from django.utils.translation import gettext_lazy as _
from products.models import Product, Category
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


fields = ['product_code', 'product_name', 'sell_price', 'cost_price', 'available']


class ProductServices:

    @classmethod
    def get_products_datatables(cls, post):
        """
        Get list products from database base on properties in POST request
        """
        start = int(post['start'])
        end = start + int(post['length'])
        field_order = fields[int(post['order[0][column]']) - 1]
        order_type = post['order[0][dir]']
        search_val = post['search[value]']
        product_status = int(post.get('productStatus', 1))

        results = Product.objects.filter(status=product_status)
        if search_val:
            results = results.filter(
                Q(product_code__icontains=search_val) | Q(product_name__icontains=search_val)
            )
        if order_type == 'asc':
            results = results.order_by(field_order)
        else:  # order_type = 'desc'
            results = results.order_by('-' + field_order)

        # make response
        data = []
        for p in results[start:end]:
            if p.unit == Product.UNIT_INT:
                available = int(p.available)
            else:
                available = p.available
            data.append({
                "0": "",
                "1": p.product_code,
                "2": p.product_name,
                "3": p.sell_price,
                "4": p.cost_price,
                "5": available,
                "DT_RowId": p.id
            })

        return {
            "draw": int(post['draw']),
            "recordsTotal": results.count(),
            "recordsFiltered": results.count(),
            "data": data
        }
