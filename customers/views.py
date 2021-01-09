from django.http import HttpResponse, JsonResponse, Http404
from django.views import View

from core.views import LoginRequire
from customers.exceptions import FormInvalidException
from customers.forms import CustomerForm
from customers.services import CustomerManagement
from stores.exceptions import UserNotInStoreException
from stores.services import StoreManagement


class CustomerView(LoginRequire, View):
    form_class = CustomerForm
    template_name = "customer/customer_form.html"
    service_class = CustomerManagement

    def get(self, request):
        pass

    def post(self, request, store_name):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        service = self.service_class(request, store)
        response = {
            "status": "success"
        }
        try:
            instance = service.validate_form()
            response["data"] = {
                "id": instance.id,
                "name": instance.customer_name
            }
        except FormInvalidException:
            errors = service.get_errors()
            response["status"] = "failed"
            response["data"] = errors
            print(response)
        return JsonResponse(data=response, status=200)
