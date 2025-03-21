function sendMassEmail(chapter_event_id) {
    const csrf = document.querySelector('meta[name="csrf-token"]').content
    const email_content = document.getElementById("email-content").value
    const email_subject = document.getElementById("mass-email-subject").value
    axios.post(
        window.url_prefix + "staff/send_mass_mail",
        {
            "chapter_event_id": chapter_event_id,
            "email_subject": email_subject,
            "email_content": email_content
        },
        {
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf
            }
        })
        .then(response => {
            if (response.data.success) {
                alert("Mass email sent successfully");
            } else {
                alert(`Error sending mass email. Error message: ${response.data.errors}`);
            }
        }
        ).catch(error => {
            console.error("Error sending the emails:", error);
            alert(`Error sending mass email. Error message: ${response.data.errors}`);
        }
    )
}

function resendEmail(paymentId) {
    const csrf = document.querySelector('meta[name="csrf-token"]').content
    axios.post(
        window.url_prefix + "staff/resend_email",
        {"paymentId": paymentId},
        {
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf
            }
        })
        .then(response => {
            if (response.data.success) {
                alert("Mail sent successfully");
            } else {
                alert(`error creating tickets. error message: ${response.data.errors}`);
            }
        }
        ).catch(error => {
            console.error("Error resending the email:", error);
            alert(`error creating tickets. error message: ${response.data.errors}`);
        }
    )
}

function calculateTotalPrice() {
    const ticketRows = document.querySelectorAll("#ticket-form table tr");
    let totalPrice = 0;
    ticketRows.forEach(row => {
        const count_element = row.querySelector("input[type=number]");
        const price_element = row.querySelector("input[type=hidden]");
        if (count_element && price_element) {
            totalPrice += (count_element.valueAsNumber || 0) * (parseInt(price_element.value) || 0);
        }
    })
    document.getElementById('total-price').value = totalPrice;
}

document.addEventListener('DOMContentLoaded', function() {
    window.url_prefix = document.querySelector('meta[name="url_prefix"]').content

    const chapterEventSelect = document.querySelector('#ticket-creation-chapter-event-form select[name="chapter_event"]');;
    const ticketFormContainer = document.getElementById('ticket-form-container');


    chapterEventSelect.addEventListener('change', function() {
        const chapterEventId = chapterEventSelect.value;
        const csrf = ticketFormContainer.querySelector('input[name="csrfmiddlewaretoken"]').outerHTML
        if (!chapterEventId) {
            ticketFormContainer.innerHTML = `<form id="ticket-form">${csrf}</form>`
            return
        }
        axios.get(window.url_prefix + `staff/filter_ticket_type_by_chapter_event/${chapterEventId}/`)
            .then(response => {
                const ticketTypes = response.data.ticket_types;
                let formHtml = '<table>';
                ticketTypes.forEach(ticketType => {
                    formHtml += `<tr><td>${ticketType.title}</td><td><input type="number" name="ticket_type_${ticketType.id}" min="0" required oninput="calculateTotalPrice()" value="0"></td>`;
                    formHtml += `<td><input type="hidden" name="ticket_type_${ticketType.id}_price" value="${ticketType.price}"></td></tr>`;
                });
                formHtml += '<tr><td>Total Price</td><td><input type="text" id="total-price" readonly></td></tr>';
                formHtml += '<tr><td>Email Address</td><td><input type="email" name="email" required></td></tr>';
                formHtml += '<tr><td><input type="checkbox" name="ignore_seat_limit"></td><td>Ignore limit in total seat count</td></tr>'
                formHtml += '<tr><td><input type="checkbox" name="send_receipt"></td><td>Send receipt</td></tr>'
                formHtml += '</table><button type="submit">Create Tickets</button>';
                ticketFormContainer.innerHTML = `<form id="ticket-form">${csrf}${formHtml}</form>`;
            })
            .catch(error => {
                console.error('Error fetching ticket types:', error);
            });
    });

    ticketFormContainer.addEventListener("submit", function(event) {
        event.preventDefault();
        const formData = new FormData(document.getElementById("ticket-form"));
        formData.append("chapter_event", document.querySelector('#ticket-creation-chapter-event-form select[name="chapter_event"]').value)
        axios.post(window.url_prefix + "staff/create_tickets", formData)
            .then(response => {
                alert(`Tickets created successfully: Created payment with reference ${response.data}`);
            })
            .catch(error => {
                if (error.response) {
                    alert(`Error creating tickets. Validation errors: ${error.response.data.non_field_errors[0]}`);
                } else {
                    alert("Error setting up the request.");
                }
            });
    });

    const emailContent = document.getElementById("email-content")
    const emailPreview = document.getElementById("email-preview")

    emailContent.addEventListener("input", function(){
        emailPreview.innerHTML = emailContent.value
    })
});
