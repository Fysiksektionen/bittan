#!/bin/bash

curl --cookie-jar cookies.utf8 -v POST localhost:8000/reserve-ticket/ \
	--header "Content-Type:application/json" \
	--data '{
		"chapter_event": "1",
		"tickets": 
		[
			{
				"ticket_type": "Studentbiljett",
				"count": 1
			},
			{
				"ticket_type": "Standardbiljett",
				"count": 1
			}
		]
	}'
