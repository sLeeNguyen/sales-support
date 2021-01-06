from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from business.services import ReportManagement


class DashboardReportView(View):
    service_class = ReportManagement

    def get(self, request):
        service = self.service_class(request)
        data_report = service.get_data_aggregations()
        return JsonResponse(data=data_report, status=200)
