import React, { useState } from 'react';
import api from './api';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
    const [form, setForm] = useState({ name: '', email: '', password: '', is_active: true });
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('/users', form);
            alert("Account created! Please login.");
            navigate('/login');
        } catch (err) {
            alert(err.response?.data?.detail || "Registration failed");
        }
    };

    return (
        <div className="auth-container">
            <div className="card form-card">
                <h2>Create Account</h2>
                <form onSubmit={handleSubmit} className="product-form">
                    <input type="text" placeholder="Full Name" onChange={e => setForm({...form, name: e.target.value})} required />
                    <input type="email" placeholder="Email" onChange={e => setForm({...form, email: e.target.value})} required />
                    <input type="password" placeholder="Password" onChange={e => setForm({...form, password: e.target.value})} required />
                    <button className="btn" type="submit">Register</button>
                </form>
                <p className="mt-4">
                    Already have an account? <Link to="/login">Login here</Link>
                </p>
            </div>
        </div>
    );
}