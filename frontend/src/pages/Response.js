import React, { useEffect, useState, useCallback } from 'react';
import AttackLogs from '../components/Dashboard/AttackLogs';
import './Response.css';

const Response = () => {
  const [status, setStatus] = useState('Connected');
  const [ws, setWs] = useState(null);

  const connectWebSocket = useCallback(() => {
    const websocket = new WebSocket('ws://localhost:5000/ws/server-health');

    websocket.onopen = () => {
      console.log('WebSocket connection opened');
      setStatus('Connected');
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('Error connecting to WebSocket');
    };

    websocket.onclose = () => {
      console.log('WebSocket connection closed');
      setStatus('Disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        console.log('Attempting to reconnect...');
        connectWebSocket();
      }, 5000);
    };

    setWs(websocket);
  }, []);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [connectWebSocket]);

  return (
    <div className="response-page">
      <div className="response-header">
        <h2>Attack Response Center</h2>
        <div className="connection-status">
          <span className={`status-indicator ${status.toLowerCase()}`}></span>
          <span>Status: {status}</span>
        </div>
      </div>
      
      <div className="response-content">
        <AttackLogs />
      </div>
    </div>
  );
};

export default Response;
