// // src/api/reserveTicket.js

import axiosInstance from './axiosConfig';

/**
 * Reserves tickets and retrieves the session cookie.
 *
 * @param {Object} requestBody - The request body containing chapter event ID and tickets.
 * @returns {Object} An object containing response data and session ID.
 * @throws {Error} If the request fails.
 */
export const reserveTicket = async (requestBody) => {
  try {

    const response = await axiosInstance.post('/reserve_ticket/', {
      chapter_event: requestBody.chapter_event,
      tickets: requestBody.tickets,
      email_address: requestBody.email,
      ...(localStorage.getItem("session_id") ? { session_id: localStorage.getItem("session_id") } : {}) 
    });

    localStorage.setItem("session_id", response.data)
    
    return response.data;
  } catch (error) {
    console.error('Error reserving tickets:', error);
    throw error;
  }
};
