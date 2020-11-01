from django.urls import re_path, path
from products import views


app_name = 'products'
urlpatterns = [
    re_path('^warehouse/', views.ProductView.as_view(), name='warehouse'),
    # re_path('^')
]