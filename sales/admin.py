from django.contrib import admin
from sales.models import Invoice, Order, ProductItem

admin.site.register(Invoice)
admin.site.register(Order)
admin.site.register(ProductItem)
