import React from 'react';
import './StatsContainer.css';

const StatCard = ({ title, value, change, type, isPositive }) => (
  <div className={`stat-card ${type}`}>
    <h3>{title}</h3>
    <div className="value">{value}</div>
    <div className={`change ${isPositive ? 'positive' : 'negative'}`}>
      <i className={`fas fa-arrow-${isPositive ? 'up' : 'down'}`}></i>
      {change}
    </div>
  </div>
);

const StatsContainer = () => {
  const stats = [
    {
      title: 'ATTACKS BLOCKED',
      value: '1,248',
      change: '12% from yesterday',
      type: 'danger',
      isPositive: false
    },
    {
      title: 'MALICIOUS REQUESTS',
      value: '5,732',
      change: '8% from yesterday',
      type: 'warning',
      isPositive: true
    },
    {
      title: 'CLEAN TRAFFIC',
      value: '2.1M',
      change: '3% from yesterday',
      type: 'success',
      isPositive: true
    },
    {
      title: 'UPTIME',
      value: '99.98%',
      change: 'All systems normal',
      type: 'info',
      isPositive: true
    }
  ];

  return (
    <div className="stats-container">
      {stats.map((stat, index) => (
        <StatCard key={index} {...stat} />
      ))}
    </div>
  );
};

export default StatsContainer; 