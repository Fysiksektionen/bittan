// src/api/startPayment.js
import axiosInstance from './axiosConfig';

export const startPayment = async (emailAddress) => {
  try {
    const response = await axiosInstance.post('/start-payment/', {
      email_address: emailAddress,
    });
    return response.data; // Returns the Swish token
  } catch (error) {
    console.error('Error starting payment:', error);
    throw error;
  }
};
