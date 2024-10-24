import React from 'react';
import Ticket from './ticket';
import './ticketList.css'

interface Ticket {
  name: string;
  price: number;
  quantity: number;
}

interface TicketListProps {
  tickets: Ticket[];
  incrementQuantity: (index: number) => void;
  decrementQuantity: (index: number) => void;
}

const TicketList: React.FC<TicketListProps> = ({ tickets, incrementQuantity, decrementQuantity }) => {
  return (
    <div className="ticket-list">
      {tickets.map((ticket, index) => (
        <Ticket
          key={index}
          name={ticket.name}
          price={ticket.price}
          quantity={ticket.quantity}
          onIncrement={() => incrementQuantity(index)}
          onDecrement={() => decrementQuantity(index)}
        />
      ))}
    </div>
  );
};

export default TicketList;
