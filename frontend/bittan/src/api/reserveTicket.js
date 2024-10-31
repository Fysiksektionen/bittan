// src/api/reserveTicket.js
import axiosInstance from './axiosConfig';

export const reserveTicket = async (eventId, tickets) => {
  const response = await axiosInstance.post('/reserve-ticket/', {
    chapter_event: eventId,
    tickets: tickets,
  });
  return response;
};
