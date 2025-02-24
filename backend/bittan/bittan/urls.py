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

from bittan.views.swish_views import get_qr
from bittan.settings import get_bittan_backend_url_path_prefix

from .api.swish import debug_cancel, swish_callback, debug_make_request, debug_synchronize_request

from .views.views import get_chapterevents, reserve_ticket, start_payment, validate_ticket, get_session_payment_status

_prefix = get_bittan_backend_url_path_prefix()

urlpatterns = [
    path(_prefix+'admin/', admin.site.urls),
    path(_prefix+'swish/callback/', swish_callback),
	path(_prefix+'get_chapterevents/', get_chapterevents),
    path(_prefix+'validate_ticket/', validate_ticket),
    path(_prefix+"reserve_ticket/", reserve_ticket),
    path(_prefix+'session_payment_status/', get_session_payment_status),
    path(_prefix+"start_payment/", start_payment),
    path(_prefix+"generate_qr/<str:token>", get_qr),
]


if environ.get("DEBUG") == "True":
	urlpatterns.append(path(_prefix+'swish/dummy/', debug_make_request))
	urlpatterns.append(path(_prefix+'swish/cancel/<str:pk>/', debug_cancel))
	urlpatterns.append(path(_prefix+'swish/sync/', debug_synchronize_request))
