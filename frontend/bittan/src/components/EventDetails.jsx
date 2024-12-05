import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axiosInstance from "../api/axiosConfig";
import { reserveTicket } from "../api/reserveTicket";

const EventDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [tickets, setTickets] = useState([]);

  useEffect(() => {
    // Fetch event details
    axiosInstance.get(`/get_chapterevents`).then((response) => {
      const event = response.data.find((event) => event.id == id);
      setEvent(event);
      // Initialize tickets selection
      setTickets(
        event.ticket_types.map((type) => ({
          ticket_type: type.name,
          count: 0,
        }))
      );
    });
  }, [id]);

  const handleTicketChange = (index, action) => {
    const newTickets = [...tickets];
    if (action === "increment") {
      newTickets[index].count += 1;
    } else if (action === "decrement" && newTickets[index].count > 0) {
      newTickets[index].count -= 1;
    }
    setTickets(newTickets);
  };

  const EventTime = ({ datetime }) => {
    const localTime = new Date(datetime).toLocaleString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: false, // Change to true for 12-hour format
    });
    return <span>{localTime}</span>;
  };

  const handleReserve = async () => {
    await reserveTicket(id, tickets.filter((t) => t.count > 0));
    navigate("/confirmation");
  };

  if (!event) return <p>Loading...</p>;

  return (
    <div>
      <h2>{event.title}</h2>
      <p>{event.description}</p>
      <p>
        <EventTime datetime={event.event_at} />
      </p>

      {event.ticket_types.map((type, index) => (
        <div key={type.name} style={{ marginBottom: "15px" }}>
          <span style={{ marginRight: "10px" }}>{type.name}</span>
          <span style={{ marginRight: "10px" }}>{type.price} kr</span>
          <button
            onClick={() => handleTicketChange(index, "increment")}
            style={{ marginRight: "5px" }}
          >
            +
          </button>
          <span>{tickets[index]?.count || 0}</span>
          <button
            onClick={() => handleTicketChange(index, "decrement")}
            style={{ marginLeft: "5px" }}
          >
            -
          </button>
        </div>
      ))}

      <button onClick={handleReserve}>Reserve Tickets</button>
    </div>
  );
};

export default EventDetails;
