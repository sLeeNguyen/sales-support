from django.urls import path, re_path

from customers import views


app_name = "customers"
urlpatterns = [
    re_path(r'^$', views.CustomerView.as_view(), name="customer")
]
