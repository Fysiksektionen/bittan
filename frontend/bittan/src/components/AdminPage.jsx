// src/pages/BookingConfirmed.js
import React from 'react';
import { useLocation } from "react-router-dom";


const BookingConfirmed = () => {
  const location = useLocation();
  const { mail, status, reference } = location.state || {};

  return (
    <div>


    </div>
  );
};

export default BookingConfirmed;
