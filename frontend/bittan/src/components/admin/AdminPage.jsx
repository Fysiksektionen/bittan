import React from 'react';
import { useLocation } from "react-router-dom";


const AdminPage = () => {
  const location = useLocation();
  const { mail, status, reference } = location.state || {};

  return (
    <div>
      This is the <b>Admin</b> page
      <ul>
        <li>
          Här hejsan hoppsan
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

export default AdminPage;
