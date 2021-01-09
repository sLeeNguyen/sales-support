from django.urls import path, re_path

from stores import views


app_name = "stores"
urlpatterns = [
    re_path('^$', views.StoreView.as_view(), name="store"),
    path('<str:store_name>/', views.check_store_name, name="check_store"),
]
