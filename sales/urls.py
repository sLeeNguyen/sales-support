from django.urls import path, re_path
from . import views

app_name = "sales"
urlpatterns = [
    path('', views.SalesView.as_view(), name="sales"),
    path('search/', views.SearchView.as_view(), name="search"),
    path('cart/<int:id>/', views.CardView.as_view(), name="cart"),
]
