from django.urls import re_path, path
from products import views


app_name = 'products'
urlpatterns = [
    re_path(r'^warehouse/$', views.ProductListView.as_view(), name='warehouse'),
    re_path(r'^product/create/$', views.ProductCreationView.as_view(), name='product-creation'),
    re_path(r'^product/detail/((?P<pk>\d+)/?)?$', views.ProductDetailView.as_view(), name='product-detail'),
    re_path(r'^product/update/((?P<pk>\d+)/?)?$', views.ProductUpdateView.as_view(),
            name='product-update'),
    re_path(r'^delete/((?P<pk>\d+)/?)?$', views.ProductDeleteView.as_view(), name='product-delete'),
]
