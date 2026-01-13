import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';

const RegisterPage = () => {
  const { register, loading, user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    role: 'STUDENT' as 'TEACHER' | 'STUDENT'
  });
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      navigate(`/${user.role.toLowerCase()}`);
    }
  }, [user, navigate]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');

    // Validation
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (form.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    if (!form.fullName.trim()) {
      setError('Full name is required');
      return;
    }

    try {
      await register({
        email: form.email,
        password: form.password,
        full_name: form.fullName,
        role: form.role.toLowerCase() as 'teacher' | 'student'
      });
    } catch (err) {
      setError('Unable to register. Please try again.');
      console.error(err);
    }
  };

  return (
    <main className="auth-layout">
      <section className="auth-card">
        <h1>Create Account</h1>
        <p className="muted">
          Join the AI-Powered Virtual Classroom platform
        </p>
        
        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            Full Name
            <input
              type="text"
              value={form.fullName}
              onChange={(e) => setForm({ ...form, fullName: e.target.value })}
              required
              placeholder="John Smith"
            />
          </label>

          <label>
            Email
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
              placeholder="john@school.edu"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              minLength={6}
              placeholder="At least 6 characters"
            />
          </label>

          <label>
            Confirm Password
            <input
              type="password"
              value={form.confirmPassword}
              onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
              required
              placeholder="Confirm your password"
            />
          </label>

          <label>
            I am a:
            <select
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value as 'TEACHER' | 'STUDENT' })}
              required
            >
              <option value="STUDENT">Student</option>
              <option value="TEACHER">Teacher</option>
            </select>
          </label>

          {error && <p className="error-text">{error}</p>}
          
          <button type="submit" disabled={loading}>
            {loading ? 'Creating Account…' : 'Create Account'}
          </button>
        </form>

        <div className="auth-links">
          <p>
            Already have an account? <Link to="/login">Sign in here</Link>
          </p>
        </div>
      </section>
    </main>
  );
};

export default RegisterPage;