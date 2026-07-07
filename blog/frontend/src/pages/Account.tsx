import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { fetchApi } from '../lib/api';
import type { UserPrivate } from '../types/api';

export default function Account() {
  const { user, logout, updateUser } = useAuth();
  const [isDeleting, setIsDeleting] = useState(false);
  const [infoError, setInfoError] = useState('');
  const [infoSuccess, setInfoSuccess] = useState(false);
  const [pwdError, setPwdError] = useState('');
  const [pwdSuccess, setPwdSuccess] = useState(false);
  const [picError, setPicError] = useState('');

  if (!user) {
    return <div className="text-center py-5">Please log in to view this page.</div>;
  }

  const handleDeleteAccount = async () => {
    try {
      await fetchApi(`/users/${user.id}`, { method: 'DELETE' });
      logout();
    } catch (err: any) {
      alert('Failed to delete account');
    }
  };

  const handleInfoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setInfoError('');
    setInfoSuccess(false);
    const form = e.target as HTMLFormElement;
    const username = (form.elements.namedItem('username') as HTMLInputElement).value;
    const email = (form.elements.namedItem('email') as HTMLInputElement).value;

    try {
      const updatedUser = await fetchApi<UserPrivate>(`/users/${user.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email }),
      });
      updateUser(updatedUser);
      setInfoSuccess(true);
    } catch (err: any) {
      setInfoError(err.message || 'Failed to update info');
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwdError('');
    setPwdSuccess(false);
    const form = e.target as HTMLFormElement;
    const current_password = (form.elements.namedItem('current_password') as HTMLInputElement).value;
    const new_password = (form.elements.namedItem('new_password') as HTMLInputElement).value;
    const confirm_new_password = (form.elements.namedItem('confirm_new_password') as HTMLInputElement).value;

    if (new_password !== confirm_new_password) {
      setPwdError('New passwords do not match');
      return;
    }

    try {
      await fetchApi('/users/me/password', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_password, new_password }),
      });
      setPwdSuccess(true);
      form.reset();
    } catch (err: any) {
      setPwdError(err.message || 'Failed to change password');
    }
  };

  const handlePictureUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setPicError('');
      const updatedUser = await fetchApi<UserPrivate>(`/users/${user.id}/picture`, {
        method: 'PATCH',
        body: formData,
      });
      updateUser(updatedUser);
    } catch (err: any) {
      setPicError(err.message || 'Failed to upload picture');
    }
  };

  return (
    <div className="content-section py-4 px-4 border rounded mb-5">
      <div className="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
        <h2 className="mb-0 fw-bold h4">Account Settings</h2>
      </div>

      <div className="d-flex align-items-center gap-4 mb-4 pb-4 border-bottom">
        <div className="position-relative">
          <img 
            className="rounded-circle object-fit-cover border" 
            src={user.image_path.startsWith('http') ? user.image_path : `http://localhost:8000${user.image_path}`} 
            alt="Profile picture" 
            width="96" 
            height="96" 
          />
          <div className="mt-2">
            <input type="file" id="profilePicInput" className="d-none" accept="image/*" onChange={handlePictureUpload} />
            <label htmlFor="profilePicInput" className="btn btn-sm btn-outline-secondary">Change Picture</label>
          </div>
          {picError && <div className="text-danger small mt-1">{picError}</div>}
        </div>
        <div>
          <h4 className="mb-1 fw-bold h5">{user.username}</h4>
          <p className="text-muted small mb-0">{user.email}</p>
        </div>
      </div>

      <div className="row g-5">
        <div className="col-md-6">
          <h5 className="mb-4 h6 fw-bold">Personal Information</h5>
          {infoError && <div className="alert alert-danger">{infoError}</div>}
          {infoSuccess && <div className="alert alert-success">Profile updated successfully.</div>}
          <form onSubmit={handleInfoSubmit}>
            <div className="mb-3">
              <label htmlFor="username" className="form-label text-uppercase text-muted small">Username</label>
              <input type="text" className="form-control" id="username" name="username" required minLength={1} maxLength={50} defaultValue={user.username} />
            </div>
            <div className="mb-3">
              <label htmlFor="email" className="form-label text-uppercase text-muted small">Email Address</label>
              <input type="email" className="form-control" id="email" name="email" required defaultValue={user.email} />
            </div>
            <button type="submit" className="btn btn-primary px-4 mt-2">Save Changes</button>
          </form>
        </div>

        <div className="col-md-6">
          <h5 className="mb-4 h6 fw-bold">Security</h5>
          {pwdError && <div className="alert alert-danger">{pwdError}</div>}
          {pwdSuccess && <div className="alert alert-success">Password changed successfully.</div>}
          <form onSubmit={handlePasswordSubmit}>
            <div className="mb-3">
              <label htmlFor="currentPassword" className="form-label text-uppercase text-muted small">Current Password</label>
              <input type="password" className="form-control" id="currentPassword" name="current_password" required placeholder="••••••••" />
            </div>
            <div className="mb-3">
              <label htmlFor="newPassword" className="form-label text-uppercase text-muted small">New Password</label>
              <input type="password" className="form-control" id="newPassword" name="new_password" required minLength={8} placeholder="••••••••" />
            </div>
            <div className="mb-3">
              <label htmlFor="confirmNewPassword" className="form-label text-uppercase text-muted small">Confirm Password</label>
              <input type="password" className="form-control" id="confirmNewPassword" name="confirm_new_password" required minLength={8} placeholder="••••••••" />
            </div>
            <button type="submit" className="btn btn-outline-primary px-4 mt-2">Update Password</button>
          </form>
        </div>
      </div>

      <div className="mt-5 pt-4 border-top border-danger-subtle">
        <h5 className="text-danger mb-3 h6 fw-bold">Danger Zone</h5>
        {isDeleting ? (
          <div className="p-4 bg-danger bg-opacity-10 border border-danger-subtle rounded d-flex flex-column gap-3">
            <div>
              <strong className="text-danger d-block">Are you absolutely sure?</strong>
              <span className="text-danger small">This action cannot be undone. All your posts will be permanently removed.</span>
            </div>
            <div className="d-flex gap-2">
              <button className="btn btn-danger" onClick={handleDeleteAccount}>Yes, delete my account</button>
              <button className="btn btn-outline-secondary" onClick={() => setIsDeleting(false)}>Cancel</button>
            </div>
          </div>
        ) : (
          <div className="d-flex justify-content-between align-items-center p-4 bg-danger bg-opacity-10 border border-danger-subtle rounded">
            <div>
              <h6 className="text-danger mb-1 fw-semibold">Delete Account</h6>
              <p className="text-danger-emphasis mb-0 small">
                Once you delete your account, there is no going back.
              </p>
            </div>
            <button type="button" className="btn btn-danger" onClick={() => setIsDeleting(true)}>
              Delete Account
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
