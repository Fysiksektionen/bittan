// src/pages/BookingConfirmed.js
import React from 'react';
import { useLocation } from "react-router-dom";


const BookingConfirmed = () => {
  const location = useLocation();
  const { email } = location.state || {};

  return (
    <div>
      <h2>Booking Confirmed</h2>
        <div>We have sent a receipt and your tickets to {email}.</div>

        <div>If you have not recieved your tickets within 20 minutes of purchase please 
          contact <a href="mailto:biljettsupport@f.kth.se">biljettsupport@f.kth.se</a>
        </div>
    </div>
  );
};

export default BookingConfirmed;
