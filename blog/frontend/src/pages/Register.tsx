import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { fetchApi } from '../lib/api';

export default function Register() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    const form = e.target as HTMLFormElement;
    
    const username = (form.elements.namedItem('username') as HTMLInputElement).value;
    const email = (form.elements.namedItem('email') as HTMLInputElement).value;
    const password = (form.elements.namedItem('password') as HTMLInputElement).value;
    const confirmPassword = (form.elements.namedItem('confirmPassword') as HTMLInputElement).value;

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    try {
      await fetchApi('/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });
      navigate('/login');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="col-md-8 col-lg-6 mx-auto mt-4 mt-lg-5">
      <div className="content-section py-5 px-4 px-md-5 mb-4 text-center">
        <h2 className="mb-2" style={{ fontSize: '2rem', fontWeight: 800 }}>Create an Account</h2>
        <p className="text-body-secondary mb-4 pb-2">Join us today to start publishing your thoughts.</p>
        
        {error && <div className="alert alert-danger mb-4">{error}</div>}

        <form onSubmit={handleSubmit} className="text-start">
          <div className="mb-4">
            <label htmlFor="username" className="form-label text-uppercase text-muted" style={{ fontSize: '0.75rem', letterSpacing: '0.05em' }}>Username</label>
            <input type="text" className="form-control form-control-lg" id="username" name="username" placeholder="alex_developer" required minLength={1} maxLength={50} />
          </div>
          <div className="mb-4">
            <label htmlFor="email" className="form-label text-uppercase text-muted" style={{ fontSize: '0.75rem', letterSpacing: '0.05em' }}>Email Address</label>
            <input type="email" className="form-control form-control-lg" id="email" name="email" placeholder="name@example.com" required />
          </div>
          <div className="mb-4">
            <label htmlFor="password" className="form-label text-uppercase text-muted" style={{ fontSize: '0.75rem', letterSpacing: '0.05em' }}>Password</label>
            <input type="password" className="form-control form-control-lg" id="password" name="password" placeholder="••••••••" required minLength={8} />
            <div className="form-text mt-2"><i className="bi bi-info-circle"></i> Must be at least 8 characters.</div>
          </div>
          <div className="mb-4">
            <label htmlFor="confirmPassword" className="form-label text-uppercase text-muted" style={{ fontSize: '0.75rem', letterSpacing: '0.05em' }}>Confirm Password</label>
            <input type="password" className="form-control form-control-lg" id="confirmPassword" name="confirmPassword" placeholder="••••••••" required minLength={8} />
          </div>
          <div className="d-grid gap-2 mt-4 pt-2">
            <button type="submit" className="btn btn-primary w-100 mt-2" disabled={isLoading}>
              {isLoading ? (
                <><span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registering...</>
              ) : 'Register Account'}
            </button>
          </div>
        </form>
        
        <div className="mt-4 pt-3 border-top border-light-subtle">
          <p className="mb-0 text-body-secondary" style={{ fontSize: '0.95rem' }}>
            Already have an account? <Link to="/login" style={{ fontWeight: 600 }}>Sign in here</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
