import React, { createContext, useState, useContext, useEffect } from 'react';
import api from './api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            // In a production app, verify the token or decode it (e.g., using jwt-decode) to get user info
            setUser({ id: 1, isAuthenticated: true }); // Restoring user session with default/stored ID
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        
        const response = await api.post('/auth/login', formData);
        localStorage.setItem('token', response.data.access_token);
        setUser({ id: 1, isAuthenticated: true }); // In a real app, you'd decode the JWT or fetch user details
    };

    const logout = () => {
        localStorage.removeItem('token');
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