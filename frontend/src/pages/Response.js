import React, { useEffect, useState } from 'react';

const Response = () => {
  const [attackLogs, setAttackLogs] = useState([]);
  const [status, setStatus] = useState('Connecting...');

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:5000/ws/server-health');

    ws.onopen = () => {
      console.log('WebSocket connection opened');
      setStatus('Connected');
      ws.send('get_attack_logs');
    };

    ws.onmessage = (event) => {
      console.log('Received data from backend:', event.data);
      const data = JSON.parse(event.data);
      setAttackLogs(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('Error connecting to WebSocket');
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
      setStatus('Disconnected');
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Live Attack Response Logs</h2>
      <p style={styles.status}>WebSocket Status: <strong>{status}</strong></p>
      {attackLogs.length === 0 ? (
        <p style={styles.noData}>No attack logs received yet.</p>
      ) : (
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>ID</th>
              <th style={styles.th}>Timestamp</th>
              <th style={styles.th}>Type</th>
              <th style={styles.th}>Source IP</th>
              <th style={styles.th}>Target</th>
              <th style={styles.th}>Severity</th>
              <th style={styles.th}>Action</th>
            </tr>
          </thead>
          <tbody>
            {attackLogs.map((log) => (
              <tr key={log.id} style={styles.row}>
                <td style={styles.td}>{log.id}</td>
                <td style={styles.td}>{new Date(log.timestamp).toLocaleString()}</td>
                <td style={styles.td}>{log.type}</td>
                <td style={styles.td}>{log.source_ip}</td>
                <td style={styles.td}>{log.target}</td>
                <td style={styles.td}>{log.severity}</td>
                <td style={styles.td}>{log.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: '2rem',
    fontFamily: 'Segoe UI, sans-serif',
    backgroundColor: '#f9f9f9',
    borderRadius: '10px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  heading: {
    fontSize: '28px',
    marginBottom: '1rem',
    color: '#333',
    textAlign: 'center',
  },
  status: {
    fontSize: '16px',
    color: '#555',
    textAlign: 'center',
    marginBottom: '1rem',
  },
  noData: {
    textAlign: 'center',
    fontSize: '18px',
    color: '#777',
    marginTop: '1rem',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '1rem',
  },
  th: {
    backgroundColor: '#007BFF',
    color: 'white',
    padding: '10px',
    textAlign: 'left',
  },
  td: {
    padding: '10px',
    borderBottom: '1px solid #ddd',
  },
  row: {
    backgroundColor: '#fff',
  },
};

export default Response;
