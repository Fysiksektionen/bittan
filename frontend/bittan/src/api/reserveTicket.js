// src/api/reserveTicket.js
import axiosInstance from './axiosConfig';

export const reserveTicket = async (chapterEventId, tickets) => {
  try {
    const response = await axiosInstance.post('/reserve-ticket/', {
      chapter_event: chapterEventId,
      tickets: tickets,
    });
    return response;
  } catch (error) {
    console.error('Error reserving tickets:', error);
    throw error;
  }
};
