// // src/api/generateQR.js

import axiosInstance from "./axiosConfig";

/**
 * Starts the payment process using the session ID from the reserveTicket response.
 *
 * @param {string} token - swish-token gained from startPayment.
 * @returns {blob} Tthe blob of the png of the QR-code
 * @throws {Error} If the request fails.
 */

export const generateQR = async (token) => {
    try {
      const response = await axiosInstance.get(`/generate_qr/${token}`, { responseType: 'blob' });
      return response.data; // Returns the QR code image blob
    } catch (error) {
      console.error('Error fetching QR code:', error);
      throw error;
    }
};
