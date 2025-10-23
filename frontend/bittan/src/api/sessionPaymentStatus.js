import axiosInstance from "./axiosConfig";

/**
 * Starts the payment process using the session ID from the reserveTicket response.
 *
 * @returns {string} The status of the payment connected the current session, as string. See for PaymentStatus in backends `services/swish/swish_payment_request.py` for possible values
 * @throws {Error} If the request fails.
 */

export const sessionPaymentStatus = async (session_id) => {
    try {
      const response = await axiosInstance.get(`/session_payment_status/${session_id}`);
      return response.data; 
    } catch (error) {
      console.error('Unable to get current payment status', error);
      throw error;
    }
};

