import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchApi } from '../lib/api';

export default function ForgotPassword() {
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    const form = e.target as HTMLFormElement;
    const email = (form.elements.namedItem('email') as HTMLInputElement).value;

    try {
      await fetchApi('/users/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Failed to request password reset');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="col-md-8 col-lg-6 mx-auto mt-4 mt-lg-5">
      <div className="content-section py-5 px-4 px-md-5 mb-4 text-center">
        <h2 className="mb-2" style={{ fontSize: '2rem', fontWeight: 800 }}>Forgot Password</h2>
        <p className="text-body-secondary mb-4 pb-2">Enter your email address and we'll send you a link to reset your password.</p>
        
        {error && <div className="alert alert-danger">{error}</div>}

        {success ? (
          <div className="alert alert-success">
            Password reset link sent! Please check your email.
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="text-start">
            <div className="mb-4">
              <label htmlFor="email" className="form-label text-uppercase text-muted" style={{ fontSize: '0.75rem', letterSpacing: '0.05em' }}>Email Address</label>
              <input type="email" className="form-control form-control-lg" id="email" name="email" placeholder="name@example.com" required autoFocus />
            </div>
            <div className="d-grid gap-2 mt-4 pt-2">
              <button type="submit" className="btn btn-primary w-100 mt-2" disabled={isLoading}>
                {isLoading ? (
                  <><span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sending...</>
                ) : 'Send Reset Link'}
              </button>
            </div>
          </form>
        )}
        
        <div className="mt-4 pt-3 border-top border-light-subtle">
          <p className="mb-0 text-body-secondary" style={{ fontSize: '0.95rem' }}>
            Remember your password? <Link to="/login" style={{ fontWeight: 600 }}>Sign in here</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
