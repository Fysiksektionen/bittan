// src/api/validateTicket.js
import axiosInstance from './axiosConfig';

export const validateTicket = async (externalId) => {
  try {
    const response = await axiosInstance.put('/validate_ticket/', {
      external_id: externalId,
    });
    return response.data; // Returns ticket validation data
  } catch (error) {
    console.error('Error validating ticket:', error);
    throw error;
  }
};
