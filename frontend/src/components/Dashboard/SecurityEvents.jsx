import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import Chart from 'chart.js/auto';
import './SecurityEvents.css';

const SecurityEvents = () => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [attacksData, setAttacksData] = useState([0, 0, 0, 0, 0, 0]); // Initial data with zeros
  const [labels, setLabels] = useState(['SQLi', 'XSS', 'DDoS', 'Brute Force', 'Port Scan', 'Malware']);
  const [loading, setLoading] = useState(true);  // Loading state to handle fetching
  const [error, setError] = useState(null);      // Error state for any API issues

  // WebSocket connection setup
  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:000/ws/stats');
    ws.onopen = () => {
      console.log('WebSocket connected');
      ws.send('get_stats');  // Request stats from the server
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received stats from WebSocket:', data);
      setAttacksData(data.map(stat => parseInt(stat.value.replace(/[^\d.-]/g, ''))));  // Convert to integers
      setLabels(data.map(stat => stat.title));
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
      setError('Failed to connect to WebSocket');
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return ws;
  };

  // Fetch attack logs via HTTP
  const fetchAttackLogs = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/get-attack-logs');
      console.log('Received attack logs:', response.data);
      // Handle attack logs as necessary here
    } catch (err) {
      console.error('Error fetching attack logs:', err);
      setError('Failed to fetch attack logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const ws = connectWebSocket();  // Connect to WebSocket on mount

    // Fetch attack logs on initial load
    fetchAttackLogs();

    // Cleanup WebSocket on unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  useEffect(() => {
    if (chartRef.current) {
      const ctx = chartRef.current.getContext('2d');
      
      // Destroy existing chart if it exists
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }

      chartInstance.current = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Attacks Blocked (Last 24h)',
            data: attacksData,
            backgroundColor: [
              '#4e73df', // Blue
              '#1cc88a', // Green
              '#36b9cc', // Teal
              '#f6c23e', // Yellow
              '#e74a3b', // Red
              '#f8d7da'  // Light Red
            ],
            borderColor: [
              '#4e73df',
              '#1cc88a',
              '#36b9cc',
              '#f6c23e',
              '#e74a3b',
              '#f8d7da'
            ],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            tooltip: {
              enabled: true,
              backgroundColor: 'rgba(0,0,0,0.7)',
              titleColor: '#fff',
              bodyColor: '#fff',
              borderColor: '#ddd',
              borderWidth: 1,
              callbacks: {
                label: function(context) {
                  return `${context.label}: ${context.raw} attacks`;
                }
              }
            }
          },
          animation: {
            duration: 1000, // Smooth animation for bar chart
            easing: 'easeInOutCubic'
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                color: '#8e8e8e',
                font: {
                  size: 14
                }
              },
              grid: {
                color: '#ddd',
                borderColor: '#ddd'
              }
            },
            x: {
              ticks: {
                color: '#8e8e8e',
                font: {
                  size: 14
                }
              },
              grid: {
                color: '#ddd',
                borderColor: '#ddd'
              }
            }
          }
        }
      });
    }
  }, [attacksData, labels]);  // Re-render the chart when data or labels change

  return (
    <div className="dashboard-section">
      <div className="section-header">
        <h2 className="section-title">Recent Security Events</h2>
        <button className="btn btn-primary">View All</button>
      </div>

      {loading && <div>Loading attack logs...</div>}
      {error && <div className="error">{error}</div>}

      <div className="chart-container">
        <canvas ref={chartRef}></canvas>
      </div>
    </div>
  );
};

export default SecurityEvents;
