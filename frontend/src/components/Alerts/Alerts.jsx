import React, { useState } from 'react';
import './Alerts.css';

const Alerts = () => {
  const [notificationType, setNotificationType] = useState('Email');
  const [severityLevels, setSeverityLevels] = useState({
    Critical: true,
    High: false,
    Medium: false,
    Low: false,
  });
  const [frequency, setFrequency] = useState('Real-Time');
  const [userChannels, setUserChannels] = useState({
    Email: true,
    SMS: false,
    'In-App': false,
  });
  const [filterDate, setFilterDate] = useState('');
  const [filterType, setFilterType] = useState('All Types');

  const alertHistory = [
    {
      date: '2024-11-17',
      type: 'Email',
      severity: 'Caution',
      status: 'Unread',
    },
  ];

  const handleSeverityChange = (level) => {
    setSeverityLevels((prev) => ({ ...prev, [level]: !prev[level] }));
  };

  const handleChannelChange = (channel) => {
    setUserChannels((prev) => ({ ...prev, [channel]: !prev[channel] }));
  };

  return (
    <div className="alerts-container">
      <h2 className="alerts-title">Alerts & Notifications</h2>
      <p className="alerts-desc">Configure how you receive alerts and manage alert history.</p>
      <div className="alerts-row">
        <div className="alerts-card">
          <h3>Alert Configuration</h3>
          <div className="form-group">
            <label>Notification Type:</label>
            <select value={notificationType} onChange={e => setNotificationType(e.target.value)}>
              <option>Email</option>
              <option>SMS</option>
              <option>In-App</option>
            </select>
          </div>
          <div className="form-group">
            <label>Severity Level:</label>
            <div className="checkbox-group">
              {['Critical', 'High', 'Medium', 'Low'].map(level => (
                <label key={level}>
                  <input
                    type="checkbox"
                    checked={severityLevels[level]}
                    onChange={() => handleSeverityChange(level)}
                  />
                  {level}
                </label>
              ))}
            </div>
          </div>
          <div className="alerts-actions">
            <button className="btn btn-secondary">Preview Alert</button>
            <button className="btn btn-primary">Send Test Alert</button>
          </div>
        </div>
        <div className="alerts-card">
          <h3>User Preferences</h3>
          <div className="form-group">
            <label>Frequency:</label>
            <select value={frequency} onChange={e => setFrequency(e.target.value)}>
              <option>Real-Time</option>
              <option>Hourly</option>
              <option>Daily</option>
            </select>
          </div>
          <div className="form-group">
            <label>Severity Level:</label>
            <div className="checkbox-group">
              {['Email', 'SMS', 'In-App'].map(channel => (
                <label key={channel}>
                  <input
                    type="checkbox"
                    checked={userChannels[channel]}
                    onChange={() => handleChannelChange(channel)}
                  />
                  {channel}
                </label>
              ))}
            </div>
          </div>
          <div className="alerts-actions">
            <button className="btn btn-primary">Save Preferences</button>
          </div>
        </div>
      </div>
      <div className="alerts-history-card">
        <h3>Alert History</h3>
        <div className="alerts-history-filters">
          <div className="form-group">
            <label>Date:</label>
            <input type="date" value={filterDate} onChange={e => setFilterDate(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Alert Type:</label>
            <select value={filterType} onChange={e => setFilterType(e.target.value)}>
              <option>All Types</option>
              <option>Email</option>
              <option>SMS</option>
              <option>In-App</option>
            </select>
          </div>
          <button className="btn btn-secondary">Filter Alerts</button>
        </div>
        <table className="alerts-history-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Alert Type</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {alertHistory.map((alert, idx) => (
              <tr key={idx}>
                <td>{alert.date}</td>
                <td>{alert.type}</td>
                <td><span className="badge badge-caution">{alert.severity}</span></td>
                <td>{alert.status}</td>
                <td>
                  <button className="btn btn-info btn-sm">Mark as Read</button>
                  <button className="btn btn-danger btn-sm">Delete</button>
                  <button className="btn btn-secondary btn-sm">Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Alerts; 