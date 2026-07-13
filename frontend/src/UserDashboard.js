import React, { useEffect, useState, useMemo } from "react";
import api from "./api";
import Navbar from "./Navbar";

export default function UserDashboard() {
  const [users, setUsers] = useState([]);
  console.log("Users state:", users); // Debugging line
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [filter, setFilter] = useState("");
  const [form, setForm] = useState({ name: "", email: "", password: "", is_active: true });
  const [editId, setEditId] = useState(null);

  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => setMessage(""), 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(""), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await api.get("/users");
      setUsers(res?.data?.data || []); // Access nested data
    } catch (err) {
      setError("Failed to fetch users");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const filteredUsers = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return users;
    return users.filter(u => 
      u.name.toLowerCase().includes(q) || 
      u.email.toLowerCase().includes(q) ||
      String(u.id).includes(q)
    );
  }, [users, filter]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };

  const resetForm = () => {
    setForm({ name: "", email: "", password: "", is_active: true });
    setEditId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");
    try {
      if (editId) {
        // UserUpdate schema: name, email, is_active
        const updatePayload = {
          name: form.name,
          email: form.email,
          is_active: form.is_active
        };
        await api.put(`/users/${editId}`, updatePayload);
        setMessage("User updated successfully");
      } else {
        // UserCreate schema: name, email, password, is_active
        await api.post("/users", form);
        setMessage("User created successfully");
      }
      resetForm();
      fetchUsers();
    } catch (err) {
      const errors = err.response?.data?.errors;
      if (Array.isArray(errors)) {
        // If FastAPI returns a list of validation errors, join their messages
        setError(errors.map(e => `${e.loc.join('.')}: ${e.msg}`).join(", "));
      } else {
        // Fallback to the error message or a generic message
        setError(err.response?.data?.message || "Operation failed");
      }
    }
    setLoading(false);
  };

  const handleEdit = (user) => {
    setForm({
      name: user.name,
      email: user.email,
      password: "", // Passwords are not returned by the API
      is_active: user.is_active
    });
    setEditId(user.id);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    try {
      await api.delete(`/users/${id}`);
      setMessage("User deleted successfully");
      fetchUsers();
    } catch (err) {
      setError("Failed to delete user");
    }
  };

  return (
    <div className="app-bg">
      <Navbar />
      <div className="container">
        <div className="stats">
          <div className="chip">Total Users: {users.length}</div>
          <div className="search">
            <input
              type="text"
              placeholder="Search by name or email..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
        </div>

        <div className="content-grid">
          <div className="card form-card">
            <h2>{editId ? "Edit User" : "Add New User"}</h2>
            <form onSubmit={handleSubmit} className="product-form">
              <input
                type="text"
                name="name"
                placeholder="Full Name"
                value={form.name}
                onChange={handleChange}
                required
              />
              <input
                type="email"
                name="email"
                placeholder="Email Address"
                value={form.email}
                onChange={handleChange}
                required
              />
              {!editId && (
                <input
                  type="password"
                  name="password"
                  placeholder="Password"
                  value={form.password}
                  onChange={handleChange}
                  required
                />
              )}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 0' }}>
                <input
                  type="checkbox"
                  name="is_active"
                  id="is_active"
                  checked={form.is_active}
                  onChange={handleChange}
                  style={{ width: 'auto' }}
                />
                <label htmlFor="is_active" style={{ fontSize: '14px', color: 'var(--text-700)' }}>
                  Active Account
                </label>
              </div>
              <div className="form-actions">
                <button className="btn" type="submit" disabled={loading}>
                  {editId ? "Update User" : "Create User"}
                </button>
                {editId && (
                  <button className="btn btn-secondary" type="button" onClick={resetForm}>
                    Cancel
                  </button>
                )}
              </div>
            </form>
            {message && <div className="success-msg">{message}</div>}
            {error && <div className="error-msg">{error}</div>}
          </div>

          <div className="card list-card">
            <h2>Registered Users</h2>
            {loading && !users.length ? (
              <div className="loader">Loading...</div>
            ) : (
              <div className="scroll-x">
                <table className="product-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((u) => (
                      <tr key={u.id}>
                        <td>{u.id}</td>
                        <td className="name-cell">{u.name}</td>
                        <td>{u.email}</td>
                        <td>
                          <span className={`qty-badge ${u.is_active ? 'active' : 'inactive'}`} style={{ 
                            background: u.is_active ? '#dcfce7' : '#fee2e2',
                            color: u.is_active ? '#166534' : '#991b1b',
                            borderColor: u.is_active ? '#bbf7d0' : '#fecaca'
                          }}>
                            {u.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                        <td>
                          <div className="row-actions">
                            <button className="btn btn-edit" onClick={() => handleEdit(u)}>Edit</button>
                            <button className="btn btn-delete" onClick={() => handleDelete(u.id)}>Delete</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {filteredUsers.length === 0 && (
                      <tr>
                        <td colSpan={5} className="empty">No users found.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}