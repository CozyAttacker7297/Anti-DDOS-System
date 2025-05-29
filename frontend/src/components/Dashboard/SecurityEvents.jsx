import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import './SecurityEvents.css';

const SecurityEvents = () => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

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
          labels: ['SQLi', 'XSS', 'DDoS', 'Brute Force', 'Port Scan', 'Malware'],
          datasets: [{
            label: 'Attacks Blocked (Last 24h)',
            data: [45, 32, 28, 56, 39, 12],
            backgroundColor: [
              '#e74c3c',
              '#f39c12',
              '#9b59b6',
              '#3498db',
              '#1abc9c',
              '#e67e22'
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
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }

    // Cleanup function
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, []);

  return (
    <div className="dashboard-section">
      <div className="section-header">
        <h2 className="section-title">Recent Security Events</h2>
        <button className="btn btn-primary">View All</button>
      </div>
      <div className="chart-container">
        <canvas ref={chartRef}></canvas>
      </div>
    </div>
  );
};

export default SecurityEvents; 