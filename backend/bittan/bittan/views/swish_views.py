import requests
from ..services.swish.swish import Swish
from django.http import HttpResponse
from ..settings import EnvVars, ENV_VAR_NAMES

def get_qr(request, token):
    """
    Fetches the QR code image from Swish and forwards it to the client.
    """
    qr_endpoint = EnvVars.get(ENV_VAR_NAMES.SWISH_QR_GENERATOR_ENDPOINT)
    data = {
            "format": "png",
            "size": "300",
            "token": token
    }

    response = requests.post(qr_endpoint, stream=True, json=data)

    # TODO error handling
    response.raise_for_status()
    return HttpResponse(response.content, content_type=response.headers.get('Content-Type', 'image/png'))
