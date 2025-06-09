import React, { useState, useEffect } from 'react';
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
  const [stats, setStats] = useState([
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
  ]);

  // WebSocket state
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:5000/ws/stats');

    // When the WebSocket is open
    ws.onopen = () => {
      console.log('WebSocket connection established');
      ws.send('get_stats'); // Request stats from the backend
    };

    // On receiving a message (i.e., updated stats)
    ws.onmessage = (event) => {
      const updatedStats = JSON.parse(event.data);
      console.log('Updated stats received:', updatedStats);
      setStats(updatedStats); // Update state with new stats
    };

    // Handle WebSocket errors
    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };

    // Handle WebSocket closure
    ws.onclose = (event) => {
      console.log('WebSocket connection closed', event);
    };

    // Save WebSocket instance to state
    setSocket(ws);

    // Cleanup WebSocket connection on component unmount
    return () => {
      // Ensure WebSocket is open before trying to close it
      if (ws && ws.readyState === WebSocket.OPEN) {
        console.log('Closing WebSocket connection');
        ws.close(); // Close WebSocket properly
      } else {
        console.log('WebSocket already closed or never opened');
      }
    };
  }, []); // Empty dependency array ensures this runs once when the component mounts

  return (
    <div className="stats-container">
      {stats.map((stat, index) => (
        <StatCard key={index} {...stat} />
      ))}
    </div>
  );
};

export default StatsContainer;
