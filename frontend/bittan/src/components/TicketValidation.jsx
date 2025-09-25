// src/components/TicketValidation.js
import React, { useState } from 'react';
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


  const loveContent = [
    { type: "text", content: "BitTan <3 Mattias Repetto" },
    { type: "image", content: "https://lh3.googleusercontent.com/d/1I7mf79CbjkNxWzJI6FpLzhbuNNn2o49b" },
    { type: "gif", content: "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWxic2YwMmZnZmkwcWh6Y2k2eXRjam1maHM2YmY1YXdidWt3cmhwYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XsNAXQl1E8ig8MHAhf/giphy.gif" },
    { type: "text", content: "Ni skannar bäst! (bästare än SL)" },
  ];

  const specialIDS = [
    "BITTAN",
  ];

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
    if (specialIDS.includes(ticketId)) {
      setShowLove(true);
      setSpecialLove(true);
      setSpecialLoveID(ticketId);
    }
    else if (rand < 0.33) {
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
          disabled={!isValidTicketId}
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
      className="position-absolute top-0 end-0 m-3"
      style={{
        zIndex: 1000,
        width: "300px",
        height: "150px",
        pointerEvents: "none"
      }}
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
        {(!specialLove && currentItem.type === "image" || currentItem.type === "gif") && (
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

        {specialLove && specialLoveID === "BITTAN" && (
          <p
            className="rainbow-text"
            style={{
              textAlign: "center",
              margin: 0,
              padding: "0 10px",
              maxWidth: "100%",
              maxHeight: "100%",
              fontWeight: "bold",
              fontSize: "1.2rem",
            }}
          >
            {"LEGENDARY TICKET"}
          </p>
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

          .rainbow-text {
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
            animation: rainbow 5s ease infinite;
          }
        `}
      </style>
    </div>
  );
};

  // const renderLove = () => {
  //   const currentItem = loveContent[loveIndex];
  //   return (
  //       <div
  //     className="position-absolute top-0 end-0 m-3"
  //     style={{
  //       zIndex: 1000,
  //       width: "300px",
  //       height: "150px",
  //       pointerEvents: "none"
  //     }}
  //   >
  //     <div
  //       style={{
  //         width: "100%",
  //         height: "100%",
  //         display: "flex",
  //         alignItems: "center",
  //         justifyContent: "center",
  //       }}
  //     >
  //       {currentItem.type === "text" && (
  //         <p
  //           style={{
  //             color: "#333",
  //             textShadow: "1px 1px 2px rgba(255, 255, 255, 0.8)",
  //             textAlign: "center",
  //             margin: 0,
  //             padding: "0 10px",
  //             maxWidth: "100%",
  //             maxHeight: "100%",
  //           }}
  //         >
  //           {currentItem.content}
  //         </p>
  //       )}
  //       {(currentItem.type === "image" || currentItem.type === "gif") && (
  //         <img
  //           src={currentItem.content}
  //           alt="Love content"
  //           style={{
  //             maxWidth: "100%",
  //             maxHeight: "100%",
  //             objectFit: "contain", 
  //             borderRadius: "0.5rem",
  //           }}
  //         />
  //       )}
  //     </div>
  //   </div>    
  //   )
  // }

  return (
    <div className="container mt-4 " >
      {error && renderError()}
      {state === "enterPassword" && renderPasswordInput()}
      {state === "scanTicket" && renderScanner()}
      {state === "showTicket" && renderResult()}
      {(showLove && state !== "enterPassword") && renderLove()}
    </div>
  );
};

export default TicketValidation;

