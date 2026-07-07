import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
});

const normalizeStoredToken = (rawValue) => {
    if (!rawValue) return null;
    const cleaned = rawValue.toString().trim().replace(/['"]+/g, '');
    return cleaned === 'undefined' || cleaned === 'null' || cleaned === '' ? null : cleaned;
};

const getStoredToken = () => normalizeStoredToken(localStorage.getItem('token'));
const getStoredRefreshToken = () => normalizeStoredToken(localStorage.getItem('refresh_token'));

// Variables to handle token refreshing logic
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

api.interceptors.request.use((config) => {
    const token = getStoredToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    } else {
        delete config.headers.Authorization;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Check if error is 401 and the request hasn't been retried yet
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            
            if (isRefreshing) {
                // If a refresh is already in progress, queue this request
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                })
                .then(token => {
                    originalRequest.headers.Authorization = `Bearer ${token}`;
                    return api(originalRequest);
                })
                .catch(err => Promise.reject(err));
            }

            originalRequest._retry = true;
            isRefreshing = true;

            return new Promise((resolve, reject) => {
                const refreshToken = getStoredRefreshToken();
                
                if (!refreshToken) {
                    isRefreshing = false;
                    localStorage.removeItem('token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login';
                    return reject(error);
                }

                // Send the refresh token in the body as expected by the backend
                api.post('/auth/refresh', { refresh_token: refreshToken })
                    .then(({ data }) => {
                        const newToken = data.data.access_token;
                        localStorage.setItem('token', newToken);
                        
                        // Update the current and future request headers
                        api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
                        originalRequest.headers.Authorization = `Bearer ${newToken}`;
                        
                        processQueue(null, newToken);
                        resolve(api(originalRequest));
                    })
                    .catch((err) => {
                        processQueue(err, null);
                        localStorage.removeItem('token');
                        window.location.href = '/login';
                        reject(err);
                    })
                    .finally(() => {
                        isRefreshing = false;
                    });
            });
        }
        return Promise.reject(error);
    }
);

export default api;