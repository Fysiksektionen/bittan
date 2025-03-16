// src/pages/BookingConfirmed.js
import React from 'react';
import { useLocation } from "react-router-dom";


const BookingConfirmed = () => {
  const location = useLocation();
  const { email } = location.state || {};

  return (
    <div>
      <h2>Ditt biljettköp har gått igenom</h2>
        <div>Dina biljetter och bokningsbekräftelse har skickats till {email}.</div>

        <div>Om du inte har tagit emot dina biljetter inom 20 minuter kontakta <a href="mailto:biljettsupport@f.kth.se">biljettsupport@f.kth.se</a>
        </div>
    </div>
  );
};

export default BookingConfirmed;
