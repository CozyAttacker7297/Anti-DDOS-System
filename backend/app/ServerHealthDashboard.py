import React, { useEffect, useState } from 'react';
import axios from 'axios';

function ServerHealthDashboard() {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/all-server-health')
      .then(response => {
        setServers(response.data || []);
        setLoading(false);
        setError(null);
      })
      .catch(error => {
        console.error('Error fetching server health:', error);
        setError('Failed to load server health data.');
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading health data...</p>;

  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  if (servers.length === 0)
    return <p>No server health data available.</p>;

  return (
    <section>
      <h2>Server Health Status</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ccc', padding: '10px' }}>Server Name</th>
            <th style={{ border: '1px solid #ccc', padding: '10px' }}>Status (%)</th>
            <th style={{ border: '1px solid #ccc', padding: '10px' }}>CPU Usage (%)</th>
            <th style={{ border: '1px solid #ccc', padding: '10px' }}>RAM Usage (%)</th>
          </tr>
        </thead>
        <tbody>
          {servers.map((server, index) => (
            <tr key={index}>
              <td style={{ border: '1px solid #ccc', padding: '10px' }}>{server.name}</td>
              <td style={{ border: '1px solid #ccc', padding: '10px' }}>{server.status}</td>
              <td style={{ border: '1px solid #ccc', padding: '10px' }}>{server.cpu}</td>
              <td style={{ border: '1px solid #ccc', padding: '10px' }}>{server.ram}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

export default ServerHealthDashboard;
