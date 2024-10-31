import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axiosInstance from '../api/axiosConfig';
import { reserveTicket } from '../api/reserveTicket';

const EventDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [tickets, setTickets] = useState([]);

  useEffect(() => {
    // Fetch event details
    axiosInstance.get(`/events/${id}/`).then((response) => {
      setEvent(response.data);
      // Initialize tickets selection
      setTickets(
        response.data.ticket_types.map((type) => ({
          ticket_type: type.name,
          count: 0,
        }))
      );
    });
  }, [id]);

  const handleTicketChange = (index, count) => {
    const newTickets = [...tickets];
    newTickets[index].count = count;
    setTickets(newTickets);
  };

  const handleReserve = async () => {
    await reserveTicket(id, tickets.filter((t) => t.count > 0));
    navigate('/confirmation');
  };

  if (!event) return <p>Loading...</p>;

  return (
    <div>
      <h2>{event.title}</h2>
      <p>{event.description}</p>
      <p>{event.time}</p>
      {event.ticket_types.map((type, index) => (
        <div key={type.name}>
          <label>{type.name} - {type.price} USD</label>
          <input
            type="number"
            min="0"
            value={tickets[index].count}
            onChange={(e) => handleTicketChange(index, parseInt(e.target.value))}
          />
        </div>
      ))}
      <button onClick={handleReserve}>Reserve Tickets</button>
    </div>
  );
};

export default EventDetails;
