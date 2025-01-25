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
from django.urls import path

from .api.swish import swish_callback, debug_make_request, debug_synchronize_request

from .views.views import get_chapterevents, reserve_ticket, start_payment, validate_ticket

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swish/callback/', swish_callback),
	path('get_chapterevents/', get_chapterevents),
    path('validate_ticket/', validate_ticket),
    path("reserve_ticket/", reserve_ticket),
    path("start_payment/", start_payment),
]


if environ.get("DEBUG") == "True":
	urlpatterns.append(path('swish/dummy/', debug_make_request))
	urlpatterns.append(path('swish/sync/', debug_synchronize_request))
