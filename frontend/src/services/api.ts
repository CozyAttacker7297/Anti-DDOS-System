import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// Types
interface ApiError {
    message: string;
    status: number;
    data?: any;
}

interface RetryConfig {
    retries: number;
    retryDelay: number;
    retryStatusCodes: number[];
}

interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
    retryCount?: number;
}

// Default retry configuration
const defaultRetryConfig: RetryConfig = {
    retries: 3,
    retryDelay: 1000,
    retryStatusCodes: [408, 429, 500, 502, 503, 504]
};

// Create axios instance with default config
const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // Important for cookies/auth
    timeout: 10000, // 10 second timeout
});

// Log API configuration
console.log('API Configuration:', {
    baseURL: api.defaults.baseURL,
    headers: api.defaults.headers,
    withCredentials: api.defaults.withCredentials,
    timeout: api.defaults.timeout
});

// Error handler
const handleError = (error: AxiosError): ApiError => {
    if (error.response) {
        // Server responded with error
        const responseData = error.response.data as { detail?: string };
        return {
            message: responseData?.detail || 'Server error occurred',
            status: error.response.status,
            data: error.response.data
        };
    } else if (error.request) {
        // Request made but no response
        return {
            message: 'No response from server',
            status: 0
        };
    } else {
        // Request setup error
        return {
            message: error.message,
            status: 0
        };
    }
};

// Retry interceptor
const retryInterceptor = async (error: AxiosError, retryConfig: RetryConfig = defaultRetryConfig) => {
    const config = error.config as CustomAxiosRequestConfig;
    if (!config) return Promise.reject(error);

    const currentRetryCount = config.retryCount ?? 0;

    if (currentRetryCount >= retryConfig.retries) {
        return Promise.reject(error);
    }

    if (error.response && retryConfig.retryStatusCodes.includes(error.response.status)) {
        config.retryCount = currentRetryCount + 1;
        await new Promise(resolve => setTimeout(resolve, retryConfig.retryDelay * config.retryCount!));
        return api(config);
    }

    return Promise.reject(error);
};

// Request interceptor for adding auth token
api.interceptors.request.use(
    (config: CustomAxiosRequestConfig) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(handleError(error));
    }
);

// Response interceptor for handling errors
api.interceptors.response.use(
    (response: AxiosResponse) => response,
    async (error: AxiosError) => {
        const handledError = handleError(error);

        // Handle specific error cases
        switch (handledError.status) {
            case 401:
                // Handle unauthorized access
                localStorage.removeItem('auth_token');
                window.location.href = '/login';
                break;
            case 403:
                // Handle forbidden access
                console.error('Access forbidden');
                break;
            case 429:
                // Handle rate limiting
                console.error('Rate limit exceeded');
                break;
        }

        // Attempt retry for certain status codes
        return retryInterceptor(error);
    }
);

// API endpoints with type safety
interface Server {
    id: number;
    name: string;
    ip_address: string;
    is_active: boolean;
}

interface ServerCreate {
    name: string;
    ip_address: string;
}

interface SecurityEvent {
    id: number;
    event_type: string;
    description: string;
    timestamp: string;
}

interface BlockedIP {
    id: number;
    ip: string;
    reason: string;
    blocked_at: string;
}

interface AttackLog {
    id: number;
    type: string;
    source_ip: string;
    target: string;
    severity: string;
    action: string;
    timestamp: string;
}

// API endpoints
export const serverApi = {
    getServers: () => api.get<Server[]>('/servers'),
    createServer: (data: ServerCreate) => api.post<Server>('/servers', data),
    deleteServer: (id: number) => api.delete(`/servers/${id}`),
    getServerHealth: () => api.get('/server-health'),
    testConnection: () => api.get<{ status: string; message: string; timestamp: number }>('/test-connection'),
};

export const securityApi = {
    getAlerts: () => api.get<SecurityEvent[]>('/alerts'),
    getSecurityEvents: () => api.get<SecurityEvent[]>('/security-events'),
    getBlockedIPs: () => api.get<BlockedIP[]>('/blocked-ips'),
    blockIP: (data: { ip: string; reason: string }) => api.post<BlockedIP>('/block-ip', data),
    getAttackLogs: () => api.get<AttackLog[]>('/attack-logs'),
};

export default api; 