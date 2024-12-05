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
    axiosInstance.get(`/get_chapterevents`).then((response) => {
      const event = response.data.find((event) => event.id == id)
      setEvent(event);
      // Initialize tickets selection
      setTickets(
        event.map((type) => ({
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
  console.log(event)
  return (
    <div>
      <h2>{event.title}</h2>
      <p>{event.description}</p>
      <p>{event.event_at}</p>
      {event.ticket_types.map((type, index) => (
        <div>
          <label></label>
          <input/>
        </div>
      ))}
      <button onClick={handleReserve}>Reserve Tickets</button>
    </div>
  );
};

export default EventDetails;
