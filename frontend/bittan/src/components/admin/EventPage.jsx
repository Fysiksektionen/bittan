import React from 'react';
import { useLocation } from "react-router-dom";


const EventPage = () => {
  const location = useLocation();
  const { mail, status, reference } = location.state || {};

  return (
    <div>
      This is the event page
    </div>
  );
};

export default EventPage;
