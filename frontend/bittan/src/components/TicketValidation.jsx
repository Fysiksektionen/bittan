// src/components/TicketValidation.js
import React, { useState, useEffect } from 'react';
import { Modal, Col, Row } from 'react-bootstrap';
import { validateTicket } from '../api/validateTicket';
import TicketScanner from './QrScanner';

const TicketValidation = () => {
  const [externalId, setExternalId] = useState('');
  const [validationResult, setValidationResult] = useState(null);
  const [state, setState] = useState("enterPassword");
  const [password, setPassword] = useState(undefined);
  const [error, setError] = useState(null);

  const [showLove, setShowLove] = useState(false);
  const [loveIndex, setLoveIndex] = useState(0);
  const [specialLove, setSpecialLove] = useState(false);
  const [specialLoveID, setSpecialLoveID] = useState("");
  const [foundPkmCards, setFoundPkmCards] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedCard, setSelectedCard] = useState(null);


  useEffect(() => {
    const timer = setTimeout(() => {
      setSpecialLove(false);
      setShowLove(false);
    }, 5000);

    return () => clearTimeout(timer);
  }, [specialLove]);

  const loveContent = [
    { type: "image", content: "https://lh3.googleusercontent.com/d/1I7mf79CbjkNxWzJI6FpLzhbuNNn2o49b" },
    { type: "gif", content: "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWxic2YwMmZnZmkwcWh6Y2k2eXRjam1maHM2YmY1YXdidWt3cmhwYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XsNAXQl1E8ig8MHAhf/giphy.gif" },
    { type: "gif", content: "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExNXcyaHA3d2k3cDJ6MDFocW14c2l3enNkNXdnMjJpaGhzMXQ2bmd6aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/tFH0DeoATug9eIDkwl/giphy.gif" },
    { type: "text", content: "Ni skannar bäst! (bästare än SL)" },
    { type: "gif", content: "https://lh3.googleusercontent.com/d/1kMqapo8lUrapYzrwCyoMZTgaLP-Z82GA" },
    { type: "gif", content: "https://judoinfo.com/wp-content/uploads/2016/07/animations//seoinage.gif"}
  ];

  const pkmCards = {
    "BITTAN": "https://lh3.googleusercontent.com/d/1L2CfRKsEKa85e5KkLS_hDz8D6Lt6Xuem",
    "EDVARD": "https://lh3.googleusercontent.com/d/1Qs10KlzK41gJQ2OxsXWXgPqe1VG2QqnD",
    "CALOTA": "https://lh3.googleusercontent.com/d/1Ktq6IKEapLqijP8dl5qdd7Gcwyau-Zq9",
  }

  const onScan = (scanResult) => {
    const ticketId = scanResult?.data;
    if (typeof ticketId !== 'string' || ticketId.length !== 6) {
      setError('Inte en giltig biljett QR-kod');
      return;
    }
    handleValidate(ticketId);
  };

  const handleValidate = async (ticketId) => {
    const rand = Math.random();
    if (pkmCards.hasOwnProperty(ticketId)) {
      setShowLove(true);
      setSpecialLove(true);
      setSpecialLoveID(ticketId);
      foundPkmCards.push(ticketId);
    }
    if (rand < 1) {
      setShowLove(true);
      setLoveIndex(Math.floor(Math.random()*loveContent.length));
    } else if (rand > 0.33 && rand < 0.67) {
      setShowLove(false);
      setSpecialLove(false);
    } 
    try {
      const result = await validateTicket(ticketId, password);
      setValidationResult(result);
      setState("showTicket");
    } catch (error) {
      if (error.response?.status === 401) {
        setPassword(undefined);
        setError("Fel lösenord");
        setState("enterPassword");
      } else if (error.response?.status === 404) {
        setError("Biljetten finns inte i databasen");
      } else {
        setError("Ett fel uppstod: " + (error.response || error.message));
      }
    }
  };

  const renderError = () => (
    <div className="alert alert-danger position-relative max-w-md mx-auto">
      <p>{error}</p>
      <button onClick={() => setError(null)} className="btn-close position-absolute top-0 end-0 m-2" />
    </div>
  );

  const renderPasswordInput = () => (
    <div className="d-flex flex-column align-items-center p-4">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.target);
          setPassword(formData.get("password"));
          setState("scanTicket");
        }}
        className="w-100"
        style={{ maxWidth: "300px" }}
      >
        <input
          type="password"
          name="password"
          placeholder="Skriv in lösenord"
          value={password || ''}
          onChange={(e) => setPassword(e.target.value)}
          className="form-control mb-3"
          required
        />

        <button type="submit" className="btn btn-primary w-100">
          Börja scanna
        </button>
      </form>
    </div>
  );

  const renderScanner = () => {
    const isValidTicketId = /^[a-zA-Z0-9]{6}$/.test(externalId);

    return (
      <div className="d-flex flex-column align-items-center p-4 bg-light rounded shadow-sm" style={{ maxWidth: "500px", margin: "0 auto" }}>
        <h4 className="mb-4">Scanna eller skriv in biljett-ID</h4>

        <div className="w-100 mb-3">
          <label htmlFor="ticket-id" className="form-label">Biljett-ID</label>
          <input
            id="ticket-id"
            type="text"
            className="form-control text-center"
            placeholder="Ex: AB12CD"
            value={externalId}
            onChange={(e) => setExternalId(e.target.value.toUpperCase())}
            maxLength={6}
          />
        </div>

        <button
          className="btn btn-primary w-100 mb-4"
          onClick={() => handleValidate(externalId)}
          disabled={specialLove || !isValidTicketId}
        >
          Visa biljett
        </button>

        <div className="w-100">
          <TicketScanner onScan={onScan} />
        </div>
      </div>
    );
  };

  const renderResult = () => (
    <div className="mt-4 mx-auto p-4 border rounded shadow-sm bg-light" style={{ maxWidth: "500px" }}>
      <h4 className="text-center mb-4">Scanningsresultat</h4>

      <ul className="list-group mb-4">
        <li className="list-group-item d-flex justify-content-between">
          <strong>Biljett-ID:</strong>
          <span>{validationResult.external_id}</span>
        </li>
        <li className="list-group-item d-flex justify-content-between">
          <strong>Evenemang:</strong>
          <span>{validationResult.chapter_event}</span>
        </li>
        <li className={`list-group-item d-flex justify-content-between ${validationResult.status === "PAID" ? "text-success" : "text-danger"}`}>
          <strong>Betalningsstatus:</strong>
          <span>{validationResult.status === "PAID" ? "Betalad" : "Ej betalad"}</span>
        </li>
        <li className={`list-group-item d-flex justify-content-between ${validationResult.times_used > 0 ? "text-danger" : "text-success"}`}>
          <strong>Använd:</strong>
          <span>{validationResult.times_used} {validationResult.times_used === 1 ? "gång" : "gånger"}</span>
        </li>
      </ul>

      <div className="d-grid gap-2 d-md-flex justify-content-md-between">
        <button
          className="btn btn-success"
          onClick={() => {
            validateTicket(validationResult.external_id, password, true);
            setState("scanTicket");
          }}
        >
          Markera som använd och gå tillbaka
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => setState("scanTicket")}
        >
          Tillbaka till scanning
        </button>
      </div>
    </div>
  );

  const renderLove = () => {
    const currentItem = loveContent[loveIndex];
    return (
        <div
      className={specialLove ? "" : "position-absolute top-0 end-0 m-3"}
      style={specialLove ? {
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        zIndex: 1000,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        pointerEvents: "none",
        background: "radial-gradient(circle closest-side, #ff49ff 0%, transparent 100%)",

      } : {
        zIndex: 1000,
        width: "300px",
        height: "150px",
        pointerEvents: "none"
      }
    }
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {!specialLove && currentItem.type === "text" && (
          <p
            style={{
              color: "#333",
              textShadow: "1px 1px 2px rgba(255, 255, 255, 0.8)",
              textAlign: "center",
              margin: 0,
              padding: "0 10px",
              maxWidth: "100%",
              maxHeight: "100%",
            }}
          >
            {currentItem.content}
          </p>
        )}
        {(!specialLove && (currentItem.type === "image" || currentItem.type === "gif")) && (
          <img
            src={currentItem.content}
            alt="Love content"
            style={{
              maxWidth: "100%",
              maxHeight: "100%",
              objectFit: "contain", 
              borderRadius: "0.5rem",
            }}
          />
        )}

        {specialLove && ( pkmCards.hasOwnProperty(specialLoveID)) && (
          <div style={{textAlign: "center"}}>
        <p
            className="rainbow-text"
            style={{
              margin: 0,
              padding: "0 10px",
              maxWidth: "100%",
              maxHeight: "100%",
              fontWeight: "bold",
              fontSize: "2rem",
              zIndex: 1001
            }}
          >
          LEGENDARY TICKET
            {[...Array(10)].map((_, i) => (
    <span key={i} className="sparkle" style={{ "--i": i }}>✨</span>
  ))}
          </p>
          <img 
            src={pkmCards[specialLoveID]}
            style={{
              maxWidth: "100%",
              maxHeight: "100%",
              padding: "8px",
              objectFit: "contain", 
              borderRadius: "0.5rem",
            }}>
          </img>
          </div>
        )}
      </div>

      {/* CSS for rainbow animation */}

<style>
  {`
    @keyframes rainbow {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    @keyframes pulse {
      0%, 100% {
        transform: scale(1);
        text-shadow: 0 0 10px gold, 0 0 20px orange;
      }
      50% {
        transform: scale(1.2);
        text-shadow: 0 0 20px white, 0 0 40px gold, 0 0 60px red;
      }
    }

    @keyframes sparkle {
      0% { opacity: 0; transform: translate(0, 0) scale(0.5) rotate(0deg); }
      50% { opacity: 1; transform: translate(var(--dx, 0px), var(--dy, -20px)) scale(1.2) rotate(45deg); }
      100% { opacity: 0; transform: translate(var(--dx, 0px), var(--dy, -40px)) scale(0.5) rotate(90deg); }
    }

    .rainbow-text {
      position: relative;
      display: inline-block;
      background: linear-gradient(
        270deg,
        red,
        orange,
        yellow,
        green,
        blue,
        indigo,
        violet
      );
      background-size: 400% 400%;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: rainbow 5s ease infinite, pulse 2s ease-in-out infinite;
    }

    .sparkle {
      position: absolute;
      font-size: 1.5rem;
      pointer-events: none;

      /* Randomized positions around text */
      top: calc(50% + (var(--i) * 5px - 25px));
      left: calc(50% + (var(--i) * 10px - 50px));

      /* Custom offsets for more chaotic motion */
      --dx: calc((var(--i) - 5) * 30px);
      --dy: calc(-20px - var(--i) * 3px);

      animation: sparkle 2s infinite ease-in-out;
      animation-delay: calc(var(--i) * 0.2s);
    }
  `}
</style>

    </div>
  );
};

  const handleCardClick = (imgSrc) => {
    setSelectedCard(imgSrc);
    setShowModal(true);
  };

  return (
    <div className="container" >
      {error && renderError()}
      {state === "enterPassword" && renderPasswordInput()}
      {state === "scanTicket" && renderScanner()}
      {state === "showTicket" && renderResult()}
      {(showLove && state !== "enterPassword") && renderLove()}
      
    {state !== "enterPassword" && (
      <>
      <Row  className="g-1 m-0 p-0" xs={4} sm={4} md={6} lg={8}>
        {Object.entries(pkmCards).map(([name, imgSrc]) => (
        <Col className="p-0">
          <div style={{
            width: '100%',
            aspectRatio: '5 / 7',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            {foundPkmCards.includes(name) ? (
              <img
                src={imgSrc}
                alt={name}
                onClick={() => handleCardClick(imgSrc)}
                style={{
                  width: '100%',
                  height: '100%',      // Fill container
                  objectFit: 'cover',   // Maintain aspect ratio
                  borderRadius: '3px',
                  border: '1px solid #eee',
                  display: 'block'
                }}
              />
            ) : (
              <div
                style={{
                  width: '100%',
                  height: '100%',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '3px',
                  border: '1px dashed #ccc',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '8px',
                  color: '#999'
                }}
              >
                ?
              </div>
            )}
            <div
              style={{
                fontSize: '8px',
                textAlign: 'center',
                padding: '2px 0',
                lineHeight: '1',
                width: '100%'
              }}
            >
              <small className="text-muted">{foundPkmCards.includes(name) ? name : "??????"}</small>
            </div>
          </div>
        </Col>
        ))}
      </Row>

    
    <Modal
        show={showModal}
        onHide={() => setShowModal(false)}
        size="lg"
        centered
        style={{ pointerEvents: "none"}}
      >
        <Modal.Body className="p-0" onClick={() => setShowModal(false)}>
          <img
            src={selectedCard}
            style={{
              width: '100%',
              maxHeight: '80vh',
              objectFit: 'contain',
              display: 'block',
              margin: '0 auto'
            }}
          />
        </Modal.Body>
      </Modal>
      </>
    )}
    </div>
  );
};

export default TicketValidation;

