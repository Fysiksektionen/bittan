from uuid import uuid4
from bittan.services.swish import Swish, example_callback_handler_function
import requests

url = f'https://mss.cpc.getswish.net/swish-cpcapi/api/v2/paymentrequests'
callback_url = "https://cab4-2001-6b0-1-1041-9825-49e0-597b-5858.ngrok-free.app/swish/callback"
cert_file_paths = ("./test_certificates/testcert.pem", "./test_certificates/testcert.key")

swish = Swish(url, "1234679304", callback_url, cert_file_paths, example_callback_handler_function)
# swish.create_swish_payment(Swish.generate_swish_id(), 123,  "RF07")
swish.create_swish_payment(Swish.generate_swish_id(), 123)

# instance = swish.get_instance()
# print(instance)


# payload = { 
# 		'payeeAlias': "1234679304",
# 		'amount': "123",
# 		'currency': "SEK",
# 		'callbackUrl': callback_url,
# 		'message': "Hello world",
# }

# a = str(uuid4()).replace('-', '').upper()
# print(a)


# resp = requests.put(url, json={"payeeAlias": "1234679304", "amount": 123, "callbackUrl": callback_url, "currency": "SEK" }, cert=("./testcert.pem", "./testcert.key"))
# print(resp)
# print(resp.headers)

# try:
# 	print(resp.json())
# except:
# 	print("No json things :(")