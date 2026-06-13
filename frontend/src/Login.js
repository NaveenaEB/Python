import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await login(email, password);
            navigate('/');
        } catch (err) {
            alert("Invalid credentials");
        }
    };

    return (
        <div className="auth-container">
            <div className="card form-card">
                <h2>Login</h2>
                <form onSubmit={handleSubmit} className="product-form">
                    <input type="email" placeholder="Email" onChange={e => setEmail(e.target.value)} required />
                    <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} required />
                    <button className="btn" type="submit">Sign In</button>
                </form>
                <p className="mt-4">
                    Don't have an account? <Link to="/register">Register here</Link>
                </p>
            </div>
        </div>
    );
}