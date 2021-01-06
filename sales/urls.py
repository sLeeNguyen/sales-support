from django.urls import path, re_path
from . import views

app_name = "sales"
urlpatterns = [
    re_path('^sales/$', views.SalesView.as_view(), name="sales"),
    re_path('^sales/search/', views.SearchView.as_view(), name="search"),
    re_path(r'^sales/order-session/((?P<oid>\d+)/)?$', views.OrderSessionView.as_view(), name="order-session"),
    path('sales/cart/<int:oid>/', views.CartView.as_view(), name="cart"),
    path('sales/payment/<int:iid>/', views.PaymentView.as_view(), name="payment"),
    re_path(r'^sales/order/((?P<oid>\d+)/)?$', views.OrderView.as_view(), name="order"),
    re_path(r'^invoices/$', views.InvoiceListView.as_view(), name="list-invoices"),
    path('invoices/invoice/<int:pk>/', views.InvoiceDetailUpdateView.as_view(), name="invoice"),
]
