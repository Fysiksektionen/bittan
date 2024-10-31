// src/components/EventDetails.js
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
    axiosInstance
      .get(`/chapterevents/${id}/`) // Replace with actual endpoint if different
      .then((response) => {
        setEvent(response.data);
        setTickets(
          response.data.ticket_types.map((type) => ({
            ticket_type: type.name,
            count: 0,
          }))
        );
      })
      .catch((error) => {
        console.error('Error fetching event details:', error);
      });
  }, [id]);

  const handleTicketChange = (index, count) => {
    const newTickets = [...tickets];
    newTickets[index].count = count;
    setTickets(newTickets);
  };

  const handleReserve = async () => {
    try {
      await reserveTicket(event.id, tickets.filter((t) => t.count > 0));
      navigate('/confirmation');
    } catch (error) {
      // Handle errors appropriately
      alert('Error reserving tickets.');
    }
  };

  if (!event) return <p>Loading...</p>;

  return (
    <div>
      <h2>{event.title}</h2>
      <p>{event.description}</p>
      <p>{new Date(event.event_at).toLocaleString()}</p>
      {event.ticket_types.map((type, index) => (
        <div key={type.name} className="mb-3">
          <label>
            {type.name} - {type.price} USD
          </label>
          <input
            type="number"
            min="0"
            className="form-control"
            value={tickets[index].count}
            onChange={(e) =>
              handleTicketChange(index, parseInt(e.target.value) || 0)
            }
          />
        </div>
      ))}
      <button className="btn btn-primary" onClick={handleReserve}>
        Reserve Tickets
      </button>
    </div>
  );
};

export default EventDetails;
