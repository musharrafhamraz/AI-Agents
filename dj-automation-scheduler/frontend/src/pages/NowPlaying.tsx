import { useEffect, useState, useRef } from 'react';
import { nowPlayingApi } from '../api/client';
import type { NowPlaying as NowPlayingType } from '../api/client';

export default function NowPlaying() {
  const [nowPlaying, setNowPlaying] = useState<NowPlayingType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    // Update current time every second
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timeInterval);
  }, []);

  const fetchNowPlaying = async () => {
    try {
      console.log('Fetching now playing...');
      const response = await nowPlayingApi.getNowPlaying();
      const data = response.data;
      console.log('Now playing data:', data);
      setNowPlaying(data);
      
      // If playing, set audio source and seek position
      if (data.is_playing && data.current_asset && audioRef.current) {
        console.log('Setting audio source:', data.current_asset.audio_url);
        console.log('Seeking to position:', data.seek_position);
        
        // Only update source if it changed
        if (audioRef.current.src !== data.current_asset.audio_url) {
          audioRef.current.src = data.current_asset.audio_url;
        }
        
        audioRef.current.currentTime = data.seek_position || 0;
        audioRef.current.play().catch(err => {
          console.error('Autoplay prevented:', err);
          console.log('Click the play button to start');
        });
      } else if (!data.is_playing && audioRef.current && !audioRef.current.paused) {
        // Stop playing if nothing is scheduled
        console.log('Stopping playback - nothing scheduled');
        audioRef.current.pause();
      }
      
      setLoading(false);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching now playing:', err);
      setError(err.message || 'Failed to fetch data');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNowPlaying();
    
    // Poll every 5 seconds for more responsive updates
    const interval = setInterval(fetchNowPlaying, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black flex items-center justify-center">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black flex items-center justify-center">
        <div className="text-white text-center">
          <h1 className="text-3xl font-bold mb-4">Connection Error</h1>
          <p className="text-red-400 mb-4">{error}</p>
          <p className="text-gray-300">Make sure the backend is running at http://localhost:8000</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-violet-500">
            DJ Live Stream
          </h1>
          <div className="flex items-center justify-center gap-4 mb-2">
            <div className={`w-3 h-3 rounded-full ${nowPlaying?.is_playing ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`}></div>
            <span className="text-xl">{nowPlaying?.is_playing ? 'LIVE' : 'OFFLINE'}</span>
          </div>
          <div className="text-sm text-gray-400">
            Current Time: {currentTime.toLocaleTimeString()}
          </div>
          <button
            onClick={fetchNowPlaying}
            className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm"
          >
            🔄 Refresh Now
          </button>
        </div>

        {/* Now Playing Card */}
        {nowPlaying?.is_playing && nowPlaying.current_asset ? (
          <div className="max-w-4xl mx-auto bg-white bg-opacity-10 backdrop-blur-lg rounded-3xl p-8 mb-8 shadow-2xl">
            <div className="text-center mb-6">
              <div className="text-sm text-gray-300 mb-2">NOW PLAYING</div>
              <h2 className="text-4xl font-bold mb-2">{nowPlaying.current_asset.title}</h2>
              <div className="inline-block px-4 py-1 bg-purple-500 bg-opacity-30 rounded-full text-sm">
                {nowPlaying.current_asset.type.toUpperCase()}
              </div>
            </div>

            {/* Audio Player */}
            <div className="mb-6">
              <audio
                ref={audioRef}
                controls
                className="w-full"
              />
            </div>

            {/* Progress Info */}
            <div className="flex justify-between text-sm text-gray-300">
              <span>Current Position: {formatTime(nowPlaying.seek_position || 0)}</span>
              <span>Duration: {formatTime(nowPlaying.current_asset.duration_seconds)}</span>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto bg-white bg-opacity-10 backdrop-blur-lg rounded-3xl p-12 mb-8 text-center">
            <div className="text-6xl mb-4">🎵</div>
            <h2 className="text-3xl font-bold mb-4">Nothing Playing Right Now</h2>
            <p className="text-gray-300">{nowPlaying?.message}</p>
          </div>
        )}

        {/* Up Next */}
        {nowPlaying?.next_event && (
          <div className="max-w-4xl mx-auto bg-white bg-opacity-5 backdrop-blur-lg rounded-2xl p-6">
            <h3 className="text-2xl font-bold mb-4">Up Next</h3>
            <div className="flex justify-between items-center">
              <div>
                <div className="text-xl font-semibold">{nowPlaying.next_event.audio_asset?.title}</div>
                <div className="text-sm text-gray-400">
                  {nowPlaying.next_event.audio_asset?.type.toUpperCase()}
                </div>
              </div>
              <div className="text-right text-sm text-gray-400">
                <div>Starts at</div>
                <div className="font-semibold">{formatDateTime(nowPlaying.next_event.start_at)}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
