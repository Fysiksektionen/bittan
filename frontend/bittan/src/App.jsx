// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import EventGrid from './components/EventGrid';
import EventDetails from './components/EventDetails';
import Confirmation from './components/Confirmation';
import Payment from './components/Payment';
import BookingConfirmed from './pages/BookingConfirmed';
import TicketValidation from './components/TicketValidation';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<EventGrid />} />
          <Route path="/events/:id" element={<EventDetails />} />
          <Route path="/confirmation" element={<Confirmation />} />
          <Route path="/payment" element={<Payment />} />
          <Route path="/booking-confirmed" element={<BookingConfirmed />} />
          <Route path="/validate-ticket" element={<TicketValidation />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
