// src/components/TicketValidation.js
import React, { useState } from 'react';
import { validateTicket } from '../api/validateTicket';

const TicketValidation = () => {
  const [externalId, setExternalId] = useState('');
  const [validationResult, setValidationResult] = useState(null);

  const handleValidate = async () => {
    try {
      const result = await validateTicket(externalId);
      setValidationResult(result);
    } catch (error) {
      alert('Error validating ticket.');
    }
  };

  return (
    <div>
      <h2>Validate Ticket</h2>
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
      <button className="btn btn-primary" onClick={handleValidate}>
        Validate Ticket
      </button>
      {validationResult && (
        <div className="mt-3">
          <p>Status: {validationResult.status}</p>
          <p>Times Used: {validationResult.times_used}</p>
        </div>
      )}
    </div>
  );
};

export default TicketValidation;
