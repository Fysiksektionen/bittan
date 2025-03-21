// src/components/TicketValidation.js
import React, { useState } from 'react';
import { validateTicket } from '../api/validateTicket';
import TicketScanner from './QrScanner'

const TicketValidation = () => {
  const [externalId, setExternalId] = useState('');
  const [validationResult, setValidationResult] = useState(null);
  const [state, setState]  = useState("enterPassword")
  const [password, setPassword] = useState(null);

  const onScan = async (scanResult) => {
    console.log(scanResult);
    const ticketId = scanResult?.data;
    if (typeof ticketId != 'string' || ticketId.length != 6) {
      alert('Ogiltig biljett');
      return;
    }
    console.log("ticket id: " + ticketId)
    handleValidate(ticketId);
  }

  const handleValidate = async (ticketId) => {
    try {
      console.log(ticketId)
      const result = await validateTicket(ticketId);
      setState("showTicket")
      setValidationResult(result);
      console.log("Showing ticket!")
    } catch (error) {
      console.log(error)
      alert('Error validating ticket.');
    }
  };

  return (
    <div>
      <h2>Validate Ticket</h2>
      {state == "enterPassword" && <>
         <div className="flex flex-col items-center p-4">
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
      {state == "showTicket" &&
        <div className="mt-3">
          <p>Status: {validationResult.status == "PAID" ? "Betalad" : "Ej betalad" }</p>
          <p>Scannad {validationResult.times_used} gånger</p>
          <button onClick={()=>setState("scanTicket")}>Scanna nästa</button>
        </div>
      }
    </div>
  );
};

export default TicketValidation;
