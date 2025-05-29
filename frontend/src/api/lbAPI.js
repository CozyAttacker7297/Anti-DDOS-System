import axios from 'axios';

const API = 'http://<your-backend-ip>:8000/load_balancer';

export const registerServer = (ip) => axios.post(`${API}/register_server/`, null, {
    params: { ip }
});

export const getNextServer = () => axios.get(`${API}/next_server/`);

export const listServers = () => axios.get(`${API}/servers/`);
