import { useNavigate } from "react-router-dom";
import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { startPayment } from "../api/startPayment";
import { sessionPaymentStatus } from "../api/sessionPaymentStatus";
import { generateQR } from "../api/generateQR";
import { Container, Row, Col } from "react-bootstrap";

const basename = process.env.PUBLIC_URL || "";

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
        if (response.status === "PAID") {
          clearInterval(interval);
          navigate("/booking-confirmed", { state: { mail: response.mail, status: response.status, reference: response.reference } });
        }
        else if (response.status !== "RESERVED") {
          clearInterval(interval);
          navigate("/booking-confirmed", { state: { mail: "", status: response.status, reference: "" } });
        }
      } catch (error) {
        console.error("Error fetching payment status:", error);
      }
    };

    interval = setInterval(fetchStatus, 1000);
    fetchStatus();

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setIsMobile(/Mobi|Android/i.test(navigator.userAgent));
  }, []);

  const handlePayment = async (sameDevice) => {
    try {
      let token = swishToken;
      if(!swishToken) {
        token = await startPayment(email);
        setSwishToken(token);
      }

      if (sameDevice) {
        window.location = `swish://paymentrequest?token=${token}`;
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
        {!qrUrl && (
          <div>
            <Row className="py-1">
              <button onClick={() => handlePayment(true)} className="btn btn-primary" disabled={!isChecked}>
                Betala med Swish på denna enhet
              </button>
            </Row>
            <Row className="py-1">
              <button onClick={() => handlePayment(false)} className="btn btn-primary" disabled={!isChecked}> 
                Betala med Swish på annan enhet 
              </button>
            </Row>
          </div>
        )}
        {qrUrl && (
            <Row className="py-1">
              <p>Skanna QR-koden i Swishappen:</p>
              <img src={qrUrl} alt="Swish QR Code" />
            </Row>
        )}
        <Row>
          <p>Du skickas tillbaka till denna sida efter att du betalat. Har du betalat omdirigeras du inom kort.</p>
        </Row>
      </Container>
    </div>
  );
};

export default Payment;
