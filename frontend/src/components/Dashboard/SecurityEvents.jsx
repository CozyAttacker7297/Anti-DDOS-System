import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import Chart from 'chart.js/auto';
import './SecurityEvents.css';

const SecurityEvents = () => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [attacksData, setAttacksData] = useState([0, 0, 0, 0, 0, 0]);
  const [labels, setLabels] = useState(['SQLi', 'XSS', 'DDoS', 'Brute Force', 'Port Scan', 'Malware']);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Function to fetch attack statistics
  const fetchAttackStats = async () => {
    try {
      setError(null);
      const response = await axios.get('http://localhost:5000/api/dashboard/attack-stats');
      console.log('Received attack stats:', response.data);
      
      if (response.data && response.data.labels && response.data.data) {
        setLabels(response.data.labels);
        setAttacksData(response.data.data);
        setLastUpdate(new Date());
      } else {
        throw new Error('Invalid data format received from server');
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching attack stats:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to fetch attack statistics');
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchAttackStats();

    // Set up polling every 5 seconds
    const interval = setInterval(fetchAttackStats, 5000);

    // Cleanup
    return () => clearInterval(interval);
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
              '#e74c3c', // Red for SQLi
              '#f39c12', // Orange for XSS
              '#9b59b6', // Purple for DDoS
              '#3498db', // Blue for Brute Force
              '#1abc9c', // Teal for Port Scan
              '#e67e22'  // Dark Orange for Malware
            ],
            borderColor: [
              '#c0392b',
              '#d35400',
              '#8e44ad',
              '#2980b9',
              '#16a085',
              '#d35400'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
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
            duration: 1000,
            easing: 'easeInOutCubic'
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                color: '#8e8e8e',
                font: {
                  size: 12
                },
                precision: 0
              },
              grid: {
                color: '#ddd',
                borderColor: '#ddd'
              },
              title: {
                display: true,
                text: 'Number of Attacks',
                color: '#8e8e8e',
                font: {
                  size: 12
                }
              }
            },
            x: {
              ticks: {
                color: '#8e8e8e',
                font: {
                  size: 12
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
  }, [attacksData, labels]);

  return (
    <div className="dashboard-section">
      <div className="section-header">
        <h2 className="section-title">Recent Security Events</h2>
        <div className="header-actions">
          {lastUpdate && (
            <span className="last-update">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
          <button className="btn btn-primary" onClick={fetchAttackStats}>
            Refresh
          </button>
        </div>
      </div>

      {loading && <div className="loading">Loading attack statistics...</div>}
      {error && (
        <div className="error">
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchAttackStats}>
            Retry
          </button>
        </div>
      )}

      <div className="chart-container">
        <canvas ref={chartRef}></canvas>
      </div>
    </div>
  );
};

export default SecurityEvents;
