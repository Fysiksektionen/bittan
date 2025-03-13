import { useNavigate } from "react-router-dom";
import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { startPayment } from "../api/startPayment";
import { sessionPaymentStatus } from "../api/sessionPaymentStatus";
import { generateQR } from "../api/generateQR";

const Payment = () => {
  const location = useLocation();
  const { email, totalAmount, chosenTickets } = location.state || {};
  const [swishToken, setSwishToken] = useState(null);
  const [qrUrl, setQrUrl] = useState(null);
  const [isMobile, setIsMobile] = useState(false);
  const [status, setStatus] = useState("pending");
  const [isChecked, setIsChecked] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    let interval;

    const fetchStatus = async () => {
      try {
        const response = await sessionPaymentStatus();
        if (response === "PAID") {
          clearInterval(interval);
          navigate("/booking-confirmed", { state: { email } });
        }
      } catch (error) {
        console.error("Error fetching payment status:", error);
      }
    };

    interval = setInterval(fetchStatus, 5000);
    fetchStatus();

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setIsMobile(/Mobi|Android/i.test(navigator.userAgent));
  }, []);

  const handlePayment = async () => {
    try {
      const token = await startPayment(email);
      setSwishToken(token);
      if (isMobile) {
        const callbackurl = `${window.location.origin}/booking-confirmed`;
        window.location = `swish://paymentrequest?token=${token}&callbackurl=${callbackurl}`;
      } else {
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

      <div>
        {chosenTickets.map((ticket) => (
          <div key={ticket.ticket_type} style={{ marginBottom: "15px" }}>
            <span style={{ marginRight: "10px" }}>{ticket.title}:</span>
            <span style={{ marginRight: "10px" }}>{ticket.count}*</span>
            <span style={{ marginRight: "10px" }}>{ticket.price}kr </span>
          </div>
        ))}
        <p>TOTAL: {totalAmount} kr (MOMS 0 kr)</p>
      </div>
      
      <div>
        <label>
          <input type="checkbox" checked={isChecked} onChange={() => setIsChecked(!isChecked)} />
            I agree to the <a href="https://drive.google.com/file/d/1biyd25AMdVJPcGlvS7PUojpc-Lj2jfDV/view" target="_blank" rel="noopener noreferrer">Terms and Conditions</a>{" "}and <a href="https://drive.google.com/file/d/1QmSgQAUfbS3sNTTLKmy2FBEiG3nloCSl/view" target="_blank" rel="noopener noreferrer">Privacy Policy</a>
        </label>
      </div>
      <div>
        {!qrUrl && (
          <button onClick={handlePayment} className="btn btn-primary" disabled={!isChecked}>
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
    </div>
  );
};

export default Payment;
