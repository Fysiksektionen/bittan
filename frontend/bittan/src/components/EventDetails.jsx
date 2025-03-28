import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axiosInstance from "../api/axiosConfig";
import { reserveTicket } from "../api/reserveTicket"; // Separate API file for reserve tickets
import Payment from "./Payment"; // Import the Payment component

import "./EventDetails.css"
import { Col, Container, Row } from "react-bootstrap";

const EventDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [totalAmount, setTotalAmount] = useState(0);
  const [email, setEmail] = useState("");
  const [confirmEmail, setConfirmEmail] = useState("")
  const [maxTickets, setMaxTickets] = useState(8)
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch event details
    axiosInstance.get(`/get_chapterevents?format=json`).then((response) => {
      const event = response.data.chapter_events.find((event) => event.id == id);
      setEvent(event);

      setMaxTickets(event.max_tickets_per_payment)

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
          description: type.description,
        }))
      );
    });
  }, [id]);

   // Set the maximum number of tickets per type

  const handleTicketChange = (ticketTypeId, action) => {
    const totalSelected = tickets.reduce((sum, ticket) => sum + ticket.count, 0);
  
    const newTickets = tickets.map((ticket) => {
      if (ticket.ticket_type === ticketTypeId) {
        let newCount = ticket.count;
  
        if (action === "increment" && totalSelected < maxTickets) {
          newCount += 1;
        } else if (action === "decrement" && ticket.count > 0) {
          newCount -= 1;
        }
  
        return { ...ticket, count: newCount };
      }
      return ticket;
    });
    setTickets(newTickets);
  
    // Update total amount
    const total = newTickets.reduce((sum, ticket) => sum + ticket.count * ticket.price, 0);
    setTotalAmount(total);
  };

  const handleReserve = async (e) => {
    e.preventDefault();
    try {

      if (email === "") throw "no_mail"
      
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
      navigate("/Payment", { state: { email, totalAmount, chosenTickets, event } });
    } catch (error) {

      if(error === "mail") {
        setError("Mejladresserna matcher inte.")
      }
      else if(error === "no tickets") {
        setError("Du måste välja minst en biljett.")
      }
      else if (error === "no_mail") {
        setError("Du måste ange en mejladress")
      }
      else if (error.response && error.response.data.error === "OutOfTickets") {
        setError(`Endast ${error.response.data.tickets_left} biljetter kvar till denna föreställning.`)
      }
      else {
        setError("Ett fel uppstod när biljetterna skulle reserveras. Prova igen, funkar det inte försök öppna i ett privat fönster eller rensa kakor. Går det fortfarande inte? Maila biljett support");
      }
    }
  };

  if (!event) return <p>Laddar...</p>;

  return (
    <div>
      <Container>
    <Row>
    <Col>
      <h2>{event.title}</h2>
      <p>{event.description}</p>
      <p>
        Tid: {" "}
        {new Date(event.event_at).toLocaleString("sv-SE", {
          weekday: "long",
          year: "numeric",
          month: "long",
          day: "numeric",
          hour: "numeric",
          minute: "2-digit",
          hour12: false,
        })}
      </p>
    </Col>
    </Row>


      {tickets.map((ticket) => (
        <Row key={ticket.ticket_type} className="p-0" style={{ maxWidth: "400px" }} >
          <Col style={{ marginBottom: "15px"}}>
            <Container className="elevated-container">
              <Row className="p-0 pt-2 m-0 g-0">
                <Col xs={4} className="d-flex text-center justify-content-center align-items-center">
                  <b>{ticket.title}</b>
                </Col>
                <Col xs={2} className="d-flex text-center justify-content-center align-items-center">
                  {ticket.price} kr
              </Col>
              <Col className="text-center">
                <button
                  onClick={() => handleTicketChange(ticket.ticket_type, "decrement")}
                  className="btn btn-primary"
                  disabled={ticket.count === 0}
                  style={{ marginRight: "-24px"}}
                >
                  -
                </button>
              </Col>
              <Col className="d-flex text-center justify-content-center align-items-center">
                {ticket.count}
              </Col>
              <Col className="text-center">
                <button
                  onClick={() => handleTicketChange(ticket.ticket_type, "increment")}
                  className="btn btn-primary"
                  disabled={tickets.reduce((sum, t) => sum + t.count, 0) >= maxTickets}
                  style={{ marginLeft: "-24px"}}
                >
                  +
                </button>
              </Col>
              </Row>
              <Row className="pt-3 pb-3">
                <Col className="text-left">
                  {ticket.description}
                </Col>
              </Row>
            </Container>
          </Col>
        </Row>
      ))}


      <div>
        <h4>Totalt: {totalAmount} kr</h4>
      </div>
      
      <form onSubmit={handleReserve}>
        <Row className="py-1">
          <Col className="text-left">
            <input
              type="email"
              placeholder="Skriv din mejladress"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{maxWidth: "300px"}}
            />
          </Col>
        </Row>
        <Row className="py-1">
          <Col className="text-left">
          <input
            type="email"
            placeholder="Bekräfta mejladress"
            value={confirmEmail}
            onChange={(e) => setConfirmEmail(e.target.value)}
            style={{maxWidth: "300px"}}
          />
          </Col>
        </Row>
          {error && <Row className="py-1"><Col className="text-left text-danger">{error}</Col></Row>}
        <Row className="py-1">
          <Col className="text-left">
            <button type="submit" className="btn btn-primary">Gå vidare till betalning</button>
          </Col>
        </Row>
    </form>
        <Row>
          <p>Vill du ha fler än 12 biljetter? Skriv ett mail till <a href="mailto:biljettsupport@f.kth.se">biljettsupport@f.kth.se</a></p>
        </Row>
      </Container>
      
      <div>
      </div>
    </div>
  );
};

export default EventDetails;
