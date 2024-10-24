import React from 'react';
import './ticket.css'

interface TicketProps {
  name: string;
  price: number;
  quantity: number;
  onIncrement: () => void;
  onDecrement: () => void;
}

const Ticket: React.FC<TicketProps> = ({ name, price, quantity, onIncrement, onDecrement }) => {
  return (
    <div className="ticket">
      <span className="ticket-name">{name}</span>
      <div className="ticket-actions">
        <button onClick={onIncrement}>+</button>
        <span>{price} kr</span>
        <span>{quantity}</span>
        <button onClick={onDecrement}>-</button>
      </div>
    </div>
  );
};

export default Ticket;
