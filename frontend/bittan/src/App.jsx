// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import EventGrid from './components/EventGrid';
import EventDetails from './components/EventDetails';
import Payment from './components/Payment';
import BookingConfirmed from './components/BookingConfirmed';
import TicketValidation from './components/TicketValidation';

const basename = process.env.PUBLIC_URL || "/";

function App() {
  return (
    <Router basename={basename}>
      <Layout>
        <Routes>
          <Route path="/" element={<EventGrid />} />
          <Route path="/events/:id" element={<EventDetails />} />
          <Route path="/payment" element={<Payment />} />
          <Route path="/booking-confirmed" element={<BookingConfirmed />} />
          <Route path="/validate-ticket" element={<TicketValidation />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
