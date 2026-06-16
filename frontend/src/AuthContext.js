import React, { createContext, useState, useContext, useEffect } from 'react';
import api from './api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token && token !== 'undefined' && token !== 'null') {
            // In a real app, you'd decode the JWT to get user details like ID and email
            // For now, we'll assume a valid token means a logged-in user
            // You might want to make an API call to /users/me to get actual user data
            setUser({ id: 1, isAuthenticated: true, email: 'user@example.com' }); 
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const formData = new FormData();
        // FastAPI's OAuth2PasswordRequestForm expects 'username' for email
        formData.append('username', email);
        formData.append('password', password);
        
        const response = await api.post('/auth/login', formData);
        // Access nested data because of the ApiResponse wrapper
        localStorage.setItem('token', response.data.data.access_token);
        localStorage.setItem('refresh_token', response.data.data.refresh_token);
        // In a real app, you'd decode the JWT or fetch user details to set the user state
        setUser({ id: 1, isAuthenticated: true, email: email }); 
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token'); // Also clear refresh token on logout
        setUser(null);
        window.location.href = "/login";
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error("useAuth must be used within an AuthProvider");
    return context;
};