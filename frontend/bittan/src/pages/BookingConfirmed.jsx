// src/pages/BookingConfirmed.js
import React, { useEffect, useState } from 'react';
import QRCodeGenerator from '../components/QRCodeGenerator';
import axiosInstance from '../api/axiosConfig';
import { useLocation } from 'react-router-dom';

const BookingConfirmed = () => {
  const [bookingDetails, setBookingDetails] = useState(null);
  const location = useLocation();

  useEffect(() => {
    // Fetch booking details using the Swish token or other identifiers
    axiosInstance
      .get('/get-booking-details/', {
        params: { swish_token: location.state?.swishToken },
      })
      .then((response) => {
        setBookingDetails(response.data);
      })
      .catch((error) => {
        console.error('Error fetching booking details:', error);
      });
  }, [location.state]);

  if (!bookingDetails) return <p>Loading booking details...</p>;

  return (
    <QRCodeGenerator
      bookingReference={bookingDetails.booking_reference}
      eventName={bookingDetails.event_name}
      userEmail={bookingDetails.user_email}
      time={new Date(bookingDetails.time).toLocaleString()}
    />
  );
};

export default BookingConfirmed;
