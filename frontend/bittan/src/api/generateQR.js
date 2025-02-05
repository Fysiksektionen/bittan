import axiosInstance from "./axiosConfig";

export const generateQR = async (token) => {
    try {
      const response = await axiosInstance.get(`/generate_qr/${token}`, { responseType: 'blob' });
      return response.data; // Returns the QR code image blob
    } catch (error) {
      console.error('Error fetching QR code:', error);
      throw error;
    }
};
