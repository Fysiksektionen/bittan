import requests


def get_ngrok_endpoint():
	print(requests.get('http://localhost:4040/api/tunnels').json()['tunnels'][0]['public_url'])
	# requests.get('http://localhost:4040/api/tunnels').json()['tunnels'][0]['public_url']

print(get_ngrok_endpoint())