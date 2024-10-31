// src/components/Payment.js
import React, { useState } from 'react';
import { startPayment } from '../api/startPayment';
import { useNavigate } from 'react-router-dom';

const Payment = () => {
  const [email, setEmail] = useState('');
  const navigate = useNavigate();

  const handlePayment = async () => {
    try {
      const swishToken = await startPayment(email);
      // Implement Swish payment initiation using swishToken
      // After payment confirmation, navigate to the booking confirmed page
      navigate('/booking-confirmed', { state: { swishToken } });
    } catch (error) {
      alert('Error starting payment.');
    }
  };

  return (
    <div>
      <h2>Payment</h2>
      <div className="mb-3">
        <label>Email Address</label>
        <input
          type="email"
          className="form-control"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <button className="btn btn-success" onClick={handlePayment}>
        Pay with Swish
      </button>
    </div>
  );
};

export default Payment;
