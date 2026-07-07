import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { fetchApi } from '../lib/api';
import type { PaginatedPostsResponse, PostResponse, UserPublic } from '../types/api';

export default function UserPosts() {
  const { userId } = useParams();
  const [posts, setPosts] = useState<PostResponse[]>([]);
  const [user, setUser] = useState<UserPublic | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const limit = 10;

  useEffect(() => {
    const loadData = async () => {
      try {
        const [userRes, postsRes] = await Promise.all([
          fetchApi<UserPublic>(`/users/${userId}`),
          fetchApi<PaginatedPostsResponse>(`/users/${userId}/posts?skip=0&limit=${limit}`)
        ]);
        setUser(userRes);
        setPosts(postsRes.posts);
        setHasMore(postsRes.has_more);
      } catch (error) {
        console.error('Failed to load user data', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [userId]);

  const loadMorePosts = async () => {
    const nextPage = page + 1;
    const skip = nextPage * limit;
    try {
      const postsRes = await fetchApi<PaginatedPostsResponse>(`/users/${userId}/posts?skip=${skip}&limit=${limit}`);
      setPosts(prev => [...prev, ...postsRes.posts]);
      setHasMore(postsRes.has_more);
      setPage(nextPage);
    } catch (error) {
      console.error('Failed to load more posts', error);
    }
  };

  if (isLoading) {
    return <div className="text-center py-5"><span className="spinner-border" /></div>;
  }

  if (!user) {
    return <div className="text-center py-5">User not found.</div>;
  }

  return (
    <>
      <h1 className="mb-4 h3 fw-bold border-bottom pb-2">Posts by {user.username}</h1>
      <div id="postsContainer">
        {posts.map(post => (
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
        ))}
      </div>
      <div className="text-center mt-4 mb-5">
        {hasMore ? (
          <button 
            className="btn btn-outline-primary px-4 py-2 rounded"
            onClick={loadMorePosts}
          >
            Load more
          </button>
        ) : (
          <button className="btn btn-outline-secondary px-4 py-2 rounded" disabled>
            No more posts
          </button>
        )}
      </div>
    </>
  );
}
