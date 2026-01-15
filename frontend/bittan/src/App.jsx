// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import EventGrid from './components/EventGrid';
import EventDetails from './components/EventDetails';
import Payment from './components/Payment';
import BookingConfirmed from './components/BookingConfirmed';
import TicketValidation from './components/TicketValidation';
import AdminPage from './components/admin/AdminPage.jsx'
import QuestionSummary from './components/admin/QuestionSummary';

const basename = process.env.PUBLIC_URL || "/";

function App() {
  return (
    <Router basename={basename}>
      <Layout>
        <Routes>
          <Route path="/" element={<EventGrid />} />
          <Route path="/events/:id" element={<EventDetails />} />
          <Route path="/payment/:session_id" element={<Payment />} />
          <Route path="/booking-confirmed" element={<BookingConfirmed />} />
          <Route path="/validate-ticket" element={<TicketValidation />} />
          <Route path="/admin/question_summary/:question_id" element={<QuestionSummary />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
