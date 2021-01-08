from calendar import mdays

from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect, Http404
from django.views import View
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone

from core.utils import client_timezone
from elasticsearch_client import es as elasticsearch
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
        today = client_timezone(timezone.now())
        yesterday = today - timezone.timedelta(days=1)
        last_month = today - timezone.timedelta(days=mdays[today.month])
        analysis = elasticsearch.aggregate_sales_today(today=today.strftime("%Y-%m-%d"),
                                                       today_begin=today.strftime("%Y-%m-01"),
                                                       yesterday=yesterday.strftime("%Y-%m-%d"),
                                                       last_month_begin=last_month.strftime("%Y-%m-01"),
                                                       last_month=last_month.strftime("%Y-%m-%d"))
        data_response = {
            "today": analysis["today"]
        }
        if analysis["today"]["total_invoices"] > 0 and analysis["yesterday"]["total_invoices"] > 0:
            revenue_today = analysis["today"]["revenue"]
            revenue_yesterday = analysis["yesterday"]["revenue"]
            compare_revenue_with_yesterday = (revenue_today - revenue_yesterday) / revenue_yesterday * 100
            data_response["compare_with_yesterday"] = round(compare_revenue_with_yesterday, 2)
        if analysis["lastmonth"]["total_invoices"] > 0:
            revenue_last_month = analysis["lastmonth"]["revenue"]
            revenue_this_month = analysis["now"]["revenue"]
            print(revenue_last_month)
            print(revenue_this_month)
            compare_revenue_with_last_month = (revenue_this_month - revenue_last_month) / revenue_last_month * 100
            data_response["compare_with_lastmonth"] = round(compare_revenue_with_last_month, 2)

        context = {
            'active': 'dashboard',
        }
        context.update(data_response)
        return render(request, template_name='core/dashboard.html', context=context)
