import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
});

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
    let token = localStorage.getItem('token');
    if (token) {
        // Clean the token: remove quotes and any accidental "Bearer " prefix stored in it
        const cleanToken = token.replace(/['"]+/g, '').replace(/^Bearer\s+/i, '');
        config.headers.Authorization = `Bearer ${cleanToken}`;
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
                const rawRefreshToken = localStorage.getItem('refresh_token');
                
                // If no refresh token exists, or it's literally the string "undefined", abort
                if (!rawRefreshToken || rawRefreshToken === "undefined") {
                    isRefreshing = false;
                    localStorage.removeItem('token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login';
                    return reject(error);
                }

                const cleanRefreshToken = rawRefreshToken.replace(/['"]+/g, '');
                
                // Send the refresh token in the body as expected by the backend
                api.post('/auth/refresh', { refresh_token: cleanRefreshToken })
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