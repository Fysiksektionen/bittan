"""
URL configuration for bittan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from os import environ
from django.contrib import admin
from django.contrib.auth import views as django_views
from django.urls import path

from .api.swish import swish_callback, debug_make_request 

from .views.views import get_chapterevents, reserve_ticket, start_payment, validate_ticket
from bittan.views.staffpage_views import staff_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swish/callback/', swish_callback),
	path('get_chapterevents/', get_chapterevents),
    path('validate_ticket/', validate_ticket),
    path("reserve_ticket/", reserve_ticket),
    path("start_payment/", start_payment),
    path("staff/", staff_dashboard, name="staff_dashboard"), 
    path("accounts/login/", django_views.LoginView.as_view(), name="login"),
    path("accounts/logout", django_views.LogoutView.as_view(), name="logout"),

]


if environ.get("DEBUG") == "True":
	urlpatterns.append(path('swish/dummy/', debug_make_request))
