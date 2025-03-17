// src/pages/BookingConfirmed.js
import React from 'react';
import { useLocation } from "react-router-dom";


const BookingConfirmed = () => {
  const location = useLocation();
  const { mail, status, reference } = location.state || {};

  return (
    <div>
    {!status && (
      <div>
        <h1>Ett fel uppstod</h1>
        <p>Betaningen kunde inte hittas.</p>
      </div>
    )}
    {status && (
      <div>
        {status === "PAID" && (
          <div>
          <h2>Ditt biljettköp har gått igenom</h2>
            <p>Dina biljetter och bokningsbekräftelse har skickats till {mail}.</p>
            <p>Ditt referensnummer är {reference}. Spara detta tills du har tagit emot ditt mejl.</p>
            <p>Om du inte har tagit emot dina biljetter inom 20 minuter kontakta <a href="mailto:biljettsupport@f.kth.se">biljettsupport@f.kth.se</a>
            </p>
          </div>
        )}
        {status !== "PAID" && (
          <div>
          <h2>Något gick fel vid din betalning. </h2>
            <div>Vänligen försök igen. </div>

            <div>Om felet upprepar sig kontakta <a href="mailto:biljettsupport@f.kth.se">biljettsupport@f.kth.se</a>
            </div>
          </div>
        )}
      </div>
    )}
    </div>

  );
};

export default BookingConfirmed;
