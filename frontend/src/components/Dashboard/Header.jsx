import React from 'react';
import './Header.css';

const Header = ({ title }) => {
  return (
    <div className="header">
      <h1>{title}</h1>
      <div className="load-balancer-status">
        <div className="status-indicator status-active"></div>
        <span>Load Balancer: Active</span>
      </div>
    </div>
  );
};

export default Header; 