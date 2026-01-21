import { useLocation } from 'react-router-dom';
import { Sun, Moon } from 'lucide-react';
import { useMeetingStore, useAudioStore } from '@/store';
import { formatDuration } from '@/utils/formatters';
import './Header.css';

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/meeting': 'Active Meeting',
  '/history': 'Meeting History',
  '/settings': 'Settings',
};

export function Header() {
  const location = useLocation();
  const { currentMeeting } = useMeetingStore();
  const { isRecording, duration } = useAudioStore();

  const title = currentMeeting?.title || pageTitles[location.pathname] || 'Meeting Assistant';

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">{title}</h1>
        {isRecording && (
          <div className="recording-indicator">
            <span className="recording-dot" />
            <span className="recording-time">{formatDuration(duration)}</span>
          </div>
        )}
      </div>

      <div className="header-right">
        <ThemeToggle />
      </div>
    </header>
  );
}

function ThemeToggle() {
  const toggleTheme = () => {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  };

  return (
    <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
      <Sun className="theme-icon light" />
      <Moon className="theme-icon dark" />
    </button>
  );
}
