import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import StatsContainer from './StatsContainer';
import SecurityEvents from './SecurityEvents';
import BlockIPForm from '../IPTable/BlockIPForm';
import ServerHealthDashboard from './ServerHealth';
import Alerts from '../Alerts/Alerts';
import './Dashboard.css';
import Response from '../../pages/Response';

const TAB_TITLES = {
  dashboard: 'DASHBOARD',
  response: 'RESPONSE',
  servers: 'SERVERS',
  'blocked-ip': 'BLOCKED IP',
  alerts: 'ALERTS',
};

const Dashboard = () => {
  const [activeMenu, setActiveMenu] = useState('dashboard');

  const renderContent = () => {
    switch (activeMenu) {
      case 'dashboard':
        return (
          <>
            <StatsContainer />
            <div className="dashboard-grid">
              <SecurityEvents />
              <BlockIPForm />
            </div>
            <ServerHealthDashboard />
          </>
        );
      case 'response':
        return <Response />;
      case 'servers':
        return <ServerHealthDashboard />;
      case 'blocked-ip':
        return <BlockIPForm />;
      case 'alerts':
        return <Alerts />;
      default:
        return null;
    }
  };

  return (
    <div className="dashboard">
      <Sidebar activeMenu={activeMenu} onMenuClick={setActiveMenu} />
      <div className="main-content">
        <Header title={TAB_TITLES[activeMenu] || 'DASHBOARD'} />
        {renderContent()}
      </div>
    </div>
  );
};

export default Dashboard; 