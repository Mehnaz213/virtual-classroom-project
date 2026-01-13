import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';

const presetCredentials = [
  { label: 'Demo Teacher', email: 'teacher@example.com', password: 'teach123' },
  { label: 'Student 1', email: 'student1@example.com', password: 'study123' },
  { label: 'Student 2', email: 'student2@example.com', password: 'study123' },
];

const LoginPage = () => {
  const { login, loading, user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      navigate(`/${user.role}`);
    }
  }, [user, navigate]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    try {
      await login(form.email, form.password);
    } catch (err) {
      setError('Unable to login. Please check credentials.');
      console.error(err);
    }
  };

  return (
    <main className="auth-layout">
      <section className="auth-card">
        <h1>AI-Powered Virtual Classroom</h1>
        <p className="muted">
          Monitor engagement, enforce lock mode, and keep remote learners focused.
        </p>
        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            Email
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
              placeholder="teacher@example.com"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </label>
          {error && <p className="error-text">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
        <div className="preset-container">
          <p>Need demo credentials?</p>
          <div className="preset-buttons">
            {presetCredentials.map((cred) => (
              <button
                key={cred.email}
                type="button"
                onClick={() => setForm({ email: cred.email, password: cred.password })}
              >
                {cred.label}
              </button>
            ))}
          </div>
        </div>
        
        <div className="auth-links">
          <p>
            Don't have an account? <Link to="/register">Create one here</Link>
          </p>
        </div>
      </section>
    </main>
  );
};

export default LoginPage;

