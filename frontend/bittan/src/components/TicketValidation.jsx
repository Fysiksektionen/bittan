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

  const onScan = (scanResult) => {
    const ticketId = scanResult?.data;
    if (typeof ticketId !== 'string' || ticketId.length !== 6) {
      setError('Inte en giltig biljett QR-kod');
      return;
    }
    handleValidate(ticketId);
  };

  const handleValidate = async (ticketId) => {
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

  return (
    <div className="container mt-4">
      {error && renderError()}
      {state === "enterPassword" && renderPasswordInput()}
      {state === "scanTicket" && renderScanner()}
      {state === "showTicket" && renderResult()}
    </div>
  );
};

export default TicketValidation;

