from django.urls import re_path
from core import views


app_name = 'core'
urlpatterns = [
    re_path(r'^login/$', views.LoginView.as_view(), name='login'),
    re_path(r'^(?P<store_name>[a-zA-Z0-9]+)/dashboard/', views.DashBoardView.as_view(), name='dashboard')
]
