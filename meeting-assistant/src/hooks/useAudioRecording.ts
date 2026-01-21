// React hook for audio capture

import { useState, useEffect, useCallback, useRef } from 'react';
import { audioCapture, AudioDevice, RecordingState } from '@/services/audioCapture';

export interface UseAudioRecordingReturn {
    // State
    devices: AudioDevice[];
    selectedDevice: string | null;
    state: RecordingState;
    error: string | null;

    // Actions
    selectDevice: (deviceId: string) => void;
    startRecording: () => Promise<boolean>;
    pauseRecording: () => void;
    resumeRecording: () => void;
    stopRecording: () => Promise<void>;

    // Utilities
    refreshDevices: () => Promise<void>;
    formattedDuration: string;
}

export function useAudioRecording(): UseAudioRecordingReturn {
    const [devices, setDevices] = useState<AudioDevice[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<string | null>(null);
    const [state, setState] = useState<RecordingState>({
        isRecording: false,
        isPaused: false,
        duration: 0,
        volume: 0,
    });
    const [error, setError] = useState<string | null>(null);

    const durationInterval = useRef<number | null>(null);

    // Load devices on mount
    useEffect(() => {
        refreshDevices();

        return () => {
            if (durationInterval.current) {
                clearInterval(durationInterval.current);
            }
        };
    }, []);

    // Subscribe to volume changes
    useEffect(() => {
        const unsubscribe = audioCapture.onVolumeChange((volume) => {
            setState(prev => ({ ...prev, volume }));
        });

        return unsubscribe;
    }, []);

    const refreshDevices = useCallback(async () => {
        try {
            const audioDevices = await audioCapture.getAudioDevices();
            setDevices(audioDevices);

            // Auto-select first device if none selected
            if (!selectedDevice && audioDevices.length > 0) {
                setSelectedDevice(audioDevices[0].deviceId);
            }

            setError(null);
        } catch (err) {
            setError('Failed to access audio devices. Please check permissions.');
            console.error(err);
        }
    }, [selectedDevice]);

    const selectDevice = useCallback((deviceId: string) => {
        setSelectedDevice(deviceId);
    }, []);

    const startRecording = useCallback(async (): Promise<boolean> => {
        setError(null);

        try {
            const success = await audioCapture.startRecording(selectedDevice || undefined);

            if (success) {
                setState(prev => ({ ...prev, isRecording: true, isPaused: false, duration: 0 }));

                // Start duration ticker
                durationInterval.current = window.setInterval(() => {
                    const currentState = audioCapture.getState();
                    setState(prev => ({ ...prev, duration: currentState.duration }));
                }, 100);

                return true;
            } else {
                setError('Failed to start recording');
                return false;
            }
        } catch (err) {
            setError('Failed to start recording. Please check microphone permissions.');
            console.error(err);
            return false;
        }
    }, [selectedDevice]);

    const pauseRecording = useCallback(() => {
        audioCapture.pauseRecording();
        setState(prev => ({ ...prev, isPaused: true }));
    }, []);

    const resumeRecording = useCallback(() => {
        audioCapture.resumeRecording();
        setState(prev => ({ ...prev, isPaused: false }));
    }, []);

    const stopRecording = useCallback(async () => {
        // Stop duration ticker
        if (durationInterval.current) {
            clearInterval(durationInterval.current);
            durationInterval.current = null;
        }

        await audioCapture.stopRecording();

        setState({
            isRecording: false,
            isPaused: false,
            duration: 0,
            volume: 0,
        });
    }, []);

    // Format duration as MM:SS or HH:MM:SS
    const formattedDuration = formatDuration(state.duration);

    return {
        devices,
        selectedDevice,
        state,
        error,
        selectDevice,
        startRecording,
        pauseRecording,
        resumeRecording,
        stopRecording,
        refreshDevices,
        formattedDuration,
    };
}

function formatDuration(ms: number): string {
    const totalSeconds = Math.floor(ms / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    if (hours > 0) {
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}
