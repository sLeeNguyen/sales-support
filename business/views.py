from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.views import View

from business.services import ReportManagement
from stores.services import StoreManagement


class DashboardReportView(View):
    service_class = ReportManagement

    def get(self, request, store_name):
        store = StoreManagement.check_store_by_name(store_name)
        if store is None:
            raise Http404()
        service = self.service_class(request, store)
        data_report = service.get_data_aggregations()
        return JsonResponse(data=data_report, status=200)
