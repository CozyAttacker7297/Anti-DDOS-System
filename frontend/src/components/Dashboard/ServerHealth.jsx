import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../Server/ServerHealth.css';

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

const ServerHealthDashboard = () => {
  const [servers, setServers] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [realTimeData, setRealTimeData] = useState({});

  // Fetch initial server health data via Axios (REST API)
  const fetchServerHealth = async () => {
    setLoading(true);
    setError(null);
    console.log("Fetching server health data...");
    try {
      const response = await axios.get('http://localhost:5000/api/server-health'); // Adjust your URL accordingly
      console.log("Server health data fetched:", response.data);
      setServers([
        {
          name: 'Server 1',
          status: response.data.cpu,  // Use actual data from response
          cpu: response.data.cpu,
          ram: response.data.ram,
        }
      ]);
    } catch (err) {
      console.error("Error fetching server health:", err);
      setError("Could not load server health data.");
    } finally {
      setLoading(false);
    }
  };

  // WebSocket for real-time stats updates (e.g., blocked attacks, malicious requests)
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/stats');  // WebSocket URL for real-time data

    ws.onopen = () => {
      console.log('WebSocket connection established');
      ws.send('get_stats');  // Request stats data on connection
    };

    ws.onmessage = (event) => {
      const updatedStats = JSON.parse(event.data);
      console.log('Real-time stats received via WebSocket:', updatedStats);
      setRealTimeData(updatedStats);  // Update real-time data state
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      ws.close();  // Cleanup WebSocket on component unmount
    };
  }, []);

  // Reload server health data every 5 seconds
  useEffect(() => {
    fetchServerHealth();
    const interval = setInterval(fetchServerHealth, 5000);  // Refresh every 5 seconds

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

      {/* Server Health Data */}
      <div className="server-health">
        {servers.map((server, index) => (
          <ServerCard key={index} {...server} />
        ))}
      </div>

      {/* Display Real-Time Stats */}
      <div className="stats-container">
        {realTimeData.length > 0 ? (
          realTimeData.map((stat, index) => (
            <div key={index} className={`stat-card ${stat.type}`}>
              <h3>{stat.title}</h3>
              <div className="value">{stat.value}</div>
              <div className={`change ${stat.isPositive ? 'positive' : 'negative'}`}>
                <i className={`fas fa-arrow-${stat.isPositive ? 'up' : 'down'}`}></i>
                {stat.change}
              </div>
            </div>
          ))
        ) : (
          <div>No stats available</div>
        )}
      </div>
    </div>
  );
};

export default ServerHealthDashboard;
