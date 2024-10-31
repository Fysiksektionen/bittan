// src/components/QRCodeGenerator.js
import React from 'react';
import QRCode from 'react-qr-code';

const QRCodeGenerator = ({ bookingReference, eventName, userEmail, time }) => {
  const qrContent = `${bookingReference} ${eventName} ${userEmail} ${time}`;

  return (
    <div className="text-center">
      <h2>Your Booking is Confirmed!</h2>
      <QRCode value={qrContent} size={256} />
      <p>Please present this QR code at the event entrance.</p>
    </div>
  );
};

export default QRCodeGenerator;
