import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { fetchApi } from '../lib/api';
import type { PaginatedPostsResponse, PostResponse } from '../types/api';

export default function Home() {
  const [posts, setPosts] = useState<PostResponse[]>([]);
  const [isComposing, setIsComposing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const limit = 10;
  const { user } = useAuth();

  const loadPosts = async (skip: number) => {
    try {
      const response = await fetchApi<PaginatedPostsResponse>(`/posts?skip=${skip}&limit=${limit}`);
      if (skip === 0) {
        setPosts(response.posts);
      } else {
        setPosts(prev => [...prev, ...response.posts]);
      }
      setHasMore(response.has_more);
    } catch (error) {
      console.error('Failed to load posts', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPosts(0);
  }, []);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const title = (form.elements.namedItem('title') as HTMLInputElement).value;
    const content = (form.elements.namedItem('content') as HTMLTextAreaElement).value;

    try {
      const newPost = await fetchApi<PostResponse>('/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      setPosts([newPost, ...posts]);
      setIsComposing(false);
    } catch (error) {
      console.error('Failed to create post', error);
      alert('Failed to create post');
    }
  };

  return (
    <div id="postsContainer">
      {user && (
        <div className="mb-4">
          {isComposing ? (
            <div className="content-section py-3 px-4 border rounded">
              <h5 className="mb-3">Create New Post</h5>
              <form onSubmit={handleCreateSubmit}>
                <div className="mb-3">
                  <label htmlFor="title" className="form-label text-muted small text-uppercase">Title</label>
                  <input type="text" className="form-control" id="title" name="title" required />
                </div>
                <div className="mb-3">
                  <label htmlFor="content" className="form-label text-muted small text-uppercase">Content</label>
                  <textarea className="form-control" id="content" name="content" rows={4} required></textarea>
                </div>
                <div className="d-flex gap-2">
                  <button type="submit" className="btn btn-primary px-4">Post</button>
                  <button type="button" className="btn btn-outline-secondary px-4" onClick={() => setIsComposing(false)}>Cancel</button>
                </div>
              </form>
            </div>
          ) : (
            <button className="btn btn-outline-primary w-100 py-3 rounded" onClick={() => setIsComposing(true)}>
              What's on your mind, {user.username}?
            </button>
          )}
        </div>
      )}

      {isLoading && posts.length === 0 ? (
        <div className="text-center py-5"><span className="spinner-border" /></div>
      ) : (
        posts.map(post => (
          <article key={post.id} className="content-section py-4 px-4 border rounded mb-4">
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
                  <Link className="text-decoration-none fw-semibold me-2" to={`/users/${post.author.id}/posts`}>
                    {post.author.username}
                  </Link>
                  <small className="text-muted">{new Date(post.date_posted).toLocaleDateString()}</small>
                </div>
                <h3 className="mb-2 h4 fw-bold">
                  <Link className="text-decoration-none text-body" to={`/posts/${post.id}`}>
                    {post.title}
                  </Link>
                </h3>
                <p className="mb-0 text-body" style={{ fontSize: '1rem', lineHeight: 1.6, opacity: 0.9 }}>
                  {post.content}
                </p>
              </div>
            </div>
          </article>
        ))
      )}
      
      <div className="text-center mt-4 mb-5">
        {hasMore ? (
          <button 
            className="btn btn-outline-primary px-4 py-2 rounded"
            onClick={() => {
              const nextPage = page + 1;
              setPage(nextPage);
              loadPosts(nextPage * limit);
            }}
          >
            Load more
          </button>
        ) : (
          <button className="btn btn-outline-secondary px-4 py-2 rounded" disabled>
            No more posts
          </button>
        )}
      </div>
    </div>
  );
}
