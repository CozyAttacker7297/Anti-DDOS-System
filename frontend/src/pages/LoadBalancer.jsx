import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './LoadBalancer.css';

const LoadBalancer = () => {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchServers = async () => {
    try {
      setError(null);
      const response = await axios.get('http://localhost:5000/api/servers');
      setServers(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching servers:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to fetch servers');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServers();
    const interval = setInterval(fetchServers, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="loading">Loading server data...</div>;
  }

  if (error) {
    return (
      <div className="error">
        <p>{error}</p>
        <button className="btn btn-primary" onClick={fetchServers}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="load-balancer">
      <h2>Load Balancer Configuration</h2>
      <div className="server-list">
        {servers.map((server) => (
          <div key={server.id} className="server-item">
            <h3>{server.name}</h3>
            <div className="server-info">
              <p><strong>IP Address:</strong> {server.ip_address}</p>
              <p><strong>Status:</strong> {server.status}</p>
              <p><strong>Weight:</strong> {server.weight}</p>
              <p><strong>Active Connections:</strong> {server.active_connections}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LoadBalancer; 