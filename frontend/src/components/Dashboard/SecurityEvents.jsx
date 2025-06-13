import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import Chart from 'chart.js/auto';
import './SecurityEvents.css';

const SecurityEvents = () => {
  const barChartRef = useRef(null);
  const lineChartRef = useRef(null);
  const pieChartRef = useRef(null);
  const barChartInstance = useRef(null);
  const lineChartInstance = useRef(null);
  const pieChartInstance = useRef(null);
  const [attacksData, setAttacksData] = useState([0, 0, 0, 0, 0, 0]);
  const [labels, setLabels] = useState(['SQLi', 'XSS', 'DDoS', 'Brute Force', 'Port Scan', 'Malware']);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [recentAttacks, setRecentAttacks] = useState([]);
  const [totalAttacks, setTotalAttacks] = useState(0);
  const [filter, setFilter] = useState('all');

  // Function to fetch attack statistics
  const fetchAttackStats = async () => {
    try {
      setError(null);
      const response = await axios.get('http://localhost:5000/api/dashboard/attack-stats');
      console.log('Received attack stats:', response.data);
      
      if (response.data && response.data.labels && response.data.data) {
        setLabels(response.data.labels);
        setAttacksData(response.data.data);
        setRecentAttacks(response.data.recent_attacks || []);
        setTotalAttacks(response.data.total_attacks || 0);
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
    if (barChartRef.current) {
      const ctx = barChartRef.current.getContext('2d');
      
      // Destroy existing chart if it exists
      if (barChartInstance.current) {
        barChartInstance.current.destroy();
      }

      barChartInstance.current = new Chart(ctx, {
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

  useEffect(() => {
    if (lineChartRef.current) {
      const ctx = lineChartRef.current.getContext('2d');
      
      // Destroy existing chart if it exists
      if (lineChartInstance.current) {
        lineChartInstance.current.destroy();
      }

      // Simulate attack trend data (replace with real data if available)
      const trendData = Array.from({ length: 24 }, () => Math.floor(Math.random() * 50));

      lineChartInstance.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
          datasets: [{
            label: 'Attack Trend (Last 24h)',
            data: trendData,
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            tension: 0.4,
            fill: true
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
              borderWidth: 1
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
  }, []);

  useEffect(() => {
    if (pieChartRef.current) {
      const ctx = pieChartRef.current.getContext('2d');
      
      // Destroy existing chart if it exists
      if (pieChartInstance.current) {
        pieChartInstance.current.destroy();
      }

      // Calculate severity distribution
      const severityCounts = recentAttacks.reduce((acc, attack) => {
        acc[attack.severity] = (acc[attack.severity] || 0) + 1;
        return acc;
      }, {});

      pieChartInstance.current = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: Object.keys(severityCounts),
          datasets: [{
            data: Object.values(severityCounts),
            backgroundColor: [
              '#e74c3c', // Red for high
              '#f39c12', // Orange for medium
              '#2ecc71'  // Green for low
            ],
            borderColor: '#fff',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            },
            tooltip: {
              enabled: true,
              backgroundColor: 'rgba(0,0,0,0.7)',
              titleColor: '#fff',
              bodyColor: '#fff',
              borderColor: '#ddd',
              borderWidth: 1
            }
          },
          animation: {
            duration: 1000,
            easing: 'easeInOutCubic'
          }
        }
      });
    }
  }, [recentAttacks]);

  const filteredAttacks = recentAttacks.filter(attack => {
    if (filter === 'all') return true;
    return attack.severity.toLowerCase() === filter;
  });

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

      <div className="summary-card">
        <h3>Total Attacks (Last 24h)</h3>
        <p className="total-attacks">{totalAttacks}</p>
      </div>

      <div className="charts-container">
        <div className="chart-container">
          <canvas ref={barChartRef}></canvas>
        </div>
        <div className="chart-container">
          <canvas ref={lineChartRef}></canvas>
        </div>
        <div className="chart-container">
          <canvas ref={pieChartRef}></canvas>
        </div>
      </div>

      <div className="filter-container">
        <label>Filter by Severity:</label>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {filteredAttacks.length > 0 && (
        <div className="recent-attacks">
          <h3>Recent Attacks</h3>
          <table className="attacks-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Type</th>
                <th>Source IP</th>
                <th>Severity</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredAttacks.map((attack, index) => (
                <tr key={index}>
                  <td>{new Date(attack.timestamp).toLocaleString()}</td>
                  <td>{attack.type}</td>
                  <td>{attack.source_ip}</td>
                  <td className={`severity-${attack.severity.toLowerCase()}`}>
                    {attack.severity}
                  </td>
                  <td>{attack.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default SecurityEvents;
