import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import api from "./api";
import "./App.css";
import TaglineSection from "./TaglineSection";
import Login from "./Login";
import Register from "./Register";
import SalaryDashboard from "./SalaryDashboard";
import UserDashboard from "./UserDashboard";
import ProductDashboard from "./ProductDashboard";
import Navbar from "./Navbar";
import { AuthProvider, useAuth } from "./AuthContext";

// Component to protect private routes
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
};

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/salaries" element={
            <ProtectedRoute>
              <SalaryDashboard />
            </ProtectedRoute>
          } />
          <Route path="/users" element={
            <ProtectedRoute>
              <UserDashboard />
            </ProtectedRoute>
          } />
          <Route path="/" element={
            <ProtectedRoute>
              <ProductDashboard />
            </ProtectedRoute>
          } />
        </Routes>
      </AuthProvider>
    </Router>
  );
}
