// Audio Device Selector Component

import { Mic, Volume2, RefreshCw, AlertCircle } from 'lucide-react';
import type { AudioDevice } from '@/services/audioCapture';
import './AudioDeviceSelector.css';

interface AudioDeviceSelectorProps {
  devices: AudioDevice[];
  selectedDevice: string | null;
  onSelectDevice: (deviceId: string) => void;
  onRefresh: () => void;
  error?: string | null;
  disabled?: boolean;
}

export function AudioDeviceSelector({
  devices,
  selectedDevice,
  onSelectDevice,
  onRefresh,
  error,
  disabled = false,
}: AudioDeviceSelectorProps) {
  return (
    <div className="audio-device-selector">
      <div className="selector-header">
        <div className="selector-label">
          <Mic className="label-icon" />
          <span>Audio Input</span>
        </div>
        <button 
          className="refresh-button"
          onClick={onRefresh}
          disabled={disabled}
          title="Refresh devices"
        >
          <RefreshCw className="refresh-icon" />
        </button>
      </div>

      {error && (
        <div className="selector-error">
          <AlertCircle className="error-icon" />
          <span>{error}</span>
        </div>
      )}

      <div className="device-list">
        {devices.length === 0 ? (
          <div className="no-devices">
            <span>No audio devices found</span>
            <button onClick={onRefresh}>Check permissions</button>
          </div>
        ) : (
          devices.map((device) => (
            <label
              key={device.deviceId}
              className={`device-option ${selectedDevice === device.deviceId ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
            >
              <input
                type="radio"
                name="audioDevice"
                value={device.deviceId}
                checked={selectedDevice === device.deviceId}
                onChange={() => onSelectDevice(device.deviceId)}
                disabled={disabled}
              />
              <div className="device-info">
                <Volume2 className="device-icon" />
                <span className="device-name">{device.label}</span>
              </div>
              <div className="device-check" />
            </label>
          ))
        )}
      </div>
    </div>
  );
}
