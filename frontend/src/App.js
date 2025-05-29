import React from 'react';
import { Routes, Route } from 'react-router-dom';
import LoadBalancer from './pages/LoadBalancer';      // adjust if path differs
import Dashboard from './components/Dashboard/Dashboard';  // adjust path
import ServerHealth from './components/Server/ServerHealth';
import './App.css';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/load-balancer" element={<LoadBalancer />} />
        <Route path="/server-health" element={<ServerHealth />} />
        <Route path="/servers" element={<ServerHealth />} />
      </Routes>
    </div>
  );
}

export default App;

