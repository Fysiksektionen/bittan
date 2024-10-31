import React from 'react';
import { FaCheckCircle } from 'react-icons/fa';

const Confirmation = () => (
  <div className="text-center">
    <FaCheckCircle size={100} color="green" />
    <h2>Your booking is tentative</h2>
    <p>Please proceed to payment to confirm your booking.</p>
  </div>
);

export default Confirmation;
