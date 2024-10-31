import React, { useState } from 'react';
import { startPayment } from '../api/startPayment';

const Payment = () => {
  const [email, setEmail] = useState('');
  const [swishToken, setSwishToken] = useState(null);

  const handlePayment = async () => {
    const token = await startPayment(email);
    setSwishToken(token);
    // Redirect to Swish payment gateway or handle accordingly
  };

  return (
    <div>
      <h2>Payment</h2>
      <input
        type="email"
        placeholder="Enter your email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <button onClick={handlePayment}>Pay with Swish</button>
      {swishToken && <p>Payment initiated with token: {swishToken}</p>}
    </div>
  );
};

export default Payment;
