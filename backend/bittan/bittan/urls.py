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
from .api.swish import swish_callback, debug_make_request, debug_query, debug_synchronize_payment_request 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swish/callback/', swish_callback),
]


if environ.get("DEBUG") == "True":
	urlpatterns.append(path('swish/dummy/', debug_make_request))
	urlpatterns.append(path('swish/<slug:id>', debug_query))

# Initialize swish
from bittan.services.swish import Swish, example_callback_handler_function
url = f'https://mss.cpc.getswish.net/swish-cpcapi/'

callback_url = "https://f450c2c5f95141.lhr.life/swish/callback/" #https://4a57cf3089a623cd042c99d6a8767a70.serveo.net/swish/callback/"
# callback_url = "https://f450c2c5f95141.lhr.life https://jongaton.serveo.net/swish/callback/" #https://4a57cf3089a623cd042c99d6a8767a70.serveo.net/swish/callback/"
cert_file_paths = ("./test_certificates/testcert.pem", "./test_certificates/testcert.key")
swish = Swish(url, "1234679304", callback_url, cert_file_paths, example_callback_handler_function)
