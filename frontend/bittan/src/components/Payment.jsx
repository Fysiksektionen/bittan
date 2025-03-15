import { useNavigate } from "react-router-dom";
import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { startPayment } from "../api/startPayment";
import { sessionPaymentStatus } from "../api/sessionPaymentStatus";
import { generateQR } from "../api/generateQR";
import { Container, Row, Col } from "react-bootstrap";

const Payment = () => {
  const location = useLocation();
  const { email, totalAmount, chosenTickets, event } = location.state || {};
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
      <h2>Betalning</h2>
    
    <h4>{event.title}</h4>
    <Container style={{maxWidth: "400px", float: "left"}}>
        {chosenTickets.map((ticket) => (
          <Row key={ticket.ticket_type} style={{ marginBottom: "15px" }}>
            <Col className="text-left">{ticket.title}:</Col>
            <Col className="text-left">{ticket.count}st</Col>
            <Col className="text-left">{ticket.price}kr</Col>
          </Row>
        ))}
        <Row className="py-1">
          <Col className="text-left">
            Totalt: {totalAmount} kr (Moms 0 kr)
          </Col>
        </Row>
      
      <Row>
        <label>
          <input type="checkbox" checked={isChecked} onChange={() => setIsChecked(!isChecked)} />
          {" "}Jag godkänner <a href="https://drive.google.com/file/d/1biyd25AMdVJPcGlvS7PUojpc-Lj2jfDV/view" target="_blank" rel="noopener noreferrer">köpesvillkoren</a>{" "}och <a href="https://drive.google.com/file/d/1QmSgQAUfbS3sNTTLKmy2FBEiG3nloCSl/view" target="_blank" rel="noopener noreferrer">Personuppgiftspolicy</a>
        </label>
      </Row>
      <div>
        {!qrUrl && (
          <button onClick={handlePayment} className="btn btn-primary" disabled={!isChecked}>
            Betala med Swish
          </button>
        )}
        {qrUrl && (
          <div>
            <p>Skanna QR-koden i Swishappen:</p>
            <img src={qrUrl} alt="Swish QR Code" />
          </div>
        )}
      </div>
      </Container>
    </div>
  );
};

export default Payment;
