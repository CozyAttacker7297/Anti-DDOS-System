import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './StatsContainer.css';

const StatCard = ({ title, value, change, type, isPositive }) => (
  <div className={`stat-card ${type}`}>
    <h3>{title}</h3>
    <div className="value">{value}</div>
    <div className={`change ${isPositive ? 'positive' : 'negative'}`}>
      <i className={`fas fa-arrow-${isPositive ? 'up' : 'down'}`}></i>
      {change}
    </div>
  </div>
);

const StatsContainer = () => {
  const [stats, setStats] = useState([
    {
      title: 'ATTACKS BLOCKED',
      value: '0',
      change: 'Real-time',
      type: 'danger',
      isPositive: false
    },
    {
      title: 'MALICIOUS REQUESTS',
      value: '0',
      change: 'Real-time',
      type: 'warning',
      isPositive: true
    },
    {
      title: 'CLEAN TRAFFIC',
      value: '0',
      change: 'Real-time',
      type: 'success',
      isPositive: true
    },
    {
      title: 'UPTIME',
      value: '00:00:00',
      change: 'No attacks yet',
      type: 'info',
      isPositive: true
    }
  ]);

  // Function to fetch stats
  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/dashboard/stats');
      console.log('Received stats:', response.data);
      
      if (Array.isArray(response.data)) {
        setStats(response.data);
      } else {
        console.error('Invalid stats data format:', response.data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Function to update uptime timer
  const updateUptime = () => {
    setStats(prevStats => {
      return prevStats.map(stat => {
        if (stat.title === 'UPTIME') {
          // Only update if we have a valid uptime value
          if (stat.value !== '00:00:00' && stat.change === 'Since last attack') {
            const [hours, minutes, seconds] = stat.value.split(':').map(Number);
            let totalSeconds = hours * 3600 + minutes * 60 + seconds + 1;
            const newHours = Math.floor(totalSeconds / 3600);
            const newMinutes = Math.floor((totalSeconds % 3600) / 60);
            const newSeconds = totalSeconds % 60;
            return {
              ...stat,
              value: `${String(newHours).padStart(2, '0')}:${String(newMinutes).padStart(2, '0')}:${String(newSeconds).padStart(2, '0')}`
            };
          }
        }
        return stat;
      });
    });
  };

  useEffect(() => {
    // Initial fetch
    fetchStats();

    // Set up polling for stats every 5 seconds
    const statsInterval = setInterval(fetchStats, 5000);
    
    // Set up timer update every second
    const timerInterval = setInterval(updateUptime, 1000);

    // Cleanup
    return () => {
      clearInterval(statsInterval);
      clearInterval(timerInterval);
    };
  }, []);

  return (
    <div className="stats-container">
      {stats.map((stat, index) => (
        <StatCard key={index} {...stat} />
      ))}
    </div>
  );
};

export default StatsContainer;
