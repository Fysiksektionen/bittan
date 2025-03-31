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
    // Function to get CSRF token from cookies

    const csrf = document.querySelector('meta[name="csrf-token"]');


    const response = await axiosInstance.post('/reserve_ticket/', {
      chapter_event: requestBody.chapter_event,
      tickets: requestBody.tickets,
      headers: {
        'X-CSRF-TOKEN': csrf
      }
    });

    // Extract session ID from cookies
    const setCookieHeader = response.headers['set-cookie'];
    let sessionId = null;

    if (setCookieHeader) {
      const sessionCookie = setCookieHeader.find(cookie => cookie.startsWith('sessionid='));
      if (sessionCookie) {
        sessionId = sessionCookie.split(';')[0].split('=')[1];
      }
    }

    return { data: response.data, sessionId };
  } catch (error) {
    console.error('Error reserving tickets:', error);
    throw error;
  }
};
