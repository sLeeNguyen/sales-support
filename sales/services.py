from django.db.models import Q

from products.models import Product


def search_products(search_val):
    products = Product.objects.filter(Q(product_code__icontains=search_val) | Q(product_name__icontains=search_val))
    return products
