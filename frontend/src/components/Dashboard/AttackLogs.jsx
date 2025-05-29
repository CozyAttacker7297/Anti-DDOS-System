import React from 'react';
import './AttackLogs.css';

const AttackLogs = () => {
  const logs = [
    {
      timestamp: '2023-06-15 14:23:45',
      type: 'SQL Injection',
      sourceIp: '192.168.45.23',
      target: 'API Server',
      severity: 'Critical',
      action: 'Blocked IP'
    },
    {
      timestamp: '2023-06-15 13:56:12',
      type: 'DDoS',
      sourceIp: '45.67.89.123',
      target: 'Load Balancer',
      severity: 'Critical',
      action: 'Rate Limited'
    },
    {
      timestamp: '2023-06-15 12:34:56',
      type: 'XSS Attempt',
      sourceIp: '78.90.123.45',
      target: 'Web Server',
      severity: 'High',
      action: 'Logged'
    },
    {
      timestamp: '2023-06-15 11:45:23',
      type: 'Port Scan',
      sourceIp: '101.202.33.44',
      target: 'Firewall',
      severity: 'Medium',
      action: 'Blocked IP'
    },
    {
      timestamp: '2023-06-15 10:12:34',
      type: 'Brute Force',
      sourceIp: '67.89.123.45',
      target: 'SSH Gateway',
      severity: 'Critical',
      action: 'Blocked IP'
    }
  ];

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

  return (
    <div className="dashboard-section">
      <div className="section-header">
        <h2 className="section-title">Attack Detection Logs</h2>
        <div>
          <button className="btn btn-primary">Export Logs</button>
          <button className="btn btn-success" style={{ marginLeft: '10px' }}>Refresh</button>
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
              <td>{log.timestamp}</td>
              <td>{log.type}</td>
              <td>{log.sourceIp}</td>
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