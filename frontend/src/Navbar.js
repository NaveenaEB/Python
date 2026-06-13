import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './AuthContext';

export default function Navbar() {
    const { logout } = useAuth();

    return (
        <header className="topbar">
            <div className="brand">
                <span className="brand-badge">🚀</span>
                <h1>Enterprise Portal</h1>
            </div>
            <nav className="top-actions">
                <Link to="/" className="btn btn-light">Products</Link>
                <Link to="/salaries" className="btn btn-light">Salaries</Link>
                <Link to="/users" className="btn btn-light">Users</Link>
                <button className="btn btn-delete" onClick={logout}>
                    Logout
                </button>
            </nav>
        </header>
    );
}