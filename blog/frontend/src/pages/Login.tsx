import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { fetchApi } from '../lib/api';
import type { Token } from '../types/api';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    const form = e.target as HTMLFormElement;
    
    const formData = new URLSearchParams();
    formData.append('username', (form.elements.namedItem('username') as HTMLInputElement).value);
    formData.append('password', (form.elements.namedItem('password') as HTMLInputElement).value);

    try {
      const response = await fetchApi<Token>('/users/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });
      await login(response.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="col-md-8 col-lg-6 mx-auto mt-4 mt-lg-5">
      <div className="content-section py-5 px-4 px-md-5 mb-4 text-center">
        <h2 className="mb-2" style={{ fontSize: '2rem', fontWeight: 800 }}>Welcome Back</h2>
        <p className="text-body-secondary mb-4 pb-2">Log in to access your account and continue reading.</p>
        
        {error && <div className="alert alert-danger mb-4">{error}</div>}

        <form onSubmit={handleSubmit} className="text-start">
          <div className="mb-4">
            <label htmlFor="email" className="form-label text-uppercase text-muted" style={{ fontSize: '0.75rem', letterSpacing: '0.05em' }}>Email Address</label>
            <input type="email" className="form-control form-control-lg" id="email" name="username" placeholder="name@example.com" required />
          </div>
          <div className="mb-4">
            <div className="d-flex justify-content-between align-items-center mb-1">
              <label htmlFor="password" className="form-label text-uppercase text-muted mb-0" style={{ fontSize: '0.75rem', letterSpacing: '0.05em' }}>Password</label>
              <Link to="/forgot-password" className="text-decoration-none" style={{ fontSize: '0.825rem', fontWeight: 500 }}>Forgot password?</Link>
            </div>
            <input type="password" className="form-control form-control-lg" id="password" name="password" placeholder="••••••••" required />
          </div>
          <div className="d-grid gap-2 mt-4 pt-2">
            <button type="submit" className="btn btn-primary w-100 mt-2" disabled={isLoading}>
              {isLoading ? (
                <><span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Signing in...</>
              ) : 'Sign in to your account'}
            </button>
          </div>
        </form>
        
        <div className="mt-4 pt-3 border-top border-light-subtle">
          <p className="mb-0 text-body-secondary" style={{ fontSize: '0.95rem' }}>
            Don't have an account? <Link to="/register" style={{ fontWeight: 600 }}>Create one now</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
