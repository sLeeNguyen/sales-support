from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect, Http404
from django.views import View
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from users.services import (
    user_authentication, AccountIsBlockedError, AccountNotExistsError
)


class LoginRequire(LoginRequiredMixin):
    login_url = '/login/'


class LoginView(View):
    def get(self, request):
        """
        Show login view.
        Change action in core/login.html rely on 'next' context
        """
        redirect_to = request.GET.get('next', '')
        return render(request, template_name='core/login.html', context={'next': redirect_to})

    def post(self, request):
        """
        Authenticate username and password.
        Redirect to other view if url has <QueryDict: {'next': ['...']}>
        """

        error_msg = ''
        redirect_to = ''
        try:
            username = request.POST['username']
            password = request.POST['password']

            user = user_authentication(username=username, password=password)
            login(request, user)
            if request.GET:
                redirect_to = request.GET.get('next', '')
            if redirect_to:
                return HttpResponseRedirect(redirect_to=redirect_to)
            else:
                return HttpResponseRedirect(reverse("core:dashboard"))
        except MultiValueDictKeyError as e:
            error_msg = str(e)
        except AccountNotExistsError as e:
            error_msg = str(e)
        except AccountIsBlockedError as e:
            error_msg = str(e)

        context = {
            'error_msg': error_msg,
            'username': username,
            'next': redirect_to,
        }
        return render(request, template_name='core/login.html', context=context)


class DashBoardView(LoginRequire, View):
    """
    Show dashboard view with template dashboard.html
    Require user logged in successfully
    """
    def get(self, request):
        context = {
            'active': 'dashboard'
        }
        return render(request, template_name='core/dashboard.html', context=context)
