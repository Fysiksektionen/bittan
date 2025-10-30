import React from 'react';
import { useLocation } from "react-router-dom";


const EventPage = () => {
  const location = useLocation();
  const { mail, status, reference } = location.state || {};

  return (
    <div>
      <ul>
        <li>
          Här
        </li>
        <li>
          Ser
        </li>
        <li>
          Vi dina evenemang
        </li>
      </ul>

    </div>
  );
};

export default EventPage;
