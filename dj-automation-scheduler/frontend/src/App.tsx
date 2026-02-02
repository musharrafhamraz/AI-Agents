import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import NowPlaying from './pages/NowPlaying';
import Admin from './pages/Admin';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <Routes>
          <Route path="/" element={<NowPlaying />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
        
        {/* Navigation */}
        <div style={{
          position: 'fixed',
          bottom: '16px',
          right: '16px',
          display: 'flex',
          gap: '8px',
          zIndex: 50
        }}>
          <Link
            to="/"
            style={{
              backgroundColor: '#9333ea',
              color: 'white',
              padding: '8px 16px',
              borderRadius: '8px',
              textDecoration: 'none',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
              transition: 'background-color 0.2s'
            }}
          >
            Now Playing
          </Link>
          <Link
            to="/admin"
            style={{
              backgroundColor: '#2563eb',
              color: 'white',
              padding: '8px 16px',
              borderRadius: '8px',
              textDecoration: 'none',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
              transition: 'background-color 0.2s'
            }}
          >
            Admin
          </Link>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
