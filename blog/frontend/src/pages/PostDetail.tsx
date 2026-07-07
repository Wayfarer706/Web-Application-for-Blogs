import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { fetchApi } from '../lib/api';
import type { PostResponse } from '../types/api';

export default function PostDetail() {
  const { postId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [post, setPost] = useState<PostResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadPost = async () => {
      try {
        const response = await fetchApi<PostResponse>(`/posts/${postId}`);
        setPost(response);
      } catch (error) {
        console.error('Failed to load post', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadPost();
  }, [postId]);

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const title = (form.elements.namedItem('title') as HTMLInputElement).value;
    const content = (form.elements.namedItem('content') as HTMLTextAreaElement).value;

    try {
      const response = await fetchApi<PostResponse>(`/posts/${postId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      setPost(response);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update post', error);
      alert('Failed to update post');
    }
  };

  const handleDelete = async () => {
    try {
      await fetchApi(`/posts/${postId}`, { method: 'DELETE' });
      navigate('/');
    } catch (error) {
      console.error('Failed to delete post', error);
      alert('Failed to delete post');
    }
  };

  if (isLoading) {
    return <div className="text-center py-5"><span className="spinner-border" /></div>;
  }

  if (!post) {
    return <div className="text-center py-5">Post not found.</div>;
  }

  if (isEditing) {
    return (
      <article className="content-section py-4 px-4 border rounded mb-4">
        <h4 className="mb-4">Edit Post</h4>
        <form onSubmit={handleEditSubmit}>
          <div className="mb-3">
            <label htmlFor="editTitle" className="form-label text-muted small text-uppercase">Title</label>
            <input type="text" className="form-control" id="editTitle" name="title" defaultValue={post.title} required />
          </div>
          <div className="mb-3">
            <label htmlFor="editContent" className="form-label text-muted small text-uppercase">Content</label>
            <textarea className="form-control" id="editContent" name="content" rows={8} defaultValue={post.content} required></textarea>
          </div>
          <div className="d-flex gap-2 mt-4">
            <button type="submit" className="btn btn-primary px-4">Save Changes</button>
            <button type="button" className="btn btn-outline-secondary px-4" onClick={() => setIsEditing(false)}>Cancel</button>
          </div>
        </form>
      </article>
    );
  }

  return (
    <article className="content-section py-4 px-4 border rounded mb-4">
      <div className="d-flex align-items-start gap-3">
        <img 
          className="rounded-circle object-fit-cover border"
          src={post.author.image_path.startsWith('http') ? post.author.image_path : `http://localhost:8000${post.author.image_path}`}
          alt={`${post.author.username}'s profile picture`}
          width="48"
          height="48"
          loading="lazy" 
        />
        <div className="flex-grow-1">
          <div className="d-flex align-items-center justify-content-between mb-3 border-bottom pb-2">
            <div>
              <Link className="text-decoration-none fw-semibold me-2" to={`/users/${post.author.id}/posts`}>
                {post.author.username}
              </Link>
              <small className="text-muted">{new Date(post.date_posted).toLocaleDateString()}</small>
            </div>
            
            {user && user.id === post.author.id && (
              <div className="dropdown">
                <button className="btn btn-sm btn-link text-muted text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                  Options
                </button>
                <ul className="dropdown-menu dropdown-menu-end shadow-sm">
                  <li><button className="dropdown-item" type="button" onClick={() => setIsEditing(true)}>Edit Post</button></li>
                  <li><button className="dropdown-item text-danger" type="button" onClick={() => setIsDeleting(true)}>Delete Post</button></li>
                </ul>
              </div>
            )}
          </div>
          
          <h2 className="mb-3 fw-bold h3">
            {post.title}
          </h2>
          
          <p className="mb-0" style={{ fontSize: '1.05rem', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
            {post.content}
          </p>

          {isDeleting && (
            <div className="mt-4 p-3 bg-danger bg-opacity-10 border border-danger-subtle rounded d-flex align-items-center justify-content-between">
              <div>
                <strong className="text-danger d-block">Are you sure you want to delete this post?</strong>
                <span className="text-danger small">This action cannot be undone.</span>
              </div>
              <div className="d-flex gap-2">
                <button className="btn btn-sm btn-danger" onClick={handleDelete}>Yes, delete</button>
                <button className="btn btn-sm btn-outline-secondary" onClick={() => setIsDeleting(false)}>Cancel</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </article>
  );
}
