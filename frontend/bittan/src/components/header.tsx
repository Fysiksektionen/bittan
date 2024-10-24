import React from 'react';
import './header.css'

interface HeaderProps {
  title: string;
}

const Header: React.FC<HeaderProps> = ({ title }) => {
  return (
    <header className="header">
      <div className="circle"></div>
      <h1>{title}</h1>
    </header>
  );
};

export default Header;
