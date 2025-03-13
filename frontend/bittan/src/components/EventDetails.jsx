import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axiosInstance from "../api/axiosConfig";
import { reserveTicket } from "../api/reserveTicket"; // Separate API file for reserve tickets
import Payment from "./Payment"; // Import the Payment component

import "./EventDetails.css"

const EventDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [totalAmount, setTotalAmount] = useState(0);
  const [email, setEmail] = useState("");
  const [confirmEmail, setConfirmEmail] = useState("")

  useEffect(() => {
    // Fetch event details
    axiosInstance.get(`/get_chapterevents?format=json`).then((response) => {
      const event = response.data.chapter_events.find((event) => event.id == id);
      setEvent(event);

      const ticket_types = response.data.ticket_types;
          
      const filteredTickets = ticket_types.filter((type) =>
        event.ticket_types.includes(type.id) // Match by ID
      );
      // Initialize tickets selection
      
      setTickets(
        filteredTickets.map((type) => ({
          ticket_type: type.id, // Use the ticket type ID for API consistency
          title: type.title,
          price: type.price,
          count: 0,
        }))
      );
    });
  }, [id]);

  const handleTicketChange = (ticketTypeId, action) => {
    const newTickets = tickets.map((ticket) => {
      if (ticket.ticket_type === ticketTypeId) {
        return {
          ...ticket,
          count:
            action === "increment"
              ? ticket.count + 1
              : ticket.count > 0
              ? ticket.count - 1
              : 0,
        };
      }
      return ticket;
    });
    setTickets(newTickets);

    // Update total amount
    const total = newTickets.reduce(
      (sum, ticket) => sum + ticket.count * ticket.price,
      0
    );

    setTotalAmount(total);
  };

  const handleReserve = async () => {
    try {

      if (email !== confirmEmail) throw "mail"

      var chosenTickets = tickets
      .filter((t) => t.count > 0) // Only include tickets with count > 0
      .map((t) => ({
        ticket_type: t.ticket_type, // Use the ticket type ID
        count: t.count,
        price: t.price,
        title: t.title
      }))

      if (chosenTickets.length === 0) throw "no tickets"

      // Prepare request body
      const requestBody = {
        chapter_event: id, // The ID of the chapter event
        tickets: chosenTickets
      };
      
      // Call the API
      await reserveTicket(requestBody);

      // Navigate to confirmation page
      navigate("/Payment", { state: { email, totalAmount, chosenTickets } });
    } catch (error) {

      if(error === "mail") {
        alert("You have not entered matching emails")
      }
      else if(error === "no tickets") {
        alert("You have to pick atleast one ticket")
      }
      else {
        alert("An error occurred while reserving tickets. Please try again.");
      }
    }
  };

  if (!event) return <p>Loading...</p>;

  return (
    <div>
      <h2>{event.title}</h2>
      <p>{event.description}</p>
      <p>
        Event Time: {" "}
        {new Date(event.event_at).toLocaleString("en-US", {
          weekday: "long",
          year: "numeric",
          month: "long",
          day: "numeric",
          hour: "numeric",
          minute: "2-digit",
          hour12: false,
        })}
      </p>

      {tickets.map((ticket) => (
        <div key={ticket.ticket_type} style={{ marginBottom: "15px" }}>
          <span style={{ marginRight: "10px" }}>{ticket.title}</span>
          <span style={{ marginRight: "10px" }}>{ticket.price} kr</span>
          <button
            onClick={() => handleTicketChange(ticket.ticket_type, "increment")}
            className="btn btn-primary"
            style={{ marginRight: "5px" }}
          >
            +
          </button>
          <span>{ticket.count}</span>
          <button
            onClick={() => handleTicketChange(ticket.ticket_type, "decrement")}
            className="btn btn-primary"
            style={{ marginLeft: "5px" }}
          >
            -
          </button>
        </div>
      ))}
      
      <div>
        <h4>Total Amount: {totalAmount} kr</h4>
      </div>
      
      <div>
        <div>
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div>
          <input
            type="email"
            placeholder="Confirm your email"
            value={confirmEmail}
            onChange={(e) => setConfirmEmail(e.target.value)}
          />
        </div>
      </div>
      
      <div>
        <button onClick={handleReserve} className="btn btn-primary">Start Ticket Purchase</button>
      </div>
    </div>
  );
};

export default EventDetails;
