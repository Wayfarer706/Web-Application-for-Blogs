import { useEffect, useState } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Layout() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'auto');
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  useEffect(() => {
    let activeTheme = theme;
    if (theme === 'auto') {
      activeTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    document.documentElement.setAttribute('data-bs-theme', activeTheme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const cycleTheme = () => {
    const themes = ['light', 'dark', 'auto'];
    const currentIndex = themes.indexOf(theme);
    const nextTheme = themes[(currentIndex + 1) % themes.length];
    setTheme(nextTheme);
  };

  return (
    <div className="d-flex flex-column min-vh-100">
      <header className="site-header">
        <nav className="navbar navbar-expand-md fixed-top border-bottom">
          <div className="container">
            <Link className="navbar-brand me-4 fw-bold" to="/">FastAPI Blog</Link>
            <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarToggle" aria-controls="navbarToggle" aria-expanded="false" aria-label="Toggle navigation">
              <span className="navbar-toggler-icon"></span>
            </button>
            <div className="collapse navbar-collapse" id="navbarToggle">
              <div className="navbar-nav me-auto">
                <Link className="nav-link" aria-current="page" to="/">Home</Link>
              </div>
              <div className="navbar-nav align-items-center">
                {user ? (
                  <div className="d-flex align-items-center gap-3">
                    <Link className="nav-link" to="/account">{user.username}</Link>
                    <button className="btn btn-link nav-link p-0" onClick={handleLogout}>Logout</button>
                  </div>
                ) : (
                  <div className="d-flex gap-3">
                    <Link className="nav-item nav-link p-0" to="/login">Login</Link>
                    <Link className="nav-item nav-link p-0" to="/register">Register</Link>
                  </div>
                )}
                <button className="btn btn-sm btn-outline-secondary ms-3" onClick={cycleTheme}>
                  Theme: {theme.charAt(0).toUpperCase() + theme.slice(1)}
                </button>
              </div>
            </div>
          </div>
        </nav>
      </header>

      <main role="main" className="container flex-grow-1" style={{ marginTop: '80px' }}>
        <div className="row">
          <div className="col-lg-8">
            <Outlet />
          </div>
          <aside className="col-lg-4 mt-4 mt-lg-0">
            <div className="content-section py-3 px-3 border rounded">
              <h3 className="h5 mb-3">Discover</h3>
              <p className="text-muted small mb-3">Join our community to stay up to date with the latest stories and insights.</p>
              <ul className="list-group list-group-flush border-0">
                <li className="list-group-item bg-transparent px-0 border-bottom">
                  Latest Posts
                </li>
                <li className="list-group-item bg-transparent px-0 border-bottom">
                  Announcements
                </li>
                <li className="list-group-item bg-transparent px-0 border-bottom">
                  Calendars
                </li>
                <li className="list-group-item bg-transparent px-0 border-bottom">
                  Inspiration
                </li>
              </ul>
            </div>
          </aside>
        </div>
      </main>

      <footer className="mt-auto py-3 bg-body-tertiary border-top">
        <div className="container text-center">
          <p className="text-muted small mb-0">
            © {new Date().getFullYear()} FastAPI Blog.
          </p>
        </div>
      </footer>
    </div>
  );
}
