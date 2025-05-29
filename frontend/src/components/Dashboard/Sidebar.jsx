import React from 'react';
import './Sidebar.css';
import fsocietyLogo from '../../assets/fsociety-logo.png';

const Sidebar = ({ activeMenu, onMenuClick }) => {
  const menuItems = [
    { id: 'dashboard', icon: 'tachometer-alt', label: 'Dashboard' },
    { id: 'response', icon: 'reply-all', label: 'Response' },
    { id: 'servers', icon: 'server', label: 'Servers' },
    { id: 'blocked-ip', icon: 'ban', label: 'Blocked IP' },
    { id: 'alerts', icon: 'bell', label: 'Alerts' }
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <img src={fsocietyLogo} alt="FSOCIETY Logo" className="fsociety-logo" />
      </div>
      <div className="sidebar-menu">
        {menuItems.map((item) => (
          <div
            key={item.id}
            className={`menu-item ${activeMenu === item.id ? 'active' : ''}`}
            onClick={() => onMenuClick(item.id)}
          >
            <i className={`fas fa-${item.icon}`}></i>
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar; 