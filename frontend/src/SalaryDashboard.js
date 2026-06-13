import React, { useEffect, useState, useCallback, useMemo } from "react";
import api from "./api";
import Navbar from "./Navbar";
import { useAuth } from "./AuthContext";

export default function SalaryDashboard() {
  const { user } = useAuth();
  const [salaries, setSalaries] = useState([]);
  const [form, setForm] = useState({ 
    amount: "", 
    month: "", 
    year: "", 
    employee_id: user?.id || 1 
  });
  const [editId, setEditId] = useState(null);
  const [users, setUsers] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState("");
  const [sortField, setSortField] = useState("id");
  const [sortDirection, setSortDirection] = useState("asc");

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

  const fetchSalaries = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get("/salaries/");
      setSalaries(res.data);
    } catch (err) {
      setError("Failed to fetch salaries");
    }
    setLoading(false);
  }, []);

  const fetchUsers = useCallback(async () => {
    try {
      const res = await api.get("/users/");
      setUsers(res.data);
    } catch (err) {
      console.error("Failed to fetch users");
    }
  }, []);

  useEffect(() => { 
    fetchSalaries(); 
    fetchUsers();
  }, [fetchSalaries, fetchUsers]);

  const handleSort = (field) => {
    const isAsc = sortField === field && sortDirection === "asc";
    setSortDirection(isAsc ? "desc" : "asc");
    setSortField(field);
  };

  const filteredSalaries = useMemo(() => {
    let filtered = [...salaries];
    const q = filter.trim().toLowerCase();
    if (q) {
      filtered = filtered.filter((s) =>
        String(s.employee_id).includes(q) || s.month?.toLowerCase().includes(q));
    }
    return filtered.sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];
      if (typeof aVal === 'string') aVal = aVal.toLowerCase();
      if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
      if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });
  }, [salaries, filter, sortField, sortDirection]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const resetForm = () => {
    setForm({ amount: "", month: "", year: "", employee_id: user?.id || 1 });
    setEditId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        amount: parseFloat(form.amount || 0),
        month: form.month,
        year: parseInt(form.year || new Date().getFullYear()),
        employee_id: parseInt(form.employee_id || user?.id || 1)
      };
      if (editId) {
        await api.put(`/salaries/${editId}`, payload);
        setMessage("Record updated");
      } else {
        await api.post("/salaries/", payload);
        setMessage("Record created");
      }
      resetForm();
      fetchSalaries();
    } catch (err) {
      setError("Operation failed");
    }
    setLoading(false);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this record?")) return;
    try {
      await api.delete(`/salaries/${id}`);
      fetchSalaries();
    } catch (err) {
      setError("Delete failed");
    }
  };

  const currency = (n) =>
    typeof n === "number" ? n.toFixed(2) : Number(n || 0).toFixed(2);

  return (
    <div className="app-bg">
      <Navbar />
      <div className="container">
        <div className="stats">
          <div className="chip">Total Records: {salaries.length}</div>
          <div className="search">
            <input
              type="text"
              placeholder="Search by ID or month..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
        </div>
        <div className="content-grid">
          <div className="card form-card">
            <h2>{editId ? "Edit Salary" : "Add Salary"}</h2>
            <form onSubmit={handleSubmit} className="product-form">
              <input type="number" name="amount" placeholder="Amount" value={form.amount} onChange={handleChange} required step="0.01" />
              <input type="text" name="month" placeholder="Month" value={form.month} onChange={handleChange} required />
              <input type="number" name="year" placeholder="Year" value={form.year} onChange={handleChange} required />
              <select 
                name="employee_id" 
                value={form.employee_id} 
                onChange={handleChange} 
                required
              >
                <option value="">Select User</option>
                {users.map(u => (
                  <option key={u.id} value={u.id}>{u.name} ({u.email})</option>
                ))}
              </select>
              <div className="form-actions">
                <button className="btn" type="submit" disabled={loading}>
                  {editId ? "Update" : "Add"}
                </button>
                {editId && (
                  <button
                    className="btn btn-secondary"
                    type="button"
                    onClick={() => {
                      resetForm();
                      setMessage("");
                      setError("");
                    }}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
            {message && <div className="success-msg">{message}</div>}
            {error && <div className="error-msg">{error}</div>}
          </div>

          <div className="card list-card">
            <h2>Salary Records</h2>
            <div className="scroll-x">
              <table className="product-table">
                <thead>
                  <tr>
                    <th 
                      className={`sortable ${sortField === 'employee_id' ? `sort-${sortDirection}` : ''}`}
                      onClick={() => handleSort('employee_id')}
                    >
                      User ID
                    </th>
                    <th 
                      className={`sortable ${sortField === 'amount' ? `sort-${sortDirection}` : ''}`}
                      onClick={() => handleSort('amount')}
                    >
                      Amount
                    </th>
                    <th 
                      className={`sortable ${sortField === 'year' ? `sort-${sortDirection}` : ''}`}
                      onClick={() => handleSort('year')}
                    >
                      Month/Year
                    </th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSalaries.map((s) => (
                    <tr key={s.id}>
                      <td>{s.employee_id}</td>
                      <td className="price-cell">${currency(s.amount)}</td>
                      <td>{s.month} {s.year}</td>
                      <td>
                        <div className="row-actions">
                          <button className="btn btn-edit" onClick={() => {
                            setEditId(s.id); 
                            setForm({
                              amount: s.amount,
                              month: s.month,
                              year: s.year,
                              employee_id: s.employee_id
                            });
                          }}>Edit</button>
                          <button className="btn btn-delete" onClick={() => handleDelete(s.id)}>Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}