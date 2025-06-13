import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ServerHealth.css';

const ServerHealth = () => {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchServerHealth = async () => {
    try {
      setError(null);
      const response = await axios.get('http://localhost:5000/api/servers/health');
      setServers(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching server health:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to fetch server health');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServerHealth();
    const interval = setInterval(fetchServerHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="loading">Loading server health data...</div>;
  }

  if (error) {
    return (
      <div className="error">
        <p>{error}</p>
        <button className="btn btn-primary" onClick={fetchServerHealth}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="server-health">
      <h2>Server Health Status</h2>
      <div className="server-grid">
        {servers.map((server) => (
          <div key={server.id} className={`server-card ${server.status.toLowerCase()}`}>
            <h3>{server.name}</h3>
            <div className="server-details">
              <p><strong>IP:</strong> {server.ip_address}</p>
              <p><strong>Status:</strong> {server.status}</p>
              <p><strong>CPU Usage:</strong> {server.cpu_usage}%</p>
              <p><strong>Memory Usage:</strong> {server.memory_usage}%</p>
              <p><strong>Last Updated:</strong> {new Date(server.last_updated).toLocaleString()}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ServerHealth;
