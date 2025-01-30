from rest_framework import status 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from ..services.swish.swish import Swish 

@api_view(['POST'])
def swish_callback(request: Request):
	# TODO For somereason the swish callback is not working and not sending any data at all. So this is a "temporary" fix.
	if request.data == {}:
		# TODO Make this an async job and not execute like this... 
		Swish.get_instance().synchronize_all_pending()
	else:
		Swish.get_instance().handle_swish_callback(request.data)

	# Swish expects a 201 when a callback is sucessfully recieved
	return Response("", status=status.HTTP_201_CREATED)

@api_view(['POST'])
def debug_synchronize_request(request: Request):
	Swish.get_instance().synchronize_all_pending()

	return Response("Wow")
@api_view(['POST'])
def debug_make_request(request: Request):
	# In merchant simulator, specify the msg query param to make the merchant simulator return an error.
	# eg. POST <BACEND_URI>/swish/dummy/?msg=RF07 ==> simulate that the user declined the transaction 
	msg = ""
	if 'msg' in request.query_params:
		msg = request.query_params['msg']

	resp = Swish.get_instance().create_swish_payment(123, msg)
	print("Skapade betalning")
	print(f'id: {resp.id}, token: {resp.token}')
	return Response(f"{resp.token}", status=status.HTTP_201_CREATED)

@api_view(['POST'])
def debug_query(request: Request, id):
	resp = Swish.get_instance().get_payment_request(id)
	print(resp)
	print(f'id: {resp.id}, token?: {resp.token or ''}, status: {resp.status}')
	return Response("Letade lite i databasen", status=status.HTTP_200_OK)
