import React, { useState, useEffect, useCallback } from 'react';
import api from './api'; // Adjust the path to your axios instance
import Navbar from './Navbar';
import TaglineSection from "./TaglineSection";
import { useAuth } from "./AuthContext";

const ProductDashboard = () => {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [searchText, setSearchText] = useState('');
  const [status, setStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Form state for Add/Edit
  const [form, setForm] = useState({
    Name: "",
    price: "",
    quantity: "",
    status: "ordered",
    description: ""
  });
  const [editId, setEditId] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Function to call the POST /products/filter endpoint
  const handleSearch = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.post('/products/filter', {
        search_text: searchText.trim() || null,
        status: status || null
      });
      setProducts(response.data.data || []); // Ensure it's an array even if data is null
    } catch (error) {
      console.error("Failed to fetch filtered products:", error);
      setError("Failed to fetch products");
    } finally {
      setIsLoading(false);
    }
  }, [searchText, status]);

  // Load all products on component mount
  useEffect(() => {
    handleSearch();
  }, [handleSearch]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const resetForm = () => {
    setForm({ Name: "", price: "", quantity: "", status: "ordered", description: "" });
    setEditId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage("");
    setError("");
    try {
      const payload = {
        ...form,
        price: parseFloat(form.price),
        quantity: parseInt(form.quantity),
        user_id: user?.id || 1
      };
      if (editId) {
        await api.put(`/products/${editId}`, payload);
        setMessage("Product updated successfully");
      } else {
        await api.post("/products", payload);
        setMessage("Product created successfully");
      }
      resetForm();
      handleSearch();
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
    setIsLoading(false);
  };

  const handleEdit = (product) => {
    setForm({
      Name: product.Name || product.name,
      price: product.price,
      quantity: product.quantity,
      status: product.status || "ordered",
      description: product.description || ""
    });
    setEditId(product.id);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this product?")) return;
    try {
      await api.delete(`/products/${id}`);
      setMessage("Product deleted successfully");
      handleSearch();
    } catch (err) {
      setError("Delete failed");
    }
  };

  return (
    <div className="app-bg">
      <Navbar />
      <div className="container">
        <div className="stats">
          <div className="chip">Total: {products.length}</div>
          <div className="search">
            <input
              type="text"
              placeholder="Search by name or description..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
            <select value={status} onChange={(e) => setStatus(e.target.value)} style={{ marginLeft: '10px', padding: '10px', borderRadius: '10px', border: '1px solid #e5e7eb' }}>
              <option value="">All Statuses</option>
              <option value="ordered">Ordered</option>
              <option value="shipped">Shipped</option>
              <option value="delivered">Delivered</option>
            </select>
            <button className="btn" onClick={handleSearch} style={{ marginLeft: '10px' }} disabled={isLoading}>Search</button>
          </div>
        </div>

        <div className="content-grid">
          <div className="card form-card">
            <h2>{editId ? "Edit Product" : "Add Product"}</h2>
            <form onSubmit={handleSubmit} className="product-form">
              <input type="text" name="Name" placeholder="Name" value={form.Name} onChange={handleChange} required />
              <input type="number" name="price" placeholder="Price" value={form.price} onChange={handleChange} required step="0.01" />
              <input type="number" name="quantity" placeholder="Quantity" value={form.quantity} onChange={handleChange}  />
              <select name="status" value={form.status} onChange={handleChange}>
                <option value="ordered">Ordered</option>
                <option value="shipped">Shipped</option>
                <option value="delivered">Delivered</option>
              </select>
              <input type="text" name="description" placeholder="Description" value={form.description} onChange={handleChange} style={{ gridColumn: '1 / -1' }} />
              <div className="form-actions">
                <button className="btn" type="submit" disabled={isLoading}>{editId ? "Update" : "Add"}</button>
                {editId && <button className="btn btn-secondary" type="button" onClick={resetForm}>Cancel</button>}
              </div>
            </form>
            {message && <div className="success-msg">{message}</div>}
            {error && <div className="error-msg">{error}</div>}
          </div>

          <TaglineSection />

          <div className="card list-card">
            <h2>Product Catalog</h2>
            <div className="product-list scroll-x">
              {products.length > 0 ? (
                <table className="product-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Status</th>
                      <th>Price</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map(p => (
                      <tr key={p.id}>
                        <td>{p.id}</td>
                        <td className="name-cell">{p.Name || p.name}</td>
                        <td><span className="qty-badge" style={{ textTransform: 'uppercase' }}>{p.status}</span></td>
                        <td className="price-cell">${p.price.toFixed(2)}</td>
                        <td>
                          <div className="row-actions">
                            <button className="btn btn-edit" onClick={() => handleEdit(p)}>Edit</button>
                            <button className="btn btn-delete" onClick={() => handleDelete(p.id)}>Delete</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                !isLoading && <p className="empty">No products found matching your criteria.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDashboard;