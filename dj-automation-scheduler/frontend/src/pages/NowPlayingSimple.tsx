import { useEffect, useState } from 'react';

export default function NowPlayingSimple() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/now-playing')
      .then(res => res.json())
      .then(data => {
        console.log('Data received:', data);
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error:', err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: 'linear-gradient(to bottom right, #581c87, #1e3a8a, #000000)',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <h1 style={{ fontSize: '32px' }}>Loading...</h1>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: 'linear-gradient(to bottom right, #581c87, #1e3a8a, #000000)',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        padding: '20px'
      }}>
        <h1 style={{ fontSize: '32px', color: '#ef4444', marginBottom: '20px' }}>Error</h1>
        <p style={{ fontSize: '18px' }}>{error}</p>
        <p style={{ fontSize: '14px', marginTop: '20px', color: '#9ca3af' }}>
          Make sure backend is running at http://localhost:8000
        </p>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(to bottom right, #581c87, #1e3a8a, #000000)',
      color: 'white',
      padding: '40px'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ 
          fontSize: '60px', 
          fontWeight: 'bold', 
          textAlign: 'center',
          marginBottom: '40px',
          background: 'linear-gradient(to right, #ec4899, #8b5cf6)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          DJ Live Stream
        </h1>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '10px',
          marginBottom: '40px'
        }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: data?.is_playing ? '#ef4444' : '#6b7280',
            animation: data?.is_playing ? 'pulse 2s infinite' : 'none'
          }}></div>
          <span style={{ fontSize: '20px' }}>
            {data?.is_playing ? 'LIVE' : 'OFFLINE'}
          </span>
        </div>

        <div style={{
          backgroundColor: 'rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '24px',
          padding: '40px',
          textAlign: 'center'
        }}>
          {data?.is_playing && data?.current_asset ? (
            <>
              <div style={{ fontSize: '14px', color: '#d1d5db', marginBottom: '10px' }}>
                NOW PLAYING
              </div>
              <h2 style={{ fontSize: '36px', fontWeight: 'bold', marginBottom: '10px' }}>
                {data.current_asset.title}
              </h2>
              <div style={{
                display: 'inline-block',
                padding: '8px 16px',
                backgroundColor: 'rgba(168, 85, 247, 0.3)',
                borderRadius: '20px',
                fontSize: '14px'
              }}>
                {data.current_asset.type.toUpperCase()}
              </div>
            </>
          ) : (
            <>
              <div style={{ fontSize: '60px', marginBottom: '20px' }}>🎵</div>
              <h2 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '20px' }}>
                Nothing Playing Right Now
              </h2>
              <p style={{ color: '#d1d5db' }}>{data?.message}</p>
            </>
          )}
        </div>

        {data?.next_event && (
          <div style={{
            backgroundColor: 'rgba(255,255,255,0.05)',
            backdropFilter: 'blur(10px)',
            borderRadius: '16px',
            padding: '24px',
            marginTop: '20px'
          }}>
            <h3 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '16px' }}>
              Up Next
            </h3>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: '20px', fontWeight: '600' }}>
                  {data.next_event.audio_asset?.title}
                </div>
                <div style={{ fontSize: '14px', color: '#9ca3af' }}>
                  {data.next_event.audio_asset?.type.toUpperCase()}
                </div>
              </div>
              <div style={{ textAlign: 'right', fontSize: '14px', color: '#9ca3af' }}>
                <div>Starts at</div>
                <div style={{ fontWeight: '600' }}>
                  {new Date(data.next_event.start_at).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
