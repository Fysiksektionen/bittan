import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { startPayment } from "../api/startPayment";
import { generateQR } from "../api/generateQR";

const Payment = () => {
  const location = useLocation();
  const { email, totalAmount } = location.state || {};
  const [swishToken, setSwishToken] = useState(null);
  const [qrUrl, setQrUrl] = useState(null);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Check if the user is on a mobile device
    setIsMobile(/Mobi|Android/i.test(navigator.userAgent));
  }, []);

  const handlePayment = async () => {
    try {
      const token = await startPayment(email);
      setSwishToken(token);
      
      if (isMobile) {
        // Open Swish app if on mobile
        window.location.href = `swish://payment?token=${token}`;
      } else {
        // Fetch QR code as a blob
        const response = await generateQR(token);
        const blob = new Blob([response], { type: 'image/png' });
        const qrCodeUrl = URL.createObjectURL(blob);
        setQrUrl(qrCodeUrl);
      }
    } catch (error) {
      console.error("Payment failed", error);
    }
  };

  return (
    <div>
      <h2>Payment</h2>
      <p>Total Amount: {totalAmount} kr</p>
      
      {!qrUrl && (
        <button onClick={handlePayment} className="btn btn-primary">
          Pay with Swish
        </button>
      )}

      {qrUrl && (
        <div>
          <p>Scan the QR code with Swish:</p>
          <img src={qrUrl} alt="Swish QR Code" />
        </div>
      )}
    </div>
  );
};

export default Payment;
