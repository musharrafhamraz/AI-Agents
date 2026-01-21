// Recording Controls Component
// Main control panel for audio recording

import { Play, Pause, Square, Mic, Settings } from 'lucide-react';
import { VolumeMeter, Waveform } from './VolumeMeter';
import './RecordingControls.css';

interface RecordingControlsProps {
  isRecording: boolean;
  isPaused: boolean;
  duration: string;
  volume: number;
  onStart: () => void;
  onPause: () => void;
  onResume: () => void;
  onStop: () => void;
  onSettings?: () => void;
  disabled?: boolean;
}

export function RecordingControls({
  isRecording,
  isPaused,
  duration,
  volume,
  onStart,
  onPause,
  onResume,
  onStop,
  onSettings,
  disabled = false,
}: RecordingControlsProps) {
  return (
    <div className="recording-controls">
      {/* Left: Duration and Status */}
      <div className="controls-left">
        <span className="recording-duration">{duration}</span>
        {isRecording && (
          <div className="recording-status">
            <span className={`status-dot ${isPaused ? 'paused' : 'recording'}`} />
            <span className="status-text">
              {isPaused ? 'Paused' : 'Recording'}
            </span>
          </div>
        )}
      </div>

      {/* Center: Control Buttons */}
      <div className="controls-center">
        {!isRecording ? (
          <button
            className="control-btn primary large"
            onClick={onStart}
            disabled={disabled}
            aria-label="Start recording"
          >
            <Mic className="btn-icon" />
            <span>Start Recording</span>
          </button>
        ) : (
          <>
            <button
              className="control-btn secondary"
              onClick={isPaused ? onResume : onPause}
              aria-label={isPaused ? 'Resume recording' : 'Pause recording'}
            >
              {isPaused ? <Play className="btn-icon" /> : <Pause className="btn-icon" />}
              <span>{isPaused ? 'Resume' : 'Pause'}</span>
            </button>

            <div className="recording-indicator">
              <Waveform isRecording={!isPaused} volume={volume} />
            </div>

            <button
              className="control-btn danger"
              onClick={onStop}
              aria-label="Stop recording"
            >
              <Square className="btn-icon" />
              <span>Stop</span>
            </button>
          </>
        )}
      </div>

      {/* Right: Volume and Settings */}
      <div className="controls-right">
        {isRecording && (
          <VolumeMeter 
            volume={volume} 
            isActive={!isPaused}
            size="md"
          />
        )}
        {onSettings && (
          <button
            className="settings-btn"
            onClick={onSettings}
            aria-label="Audio settings"
            disabled={isRecording}
          >
            <Settings className="settings-icon" />
          </button>
        )}
      </div>
    </div>
  );
}
