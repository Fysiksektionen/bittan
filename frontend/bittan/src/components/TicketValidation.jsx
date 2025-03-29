// src/components/TicketValidation.js
import React, { useState } from 'react';
import { validateTicket } from '../api/validateTicket';
import TicketScanner from './QrScanner'

const TicketValidation = () => {
  const [externalId, setExternalId] = useState('');
  const [validationResult, setValidationResult] = useState(null);
  const [state, setState]  = useState("enterPassword")
  const [password, setPassword] = useState(undefined);
  const [error, setError] = useState(null);

  const onScan = (scanResult) => {
    const ticketId = scanResult?.data;

    if (typeof ticketId != 'string' || ticketId.length != 6) {
      setError('Inte en biljett qr-kod');
      return;
    }
    handleValidate(ticketId);
  }

  const handleValidate = async (ticketId) => {
    try {
      console.log(ticketId)
      const result = await validateTicket(ticketId, password);
      setState("showTicket")
      setValidationResult(result);
      console.log("Showing ticket!")
    } catch (error) {
      console.log(error)

      // The password was incorrect
      if(error.response && error.response.status == 401) {
        setPassword(undefined);
        setError("Fel lösenord")
        setState("enterPassword")
      }
      else if(error.response && error.response.status == 404) {
        setError('Biljetten finns inte med i databasen')
      }
      else {
        setError('Biljetten finns inte med i databasen' + (error.response || ""))
      }
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4 text-center">Biljettinformation</h2>
      {error ? (
      <div className="bg-red-100 text-red-800 border border-red-300 p-4 mb-4 rounded relative max-w-md mx-auto">
        <p>{error}</p>
        <button
          onClick={() => setError(null)}
          className="absolute top-1 right-2 text-xl font-bold leading-none hover:text-red-600"
        >
          &times;
        </button>
      </div>
    ) : ( <>
      {state == "enterPassword" && <>
         <div className="flex flex-col items-center p-4">
          {/* Password validation is handled when we scan the first ticket */}
          <form onSubmit={(e) => { e.preventDefault(); setState("scanTicket"); setPassword(new FormData(e.target).get("password")); }}
             className="space-y-4">
            <input
              type="password"
              name="password"
              placeholder="Skriv in lösenord"
              value={password}
              className="border rounded-lg px-3 py-2 w-64"
            />
            <button
              type="submit"
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
            >
              Submit
            </button>
          </form>
        </div>
      </>}
      {state == "scanTicket" && <>
        <div className="mb-3">
          <label>External Ticket ID</label>
          <input
            type="text"
            className="form-control"
            placeholder="Enter ticket external ID"
            value={externalId}
            onChange={(e) => setExternalId(e.target.value)}
          />
        </div>
        <button className="btn btn-primary" onClick={() => handleValidate(externalId)}>
          Validate Ticket
        </button>
        <TicketScanner onScan={onScan} />
      </>}
     {state === "showTicket" && (
  <div className="mt-4 mx-auto p-4 border rounded shadow-sm bg-light" style={{ maxWidth: "500px" }}>
    <h4 className="text-center mb-4">Biljettinformation</h4>

    <ul className="list-group mb-4">
      <li className="list-group-item d-flex justify-content-between">
        <strong>Biljett-ID:</strong>
        <span>{validationResult.external_id}</span>
      </li>
      <li className="list-group-item d-flex justify-content-between">
        <strong>Event:</strong>
        <span>{validationResult.chapter_event}</span>
      </li>
      <li className={`list-group-item d-flex justify-content-between ${validationResult.status === "PAID" ? "text-success" : "text-danger"}`}>
        <strong>Status:</strong>
        <span>{validationResult.status === "PAID" ? "Betalad" : "Ej betalad"}</span>
      </li>
      <li className={`list-group-item d-flex justify-content-between ${validationResult.times_used > 0 ? "text-danger" : "text-sucess"}`}>
        <strong>Tidigare scannad:</strong>
        <span>{validationResult.times_used} gånger</span>
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
        Använd biljett och gå tillbaka
      </button>
      <button
        className="btn btn-secondary"
        onClick={() => setState("scanTicket")}
      >
        Gå tillbaka till scanning
      </button>
    </div>
  </div>
)} 
      </>
      )}
    </div>
  );
};

export default TicketValidation;
