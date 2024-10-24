import React, { useState } from 'react';
import Header from '../components/header';
import TicketList from '../components/ticketList';
import CheckoutButton from '../components/checkoutButton';

export default function OtherPage() {
	interface Ticket {
	  name: string;
	  price: number;
	  quantity: number;
	}
	

	const [tickets, setTickets] = useState<Ticket[]>([
	{ name: 'Student', price: 5, quantity: 1 },
	{ name: 'Normie', price: 50, quantity: 1 },
	{ name: 'Rich Boy', price: 500, quantity: 2 },
	]);

	const incrementQuantity = (index: number) => {
	const newTickets = [...tickets];
	newTickets[index].quantity += 1;
	setTickets(newTickets);
	};

	const decrementQuantity = (index: number) => {
	const newTickets = [...tickets];
	if (newTickets[index].quantity > 0) {
		newTickets[index].quantity -= 1;
		setTickets(newTickets);
	}
	};

	return (
	<div className="container">
		<Header title="Fysikalen" />
		<TicketList
		tickets={tickets}
		incrementQuantity={incrementQuantity}
		decrementQuantity={decrementQuantity}
		/>
		<CheckoutButton />
	</div>
	);
}