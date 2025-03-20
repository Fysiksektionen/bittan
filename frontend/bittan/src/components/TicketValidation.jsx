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
    if(!ticketId) {
      alert('Ogiltig biljett');
      return;
    }
    const result = await validateTicket(ticketId);
    setValidationResult(result);
    setState("showTicket")
  }

  const handleValidate = async () => {
    try {
      const result = await validateTicket(externalId);
      setState("showTicket")
      validationResult = setValidationResult(result);
    } catch (error) {
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
              // onChange={(e) => setPassword(new FormData(e.target).get("password");}
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
        <TicketScanner onScan={onScan} />
        <button className="btn btn-primary" onClick={handleValidate}>
          Validate Ticket
        </button>
      </>}
      {state == "showticket" &&
        <div className="mt-3">
          <p>Status: {validationResult.status}</p>
          <p>Times Used: {validationResult.times_used}</p>
        </div>
      }
    </div>
  );
};

export default TicketValidation;
