// // src/api/startPayment.js

import axiosInstance from './axiosConfig';

/**
 * Starts the payment process using the session ID from the reserveTicket response.
 *
 * @param {string} emailAddress - The user's email address.
 * @param {string} sessionId - The session ID from reserveTicket.
 * @returns {Object} The Swish payment token.
 * @throws {Error} If the request fails.
 */
export const startPayment = async (emailAddress, sessionId) => {
  try {

    const csrf = document.querySelector('meta[name="csrf-token"]');

    const response = await axiosInstance.post(
      '/start_payment/',
      { email_address: emailAddress },
      { headers: { Cookie: `sessionid=${sessionId}`, 		'X-CSRF-TOKEN': csrf } } // Attach session ID in the request
    );

    return response.data; // Returns the Swish token
  } catch (error) {
    console.error('Error starting payment:', error);
    throw error;
  }
};
