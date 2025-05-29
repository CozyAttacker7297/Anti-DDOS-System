import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ServerHealth.css';

const ServerCard = ({ name, status, cpu, ram }) => {
  const getStatusClass = (value) => {
    if (value >= 90) return 'server-healthy';
    if (value >= 70) return 'server-warning';
    return 'server-critical';
  };

  return (
    <div className="server">
      <div className="server-name">{name}</div>
      <div className={`server-status ${getStatusClass(status)}`}>{status}%</div>
      <div>CPU: {cpu}%</div>
      <div>RAM: {ram}%</div>
    </div>
  );
};

const ServerHealth = () => {
  const [servers, setServers] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchServerHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/all-server-health');
      setServers(response.data);
    } catch (err) {
      console.error("Error fetching server health:", err);
      setError("Could not load server health data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServerHealth();
    const interval = setInterval(fetchServerHealth, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-section">
      <div className="section-header">
        <h2 className="section-title">Server Health Status</h2>
      </div>

      {error && (
        <div className="error-message">
          {error} <button onClick={fetchServerHealth}>Retry</button>
        </div>
      )}

      {loading && !error && <div>Loading server data...</div>}

      <div className="server-health">
        {servers.map((server, index) => (
          <ServerCard key={index} {...server} />
        ))}
      </div>
    </div>
  );
};

export default ServerHealth;
