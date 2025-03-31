// src/api/validateTicket.js
import axiosInstance from './axiosConfig';

export const validateTicket = async (externalId, password, useTicket=false) => {
  try {
    const csrf = document.querySelector('meta[name="csrf-token"]');

    const response = await axiosInstance.put('/validate_ticket/', {
      external_id: externalId,
      password: password,
      use_ticket: useTicket,
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
