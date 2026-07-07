import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="col-md-8 col-lg-6 mx-auto mt-5 pt-3">
      <div className="content-section py-5 px-4 px-md-5 mb-4 text-center shadow-sm rounded-4 border-top border-4 border-danger">
        <div className="mb-4 text-danger">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" className="bi bi-exclamation-triangle" viewBox="0 0 16 16">
            <path d="M7.938 2.016A.13.13 0 0 1 8.002 2a.13.13 0 0 1 .063.016.146.146 0 0 1 .054.057l6.857 11.667c.036.06.035.124.002.183a.163.163 0 0 1-.054.06.116.116 0 0 1-.066.017H1.146a.115.115 0 0 1-.066-.017.163.163 0 0 1-.054-.06.176.176 0 0 1 .002-.183L7.884 2.073a.147.147 0 0 1 .054-.057zm1.044-.45a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566z"/>
            <path d="M7.002 12a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 5.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995z"/>
          </svg>
        </div>
        <h1 className="mb-3" style={{ fontWeight: 800, fontSize: '2.5rem' }}>404 Error</h1>
        <p className="text-body-secondary mb-4" style={{ fontSize: '1.1rem' }}>The page you are looking for does not exist.</p>
        <Link to="/" className="btn btn-primary px-4">Return Home</Link>
      </div>
    </div>
  );
}
