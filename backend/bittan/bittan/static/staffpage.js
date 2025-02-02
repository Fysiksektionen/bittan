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
    const chapterEventSelect = document.querySelector('#ticket-creation-chapter-event-form select[name="chapter_event"]');;
    const ticketFormContainer = document.getElementById('ticket-form-container');

    chapterEventSelect.addEventListener('change', function() {
        const chapterEventId = chapterEventSelect.value;
        const csrf = ticketFormContainer.querySelector('input[name="csrfmiddlewaretoken"]').outerHTML
        if (!chapterEventId) {
            ticketFormContainer.innerHTML = `<form id="ticket-form">${csrf}</form>`
            return
        }
        axios.get(`/filter_ticket_type_by_chapter_event/${chapterEventId}/`)
            .then(response => {
                const ticketTypes = response.data.ticket_types;
                let formHtml = '<table>';
                ticketTypes.forEach(ticketType => {
                    formHtml += `<tr><td>${ticketType.title}</td><td><input type="number" name="ticket_type_${ticketType.id}" min="0" required oninput="calculateTotalPrice()" value="0"></td>`;
                    formHtml += `<td><input type="hidden" name="ticket_type_${ticketType.id}_price" value="${ticketType.price}"></td></tr>`;
                });
                formHtml += '<tr><td>Total Price</td><td><input type="text" id="total-price" readonly></td></tr>';
                formHtml += '<tr><td>Email Address</td><td><input type="email" name="email" required></td></tr>';
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
        axios.post("/create_tickets", formData)
            .then(response => {
                if (response.data.success) {
                    alert(`Tickets created successfully: created payment with reference ${response.data.payment_reference}`);
                } else {
                    console.log(response.data.errors)
                    alert(`Error creating tickets. Error message: ${response.data.errors}`);
                }
            })
            .catch(error => {
                console.error("Error creating tickets:", error);
            });
    });
});
