import React, { useEffect, useState } from 'react';
import { serverApi } from '../services/api';

const ConnectionTest: React.FC = () => {
    const [status, setStatus] = useState<string>('Testing connection...');
    const [error, setError] = useState<string | null>(null);
    const [responseData, setResponseData] = useState<any>(null);

    useEffect(() => {
        const testConnection = async () => {
            try {
                console.log('Attempting to connect to backend...');
                const response = await serverApi.testConnection();
                console.log('Backend response:', response.data);
                setResponseData(response.data);
                setStatus(`Connected! Message: ${response.data.message}`);
                setError(null);
            } catch (err) {
                console.error('Connection test error:', err);
                setError(err instanceof Error ? err.message : 'Failed to connect to backend');
                setStatus('Connection failed');
            }
        };

        testConnection();
    }, []);

    return (
        <div style={{ 
            padding: '20px', 
            margin: '20px', 
            border: '1px solid #ccc',
            borderRadius: '5px',
            backgroundColor: error ? '#fff3f3' : '#f3fff3'
        }}>
            <h3>Backend Connection Test</h3>
            <p>Status: {status}</p>
            {error && <p style={{ color: 'red' }}>Error: {error}</p>}
            {responseData && (
                <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#f8f9fa' }}>
                    <h4>Response Data:</h4>
                    <pre>{JSON.stringify(responseData, null, 2)}</pre>
                </div>
            )}
            <div style={{ marginTop: '10px', fontSize: '0.9em', color: '#666' }}>
                <p>API URL: {process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}</p>
            </div>
        </div>
    );
};

export default ConnectionTest; 