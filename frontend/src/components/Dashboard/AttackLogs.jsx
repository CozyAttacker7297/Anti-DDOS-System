import React, { useState, useEffect } from 'react';
import './AttackLogs.css';

const AttackLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Function to fetch attack logs
  const fetchAttackLogs = async () => {
    try {
      console.log('Fetching attack logs...');  // Add a log to confirm the function is being triggered
      const response = await fetch('http://localhost:5000/api/get-attack-logs'); // Adjust endpoint if necessary
      console.log('Response status:', response.status);  // Log the response status

      // Check if the response is successful
      if (!response.ok) {
        console.error('Failed to fetch data:', response.statusText);
        throw new Error('Failed to fetch data');
      }

      const data = await response.json();
      console.log('Fetched attack logs:', data);  // Log the response data

      if (Array.isArray(data)) {
        setLogs(data); // Assuming the data is an array
      } else {
        console.error('Data format is incorrect:', data);  // Handle unexpected data format
      }

      setLoading(false); // Stop loading
    } catch (error) {
      console.error('Error fetching attack logs:', error); // Log the error if any
      setLoading(false); // Stop loading even if there's an error
    }
  };

  // Fetch attack logs on component mount
  useEffect(() => {
    fetchAttackLogs();
  }, []);

  const getSeverityClass = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'badge-danger';
      case 'high':
        return 'badge-warning';
      case 'medium':
        return 'badge-info';
      default:
        return 'badge-success';
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="dashboard-section">
      <div className="section-header">
        <h2 className="section-title">Attack Detection Logs</h2>
        <div>
          <button className="btn btn-primary">Export Logs</button>
          <button className="btn btn-success" style={{ marginLeft: '10px' }} onClick={fetchAttackLogs}>
            Refresh
          </button>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Attack Type</th>
            <th>Source IP</th>
            <th>Target</th>
            <th>Severity</th>
            <th>Action Taken</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, index) => (
            <tr key={index}>
              <td>{new Date(log.timestamp).toLocaleString()}</td> {/* Format timestamp */}
              <td>{log.type}</td>
              <td>{log.source_ip}</td> {/* Match the backend field name */}
              <td>{log.target}</td>
              <td>
                <span className={`badge ${getSeverityClass(log.severity)}`}>
                  {log.severity}
                </span>
              </td>
              <td>{log.action}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AttackLogs;
