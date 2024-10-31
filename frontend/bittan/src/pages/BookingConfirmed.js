// src/pages/BookingConfirmed.js
import React from 'react';
import QRCodeGenerator from '../components/QRCodeGenerator';

const BookingConfirmed = () => {
  // Fetch booking details from backend or state
  const bookingDetails = {
    bookingReference: 'ABC123',
    eventName: 'Student Gala',
    userEmail: 'user@example.com',
    time: '2024-10-31 19:00',
  };

  return (
    <QRCodeGenerator {...bookingDetails} />
  );
};

export default BookingConfirmed;
