from django.urls import path, re_path
from . import views

app_name = "sales"
urlpatterns = [
    path('', views.SalesView.as_view(), name="sales"),
    path('search/', views.SearchView.as_view(), name="search"),
    re_path(r'order-session/((?P<oid>\d+)/)?', views.OrderSessionView.as_view(), name="order-session"),
    path('cart/<int:oid>/', views.CartView.as_view(), name="cart"),
    path('invoice/<int:iid>/', views.InvoiceView.as_view(), name="invoice"),
    re_path(r'order/((?P<oid>\d+)/)?', views.OrderView.as_view(), name="order"),
]
