#!/bin/bash

curl -v --cookie cookies.utf8 localhost:8000/start-payment/ \
	--header "Content-Type:application/json" \
	--data '{
		"email_address": "test@mail.com"
	}'
	
