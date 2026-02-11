# Backend endpoints

- [/get_chapterevents/](#get-chapterevents)
- [/get_session/](#get-session)
- [/reserve_ticket/](#reserve-ticket)
- [/session_payment_status/](#session-payment-status)
- [/start_payment/](#start-payment)
- [/validate_ticket/](#validate-ticket)

## Get chapterevents

`GET /get_chapterevents/`

Retrieves all chapterevents where `sales_stop_at` has not been surpassed. Also retrieves all visible tickettypes that appear among the returned chapterevents. These are organized as `{"chapter_events": [...], "ticket_types": [...]}`.

Example of response content:
```json
{
    "chapter_events": [
        {
            "id": 1,
            "title": "Fysikalen Dag 1",
            "description": "Första dagen av Fysikalen.",
            "event_at": "2025-12-05T18:49:12.677086+01:00",
            "max_tickets_per_payment": 8,
            "sales_stop_at": "2025-12-05T18:49:12.677086+01:00",
            "ticket_types": [
                1,
                2
            ]
        },
        {
            "id": 2,
            "title": "Fysikalen Dag 2",
            "description": "Andra dagen av Fysikalen.",
            "event_at": "2025-12-06T18:49:12.677086+01:00",
            "max_tickets_per_payment": 8,
            "sales_stop_at": "2025-12-05T18:49:12.677086+01:00",
            "ticket_types": [
                1,
                2
            ]
        }
    ],
    "ticket_types": [
        {
            "id": 1,
            "price": "199",
            "title": "Standardbiljett",
            "description": "En vanlig biljett."
        },
        {
            "id": 2,
            "price": "99",
            "title": "Studentbiljett",
            "description": "En billigare biljett."
        }
    ]
}
```
## Get session

`GET /get_session/<payment_id>`

Retrieves the data of a session. Retrieves the associated tickets, payment status, and if there is a form attached to the event, the answers to the form. 
The tickets list consits of objects with a corresponding ticket type as well as the number of tickets of this type that is associated with the session. 
The answers list contains answer to the chapter event's associated form if there exists one. Each object in this list contains the question id, 
a list with the selected options, as welll as a list with the texts asscioated with the option. The texts are linked to their corresponding option 
by having mathing indicies in their respective list. The answers array is only attached if there exists a form for the event.  

Example of response content:
```json
{
    "status": "FORM_SUBMITTED",
    "tickets": [
        {
            "ticket_type": 1,
            "count": 1
        }
    ],
    "answers": [
        {
            "question": 1,
            "options": [
                1
            ],
            "texts": [
                "Wohohoh"
            ]
        },
        {
            "question": 2,
            "options": [
                2,
                3,
                4
            ],
            "texts": [
                "",
                "",
                "Allt"
            ]
        },
        {
            "question": 3,
            "options": [
                5
            ],
            "texts": [
                ""
            ]
        },
        {
            "question": 4,
            "options": [
                7,
                8
            ],
            "texts": [
                "",
                ""
            ]
        }
    ]
}
```
## Reserve ticket

`POST /reserve_ticket/`

Reserves ticket for later payment. 

### Request body
* `chapter_event` `string` *Required*</span> <br>
    The id of the chapter event tickets are being booked for. 
* `email_address` `string` *Required* <br>
    The email address of the one booking the tickets. 

* `tickets` `Array<Object>` *Required* <br>
    A list of objects that contains information about the ticket type to reserve as well as how many of each ticket type to reserve. 
    * `ticket_type` `string` *Required* <br>
        The id of the ticket type to reserve.
    * `count` `int` *Required* <br>
        How many of the ticket type to reserve. Minimum value is $1$. 

### Response
A string containing the session id of the current ticket booking session. 

### Response codes 

|Response code|Data|
|---------:|:---------------|
|201 CREATED|Reservation of tickets are successful. Receives a session cookie that is used to access the tickets. |
|400 BAD REQUEST|`"InvalidRequestData"`|
|403 FORBIDDEN|`"TooManyTickets"`|
| |`{"error": "OutOfTickets", "tickets_left": int}`|
|404 NOT FOUND|`"EventDoesNotExist"`|
| | `"TicketTypeDoesNotExist"`|
|500 INTERNAL SERVER ERROR|There is an error on the server. Check the logs.|

### Example request

Request using curl.
```bash
curl -v POST <Your URL>/reserve_ticket/ \
        --header "Content-Type:application/json" \
        --data '{
                "chapter_event": "<Event_Id>",
                "email_address": "<Email address>",
                "tickets":
                [
                        {
                                "ticket_type": "<Ticket Type1>",
                                "count": <Count1>
                        },
                        {
                                "ticket_type": "<Ticket Type2>",
                                "count": <Count2>
                        }
                ]
        }'
```
Example response
```bash
"hRcAKTANoOWQ"
```
Reserves tickets to the event with event_id. Reserves Count1 of Type1 tickets and Count2 of Type2 tickets. Returns the session id which is used to interact with the payment in the future.


## Start payment

`POST /start_payment/`

Starts the swish payment process. 


### Request body
* `session_id` `string` *Required*</span> <br>
    The session id of the payment to start. 

### Response
If successful a swish token is sent. This token is used to interact with the users swish app. 

### Response codes 

|Response code|Data|
|---------:|:---------------|
|200 OK|`string`|
|400 BAD REQUEST|`"InvalidRequestData"`|
| |`"InvalidSession"`|
|403 FORBIDDEN|`"AlreadyPaidPayment"`|
|408 Request timeout|`"SessionExpired"`|
|500 INTERNAL SERVER ERROR|There is an error with the server. Check the logs.|

### Example request
Request using curl.  
```bash
curl -v --cookie cookies.utf8 <Your URL>/start-payment/ \
        --header "Content-Type:application/json" \
        --data '{
                "session_id": "Session Id"
        }'
```
Response
```bash
< HTTP/1.1 200 OK
< Date: Sat, 29 Jun 2024 08:20:29 GMT
< Server: WSGIServer/0.2 CPython/3.12.3
< Content-Type: application/json
< Vary: Accept, Cookie
< Allow: POST, OPTIONS
< X-Frame-Options: DENY
< Content-Length: 34
< X-Content-Type-Options: nosniff
< Referrer-Policy: same-origin
< Cross-Origin-Opener-Policy: same-origin
<
* Connection #0 to host localhost left intact
"e2ce062d69294373838e65f6e5d24b1c"
```
Starts a swish payment and returns the Swish token. 

## Validate ticket

`PUT /validate_ticket/`

Determines a tickets validity. 

### Request body

* `external_id` `string` *Required* <br>
    The external id of the ticket to validate. 
* `password` `string` *Required* <br>
    The password to the scanner. Send as a string, itis very safe. I promise.
* `use_ticket` `bool` *Required* <br>
    Boolean value that determines if theticket should be used or not. 

|Response code|Data|
|---------:|:---------------|
|200 OK|Ticket was validated successfully and a response with information about the tickets validity is received. See example response for an example of valid response data.|
|400 BAD_REQUEST|`"InvalidRequestData"`|
|401 UNAUTHORIZED|`"Incorrect password"`|
|404 NOT_FOUND|`{"times_used": -1, "status": "Ticket does not exist"}`|

Example of valid response content:
```json
{
  "external_id": "AAAAAA"
  "times_used": 1,
  "chapter_event": "Fysikalen dag 1",
  "status": "PAID"
}
```
