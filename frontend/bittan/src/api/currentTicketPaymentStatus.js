import axiosInstance from "./axiosConfig";

/**
 * Starts the payment process using the session ID from the reserveTicket response.
 *
 * @param {string} token - swish-token gained from startPayment.
 * @returns {blob} Tthe blob of the png of the QR-code
 * @throws {Error} If the request fails.
 */

export const currentTicketPaymentStatus = async () => {
    try {
      const response = await axiosInstance.get(`/current_ticket_payment_status/`);
      return response.data; 
    } catch (error) {
      console.error('AAAAAAAAAAAAAAAaFuk', error);
      throw error;
    }
};

