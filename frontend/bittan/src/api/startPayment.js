// src/api/startPayment.js
import axiosInstance from './axiosConfig';

export const startPayment = async (email) => {
  const response = await axiosInstance.post('/start-payment/', {
    email_address: email,
  });
  return response.data; // Swish token
};
