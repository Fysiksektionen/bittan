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

from bittan.views.swish_views import get_qr

from .api.swish import swish_callback, debug_make_request, debug_synchronize_request

from .views.views import get_chapterevents, reserve_ticket, start_payment, validate_ticket
from bittan.views.staffpage_views import create_tickets, filter_ticket_type_from_chapter_event, staff_dashboard, update_payment, update_tickets

urlpatterns = [
    path("admin/", admin.site.urls),
    path("swish/callback/", swish_callback),
	path("get_chapterevents/", get_chapterevents),
    path("validate_ticket/", validate_ticket),
    path("reserve_ticket/", reserve_ticket),
    path("start_payment/", start_payment),
    path("staff/", staff_dashboard, name="staff_dashboard"), 
    path("accounts/login/", django_views.LoginView.as_view(), name="login"),
    path("accounts/logout", django_views.LogoutView.as_view(), name="logout"),
    path("update_payment/<int:payment_id>/", update_payment, name="update_payment"),
    path("update_tickets/<int:payment_id>/", update_tickets, name="update_tickets"),
    path("create_tickets", create_tickets , name="create_tickets"),
    path("filter_ticket_type_by_chapter_event/<int:chapter_event_id>/", filter_ticket_type_from_chapter_event),
    path("generate_qr/<str:token>/", get_qr),
]


if environ.get("DEBUG") == "True":
	urlpatterns.append(path('swish/dummy/', debug_make_request))
	urlpatterns.append(path('swish/sync/', debug_synchronize_request))
