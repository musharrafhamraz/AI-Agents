// Audio Capture Service
// Handles audio recording from microphone and system audio using Web Audio API

import { appDataDir } from '@tauri-apps/api/path';
import { writeBinaryFile, createDir } from '@tauri-apps/api/fs';

export interface AudioDevice {
    deviceId: string;
    label: string;
    kind: 'audioinput' | 'audiooutput';
}

export interface RecordingState {
    isRecording: boolean;
    isPaused: boolean;
    duration: number;
    volume: number;
}

export interface AudioChunk {
    data: Float32Array;
    timestamp: number;
    sampleRate: number;
}

type AudioCallback = (chunk: AudioChunk) => void;
type VolumeCallback = (volume: number) => void;

class AudioCaptureService {
    private mediaStream: MediaStream | null = null;
    private audioContext: AudioContext | null = null;
    private analyserNode: AnalyserNode | null = null;
    private processorNode: ScriptProcessorNode | null = null;
    private mediaRecorder: MediaRecorder | null = null;

    private recordedChunks: Blob[] = [];
    private startTime: number = 0;
    private pausedDuration: number = 0;
    private pauseStartTime: number = 0;

    private audioCallbacks: AudioCallback[] = [];
    private volumeCallbacks: VolumeCallback[] = [];
    private volumeInterval: number | null = null;

    private state: RecordingState = {
        isRecording: false,
        isPaused: false,
        duration: 0,
        volume: 0,
    };

    /**
     * Get available audio input devices
     */
    async getAudioDevices(): Promise<AudioDevice[]> {
        try {
            // Request permission first
            await navigator.mediaDevices.getUserMedia({ audio: true });

            const devices = await navigator.mediaDevices.enumerateDevices();
            return devices
                .filter(device => device.kind === 'audioinput')
                .map(device => ({
                    deviceId: device.deviceId,
                    label: device.label || `Microphone ${device.deviceId.slice(0, 8)}`,
                    kind: device.kind as 'audioinput',
                }));
        } catch (error) {
            console.error('Failed to get audio devices:', error);
            return [];
        }
    }

    /**
     * Start recording audio
     */
    async startRecording(deviceId?: string): Promise<boolean> {
        if (this.state.isRecording) {
            console.warn('Already recording');
            return false;
        }

        try {
            // Set up audio constraints
            const constraints: MediaStreamConstraints = {
                audio: {
                    deviceId: deviceId ? { exact: deviceId } : undefined,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 16000, // Good for speech recognition
                },
            };

            // Get microphone stream
            this.mediaStream = await navigator.mediaDevices.getUserMedia(constraints);

            // Set up audio context for analysis
            this.audioContext = new AudioContext({ sampleRate: 16000 });
            const source = this.audioContext.createMediaStreamSource(this.mediaStream);

            // Create analyser for volume metering
            this.analyserNode = this.audioContext.createAnalyser();
            this.analyserNode.fftSize = 256;
            source.connect(this.analyserNode);

            // Create processor for audio chunks (for transcription)
            this.processorNode = this.audioContext.createScriptProcessor(4096, 1, 1);
            source.connect(this.processorNode);
            this.processorNode.connect(this.audioContext.destination);

            this.processorNode.onaudioprocess = (event) => {
                if (this.state.isPaused) return;

                const inputData = event.inputBuffer.getChannelData(0);
                const chunk: AudioChunk = {
                    data: new Float32Array(inputData),
                    timestamp: Date.now() - this.startTime - this.pausedDuration,
                    sampleRate: this.audioContext?.sampleRate || 16000,
                };

                // Notify callbacks
                this.audioCallbacks.forEach(cb => cb(chunk));
            };

            // Set up MediaRecorder for full audio recording
            this.mediaRecorder = new MediaRecorder(this.mediaStream, {
                mimeType: 'audio/webm;codecs=opus',
            });

            this.recordedChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.recordedChunks.push(event.data);
                }
            };

            this.mediaRecorder.start(1000); // Collect data every second

            // Start volume monitoring
            this.startVolumeMonitoring();

            // Update state
            this.startTime = Date.now();
            this.pausedDuration = 0;
            this.state = {
                isRecording: true,
                isPaused: false,
                duration: 0,
                volume: 0,
            };

            console.log('Audio recording started');
            return true;
        } catch (error) {
            console.error('Failed to start recording:', error);
            this.cleanup();
            return false;
        }
    }

    /**
     * Pause recording
     */
    pauseRecording(): void {
        if (!this.state.isRecording || this.state.isPaused) return;

        this.mediaRecorder?.pause();
        this.pauseStartTime = Date.now();
        this.state.isPaused = true;

        console.log('Audio recording paused');
    }

    /**
     * Resume recording
     */
    resumeRecording(): void {
        if (!this.state.isRecording || !this.state.isPaused) return;

        this.mediaRecorder?.resume();
        this.pausedDuration += Date.now() - this.pauseStartTime;
        this.state.isPaused = false;

        console.log('Audio recording resumed');
    }

    /**
     * Stop recording and return audio blob
     */
    async stopRecording(): Promise<Blob | null> {
        if (!this.state.isRecording) return null;

        return new Promise((resolve) => {
            if (this.mediaRecorder) {
                this.mediaRecorder.onstop = () => {
                    const blob = new Blob(this.recordedChunks, { type: 'audio/webm' });
                    this.cleanup();
                    resolve(blob);
                };
                this.mediaRecorder.stop();
            } else {
                this.cleanup();
                resolve(null);
            }
        });
    }

    /**
     * Save recorded audio to file
     */
    async saveRecording(meetingId: string): Promise<string | null> {
        const blob = await this.stopRecording();
        if (!blob) return null;

        try {
            const dataDir = await appDataDir();
            const recordingsDir = `${dataDir}recordings`;

            // Create recordings directory if needed
            await createDir(recordingsDir, { recursive: true });

            // Convert blob to array buffer
            const arrayBuffer = await blob.arrayBuffer();
            const uint8Array = new Uint8Array(arrayBuffer);

            // Save file
            const fileName = `${meetingId}_${Date.now()}.webm`;
            const filePath = `${recordingsDir}/${fileName}`;
            await writeBinaryFile(filePath, uint8Array);

            console.log(`Recording saved to: ${filePath}`);
            return filePath;
        } catch (error) {
            console.error('Failed to save recording:', error);
            return null;
        }
    }

    /**
     * Get current recording state
     */
    getState(): RecordingState {
        if (this.state.isRecording && !this.state.isPaused) {
            this.state.duration = Date.now() - this.startTime - this.pausedDuration;
        }
        return { ...this.state };
    }

    /**
     * Subscribe to audio chunks (for transcription)
     */
    onAudioChunk(callback: AudioCallback): () => void {
        this.audioCallbacks.push(callback);
        return () => {
            this.audioCallbacks = this.audioCallbacks.filter(cb => cb !== callback);
        };
    }

    /**
     * Subscribe to volume changes
     */
    onVolumeChange(callback: VolumeCallback): () => void {
        this.volumeCallbacks.push(callback);
        return () => {
            this.volumeCallbacks = this.volumeCallbacks.filter(cb => cb !== callback);
        };
    }

    private startVolumeMonitoring(): void {
        if (this.volumeInterval) return;

        this.volumeInterval = window.setInterval(() => {
            if (!this.analyserNode || this.state.isPaused) return;

            const dataArray = new Uint8Array(this.analyserNode.frequencyBinCount);
            this.analyserNode.getByteFrequencyData(dataArray);

            // Calculate average volume
            const sum = dataArray.reduce((a, b) => a + b, 0);
            const average = sum / dataArray.length;
            const normalizedVolume = Math.min(average / 128, 1);

            this.state.volume = normalizedVolume;
            this.volumeCallbacks.forEach(cb => cb(normalizedVolume));
        }, 100);
    }

    private cleanup(): void {
        // Stop volume monitoring
        if (this.volumeInterval) {
            clearInterval(this.volumeInterval);
            this.volumeInterval = null;
        }

        // Disconnect audio nodes
        this.processorNode?.disconnect();
        this.analyserNode?.disconnect();

        // Close audio context
        this.audioContext?.close();

        // Stop media stream
        this.mediaStream?.getTracks().forEach(track => track.stop());

        // Reset references
        this.mediaStream = null;
        this.audioContext = null;
        this.analyserNode = null;
        this.processorNode = null;
        this.mediaRecorder = null;
        this.recordedChunks = [];

        // Reset state
        this.state = {
            isRecording: false,
            isPaused: false,
            duration: 0,
            volume: 0,
        };

        console.log('Audio capture cleaned up');
    }
}

// Singleton instance
export const audioCapture = new AudioCaptureService();
