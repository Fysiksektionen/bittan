// src/api/validateTicket.js
import axiosInstance from './axiosConfig';

export const validateTicket = async (externalId, password) => {
  try {
    const csrf = document.querySelector('meta[name="csrf-token"]');

    const response = await axiosInstance.put('/validate_ticket/', {
      external_id: externalId,
      password: password,
      headers: {
        'X-CSRF-TOKEN': csrf
      }
    });
    return response.data; // Returns ticket validation data
  } catch (error) {
    console.error('Error validating ticket:', error);
    throw error;
  }
};
