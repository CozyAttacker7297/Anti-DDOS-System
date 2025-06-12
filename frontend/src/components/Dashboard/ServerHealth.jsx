import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../Server/ServerHealth.css';

const ServerCard = ({ name, status, cpu, ram, onRemove }) => {
  const getStatusClass = (value) => {
    if (value >= 90) return 'server-healthy';
    if (value >= 70) return 'server-warning';
    return 'server-critical';
  };

  return (
    <div className="server">
      <div className="server-header">
        <div className="server-name">{name}</div>
        {onRemove && (
          <button 
            className="remove-server" 
            onClick={() => onRemove(name)}
            title="Remove server"
          >
            <i className="fas fa-times"></i>
          </button>
        )}
      </div>
      <div className={`server-status ${getStatusClass(status)}`}>{status}%</div>
      <div className="server-metrics">
        <div className="metric">
          <i className="fas fa-microchip"></i>
          <span>CPU: {cpu}%</span>
        </div>
        <div className="metric">
          <i className="fas fa-memory"></i>
          <span>RAM: {ram}%</span>
        </div>
      </div>
    </div>
  );
};

const ServerHealthDashboard = () => {
  const [servers, setServers] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newServer, setNewServer] = useState('');
  const [lbStatus, setLbStatus] = useState('active');
  const [nextServer, setNextServer] = useState(null);

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

  const handleAddServer = async (e) => {
    e.preventDefault();
    if (!newServer) return;

    try {
      await axios.post('/api/load-balancer/register', { server: newServer });
      setNewServer('');
      fetchServerHealth();
    } catch (err) {
      setError("Failed to add server. Please check the server address.");
    }
  };

  const handleRemoveServer = async (serverName) => {
    try {
      await axios.delete(`/api/load-balancer/servers/${encodeURIComponent(serverName)}`);
      fetchServerHealth();
    } catch (err) {
      setError("Failed to remove server.");
    }
  };

  const handleGetNextServer = async () => {
    try {
      const response = await axios.get('/api/load-balancer/next-server');
      setNextServer(response.data.server);
    } catch (err) {
      setError("Failed to get next server.");
    }
  };

  useEffect(() => {
    fetchServerHealth();
    const interval = setInterval(fetchServerHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-section">
      <div className="section-header">
        <h2 className="section-title">Server Management</h2>
        <div className="load-balancer-status">
          <div className={`status-indicator status-${lbStatus}`}></div>
          <span>Load Balancer: {lbStatus}</span>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error} <button onClick={fetchServerHealth}>Retry</button>
        </div>
      )}

      <div className="server-controls">
        <form onSubmit={handleAddServer} className="add-server-form">
          <input
            type="text"
            value={newServer}
            onChange={(e) => setNewServer(e.target.value)}
            placeholder="Enter server address (e.g., http://server:port)"
            className="server-input"
          />
          <button type="submit" className="btn btn-primary">
            <i className="fas fa-plus"></i> Add Server
          </button>
        </form>

        <div className="load-balancer-controls">
          <button onClick={handleGetNextServer} className="btn btn-secondary">
            <i className="fas fa-random"></i> Get Next Server
          </button>
          {nextServer && (
            <div className="next-server-info">
              Next Server: <span className="server-address">{nextServer}</span>
            </div>
          )}
        </div>
      </div>

      {loading && !error && (
        <div className="loading">
          <i className="fas fa-spinner fa-spin"></i> Loading server data...
        </div>
      )}

      <div className="server-health">
        {servers.map((server, index) => (
          <ServerCard
            key={index}
            {...server}
            onRemove={handleRemoveServer}
          />
        ))}
      </div>
    </div>
  );
};

export default ServerHealthDashboard;
