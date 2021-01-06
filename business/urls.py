from django.urls import re_path, path
from business import views


app_name = 'business'
urlpatterns = [
    re_path(r'^analysis/dashboard/$', views.DashboardReportView.as_view(), name="dash-report")
]
