from django.contrib import admin
from products.models import Product, Category
from products.forms import ProductForm


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['id', 'product_code', 'product_name', 'status']


admin.site.register(Category)
