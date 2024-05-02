from os import environ
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
from django.contrib import admin
from django.urls import path
from .api.swish import swish_callback, debug_make_request, debug_query 

from .views import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("reserve-ticket/", views.reserve_ticket),
    path("start-payment/", views.start_payment),
    path('swish/callback/', swish_callback),
]


if environ.get("DEBUG") == "True":
	urlpatterns.append(path('swish/dummy/', debug_make_request))
	urlpatterns.append(path('swish/<slug:id>', debug_query))


# Initialize swish
from bittan.services.swish import Swish, example_callback_handler_function
url = f'https://mss.cpc.getswish.net/swish-cpcapi/'

callback_url = "https://bb89-2001-6b0-1-1041-9825-49e0-597b-5858.ngrok-free.app/swish/callback/"
cert_file_paths = ("./test_certificates/testcert.pem", "./test_certificates/testcert.key")
swish = Swish(url, "1234679304", callback_url, cert_file_paths, example_callback_handler_function)
