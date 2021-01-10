from django.contrib.auth.models import Group
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.http import JsonResponse

from stores.models import Store
from stores.services import StoreManagement
from users.models import User


class StoreView(View):
    template_name = "store/store.html"
    service_class = StoreManagement

    def get(self, request):
        return render(request=request, template_name=self.template_name)

    def post(self, request):
        firstname = request.POST.get("fname")
        lastname = request.POST.get("lname")
        phone = request.POST.get("phone")
        # email = request.POST.get("email")
        store_name = request.POST.get("storeName")
        username = request.POST.get("username")
        password = request.POST.get("password")
        response = {
            "status": "failed"
        }
        if self.service_class.check_store_by_name(store_name):
            response["msg"] = "Tên cửa hàng đã được sử dụng"
        elif User.objects.filter(username=username).exists():
            response["msg"] = "Tên tài khoản dã được sử dụng"
        else:
            response["status"] = "success"
            store = Store.objects.create(store_name=store_name)
            user = User.objects.create_user(username=username, password=password,
                                            first_name=firstname, last_name=lastname,
                                            phone_number=phone, store=store)
            manager = Group.objects.get(name="manager")
            user.groups.add(manager)
        return JsonResponse(data=response, status=200)


def check_store_name(request, store_name):
    if StoreManagement.check_store_by_name(store_name):
        response = {
            "status": "success",
            "url": reverse("core:login"),
            "store_name": store_name
        }
    else:
        response = {
            "status": "failed",
            "msg": "Cửa hàng không tồn tại"
        }
    return JsonResponse(data=response, status=200)
