from django.shortcuts import render, HttpResponse
from django.views import View
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth import authenticate


class LoginView(View):
    def get(self, request):
        return render(request, template_name='core/login.html')

    def post(self, request):
        try:
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                return HttpResponse("Hello %s" % (username,))
            else:
                return HttpResponse("Login fail!")

        except MultiValueDictKeyError as e:
            return HttpResponse("POST request has no attribute named '%s'" % e.__str__())