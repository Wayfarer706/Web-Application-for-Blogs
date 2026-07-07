import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { fetchApi } from '../lib/api';

export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    const form = e.target as HTMLFormElement;
    const new_password = (form.elements.namedItem('new_password') as HTMLInputElement).value;
    const confirm_password = (form.elements.namedItem('confirm_password') as HTMLInputElement).value;

    if (new_password !== confirm_password) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    if (!token) {
      setError('Invalid or missing reset token');
      setIsLoading(false);
      return;
    }

    try {
      await fetchApi('/users/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password }),
      });
      navigate('/login');
    } catch (err: any) {
      setError(err.message || 'Failed to reset password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="col-md-8 col-lg-6 mx-auto mt-4 mt-lg-5">
      <div className="content-section py-5 px-4 px-md-5 mb-4 text-center">
        <h2 className="mb-2" style={{ fontSize: '2rem', fontWeight: 800 }}>Reset Password</h2>
        <p className="text-body-secondary mb-4 pb-2">Enter your new password below.</p>
        
        {error && <div className="alert alert-danger">{error}</div>}

        <form onSubmit={handleSubmit} className="text-start">
          <div className="mb-4">
            <label htmlFor="newPassword" className="form-label text-uppercase text-muted" style={{ fontSize: '0.75rem', letterSpacing: '0.05em' }}>New Password</label>
            <input type="password" className="form-control form-control-lg" id="newPassword" name="new_password" placeholder="••••••••" required minLength={8} autoFocus />
            <div className="form-text mt-2"><i className="bi bi-info-circle"></i> Password must be at least 8 characters.</div>
          </div>
          <div className="mb-4">
            <label htmlFor="confirmPassword" className="form-label text-uppercase text-muted" style={{ fontSize: '0.75rem', letterSpacing: '0.05em' }}>Confirm New Password</label>
            <input type="password" className="form-control form-control-lg" id="confirmPassword" name="confirm_password" placeholder="••••••••" required minLength={8} />
          </div>
          <div className="d-grid gap-2 mt-4 pt-2">
            <button type="submit" className="btn btn-primary w-100 mt-2" disabled={isLoading}>
              {isLoading ? (
                <><span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Resetting...</>
              ) : 'Reset Password'}
            </button>
          </div>
        </form>
        
        <div className="mt-4 pt-3 border-top border-light-subtle">
          <p className="mb-0 text-body-secondary" style={{ fontSize: '0.95rem' }}>
            Remember your password? <Link to="/login" style={{ fontWeight: 600 }}>Sign in here</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
