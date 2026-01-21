// Transcription Service
// Handles speech-to-text using OpenAI Whisper API

import { AudioChunk } from './audioCapture';

export interface TranscriptionResult {
    text: string;
    timestamp: number;
    confidence: number;
    language?: string;
    speakerId?: string;
}

export interface TranscriptionConfig {
    apiKey: string;
    language?: string; // ISO-639-1 code, e.g., 'en', 'es', 'fr'
    model?: 'whisper-1';
    prompt?: string; // Optional context for better accuracy
}

type TranscriptionCallback = (result: TranscriptionResult) => void;

class TranscriptionService {
    private config: TranscriptionConfig | null = null;
    private audioBuffer: Float32Array[] = [];
    private bufferDuration: number = 0;
    private readonly CHUNK_DURATION_MS = 5000; // Send audio every 5 seconds
    private readonly SAMPLE_RATE = 16000;
    private isProcessing: boolean = false;
    private callbacks: TranscriptionCallback[] = [];
    private processInterval: number | null = null;

    /**
     * Initialize the transcription service with API config
     */
    configure(config: TranscriptionConfig): void {
        this.config = config;
        console.log('Transcription service configured');
    }

    /**
     * Check if service is configured
     */
    isConfigured(): boolean {
        return this.config !== null && this.config.apiKey.length > 0;
    }

    /**
     * Start processing audio chunks for transcription
     */
    start(): void {
        if (this.processInterval) return;

        this.audioBuffer = [];
        this.bufferDuration = 0;

        // Process buffer periodically
        this.processInterval = window.setInterval(() => {
            this.processBuffer();
        }, this.CHUNK_DURATION_MS);

        console.log('Transcription service started');
    }

    /**
     * Stop processing
     */
    stop(): void {
        if (this.processInterval) {
            clearInterval(this.processInterval);
            this.processInterval = null;
        }

        // Process remaining audio
        if (this.audioBuffer.length > 0) {
            this.processBuffer();
        }

        console.log('Transcription service stopped');
    }

    /**
     * Add audio chunk to buffer for transcription
     */
    addAudioChunk(chunk: AudioChunk): void {
        this.audioBuffer.push(chunk.data);
        this.bufferDuration += (chunk.data.length / this.SAMPLE_RATE) * 1000;
    }

    /**
     * Subscribe to transcription results
     */
    onTranscription(callback: TranscriptionCallback): () => void {
        this.callbacks.push(callback);
        return () => {
            this.callbacks = this.callbacks.filter(cb => cb !== callback);
        };
    }

    /**
     * Process buffered audio and send for transcription
     */
    private async processBuffer(): Promise<void> {
        if (this.isProcessing || this.audioBuffer.length === 0 || !this.config) {
            return;
        }

        this.isProcessing = true;

        try {
            // Combine audio chunks
            const combinedAudio = this.combineAudioChunks(this.audioBuffer);
            const timestamp = Date.now();

            // Clear buffer
            this.audioBuffer = [];
            this.bufferDuration = 0;

            // Check if audio has enough content (not just silence)
            if (!this.hasAudioContent(combinedAudio)) {
                this.isProcessing = false;
                return;
            }

            // Convert to WAV and send to API
            const wavBlob = this.audioToWav(combinedAudio);
            const result = await this.sendToWhisper(wavBlob);

            if (result && result.text.trim()) {
                const transcriptionResult: TranscriptionResult = {
                    text: result.text.trim(),
                    timestamp,
                    confidence: 1.0, // Whisper doesn't return confidence
                    language: result.language,
                };

                // Notify callbacks
                this.callbacks.forEach(cb => cb(transcriptionResult));
            }
        } catch (error) {
            console.error('Transcription error:', error);
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Combine multiple audio chunks into one
     */
    private combineAudioChunks(chunks: Float32Array[]): Float32Array {
        const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
        const combined = new Float32Array(totalLength);
        let offset = 0;

        for (const chunk of chunks) {
            combined.set(chunk, offset);
            offset += chunk.length;
        }

        return combined;
    }

    /**
     * Check if audio contains actual content (not silence)
     */
    private hasAudioContent(audio: Float32Array): boolean {
        const threshold = 0.01;
        let sum = 0;

        for (let i = 0; i < audio.length; i++) {
            sum += Math.abs(audio[i]);
        }

        const average = sum / audio.length;
        return average > threshold;
    }

    /**
     * Convert Float32Array audio to WAV blob
     */
    private audioToWav(audio: Float32Array): Blob {
        const buffer = new ArrayBuffer(44 + audio.length * 2);
        const view = new DataView(buffer);

        // WAV header
        const writeString = (offset: number, string: string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };

        writeString(0, 'RIFF');
        view.setUint32(4, 36 + audio.length * 2, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true); // Subchunk1Size
        view.setUint16(20, 1, true); // AudioFormat (PCM)
        view.setUint16(22, 1, true); // NumChannels
        view.setUint32(24, this.SAMPLE_RATE, true);
        view.setUint32(28, this.SAMPLE_RATE * 2, true); // ByteRate
        view.setUint16(32, 2, true); // BlockAlign
        view.setUint16(34, 16, true); // BitsPerSample
        writeString(36, 'data');
        view.setUint32(40, audio.length * 2, true);

        // Convert Float32 to Int16
        let offset = 44;
        for (let i = 0; i < audio.length; i++) {
            const sample = Math.max(-1, Math.min(1, audio[i]));
            view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
            offset += 2;
        }

        return new Blob([buffer], { type: 'audio/wav' });
    }

    /**
     * Send audio to OpenAI Whisper API
     */
    private async sendToWhisper(audioBlob: Blob): Promise<{ text: string; language?: string } | null> {
        if (!this.config) return null;

        try {
            const formData = new FormData();
            formData.append('file', audioBlob, 'audio.wav');
            formData.append('model', this.config.model || 'whisper-1');

            if (this.config.language) {
                formData.append('language', this.config.language);
            }

            if (this.config.prompt) {
                formData.append('prompt', this.config.prompt);
            }

            const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.config.apiKey}`,
                },
                body: formData,
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error?.message || 'Transcription failed');
            }

            const data = await response.json();
            return {
                text: data.text,
                language: data.language,
            };
        } catch (error) {
            console.error('Whisper API error:', error);
            throw error;
        }
    }

    /**
     * Transcribe a complete audio file
     */
    async transcribeFile(audioBlob: Blob): Promise<string> {
        if (!this.config) {
            throw new Error('Transcription service not configured');
        }

        const result = await this.sendToWhisper(audioBlob);
        return result?.text || '';
    }
}

// Singleton instance
export const transcriptionService = new TranscriptionService();
