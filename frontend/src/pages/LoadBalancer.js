import React, { useEffect, useState } from 'react';
import { registerServer, getNextServer, listServers } from '../api/lbAPI';

export default function LoadBalancer() {
  const [serverIp, setServerIp] = useState('');
  const [servers, setServers] = useState([]);
  const [nextServer, setNextServer] = useState('');

  useEffect(() => {
    fetchServers();
  }, []);

  const fetchServers = async () => {
    const res = await listServers();
    setServers(res.data.servers);
  };

  const handleRegister = async () => {
    if (serverIp) {
      await registerServer(serverIp);
      setServerIp('');
      fetchServers();
    }
  };

  const handleNextServer = async () => {
    const res = await getNextServer();
    setNextServer(res.data.next_server);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Load Balancer Control</h2>

      <div className="mb-4">
        <input
          type="text"
          value={serverIp}
          onChange={(e) => setServerIp(e.target.value)}
          placeholder="Enter server IP"
          className="border p-2 mr-2"
        />
        <button onClick={handleRegister} className="bg-blue-600 text-white px-4 py-2 rounded">Register Server</button>
      </div>

      <div className="mb-4">
        <button onClick={handleNextServer} className="bg-green-600 text-white px-4 py-2 rounded">Get Next Server</button>
        {nextServer && <p className="mt-2">Next Server: {nextServer}</p>}
      </div>

      <h3 className="text-lg font-semibold">Registered Servers</h3>
      <ul className="list-disc list-inside">
        {servers.map((ip, idx) => (
          <li key={idx}>{ip}</li>
        ))}
      </ul>
    </div>
  );
}
