// Transcription Service
// Handles speech-to-text using Rev.ai API with built-in speaker diarization

import { AudioChunk } from './audioCapture';

// Dynamically import Tauri API (only available in Tauri context)
let tauriInvoke: ((cmd: string, args?: any) => Promise<any>) | null = null;

// Check if running in Tauri
const isTauri = typeof window !== 'undefined' && '__TAURI__' in window;

if (isTauri) {
    import('@tauri-apps/api/tauri').then(module => {
        tauriInvoke = module.invoke;
        console.log('Tauri API loaded successfully');
    }).catch(err => {
        console.warn('Failed to load Tauri API:', err);
    });
}

export interface TranscriptionResult {
    text: string;
    timestamp: number;
    confidence: number;
    language?: string;
    speakerId?: string;
    speakerName?: string;
}

export interface TranscriptionConfig {
    apiKey: string;
    provider?: 'revai' | 'openai'; // Default: auto-detect based on key format
    language?: string; // ISO-639-1 code, e.g., 'en', 'es', 'fr'
    skipDiarization?: boolean; // Default: false (diarization enabled)
    speakersCount?: number; // Hint for number of speakers
    diarizationType?: 'standard' | 'premium'; // Default: standard
}

type TranscriptionCallback = (result: TranscriptionResult) => void;

interface RevAiJob {
    id: string;
    status: 'in_progress' | 'transcribed' | 'failed';
    created_on: string;
    completed_on?: string;
}

interface RevAiTranscript {
    monologues: Array<{
        speaker: number;
        elements: Array<{
            type: 'text' | 'punct';
            value: string;
            ts?: number;
            end_ts?: number;
            confidence?: number;
        }>;
    }>;
}

class TranscriptionService {
    private config: TranscriptionConfig | null = null;
    private audioBuffer: Float32Array[] = [];
    private bufferDuration: number = 0;
    private readonly CHUNK_DURATION_MS = 30000; // Send audio every 30 seconds for Rev.ai (increased from 10s)
    private readonly SAMPLE_RATE = 16000;
    private isProcessing: boolean = false;
    private callbacks: TranscriptionCallback[] = [];
    private processInterval: number | null = null;
    private readonly API_BASE = 'https://api.rev.ai/speechtotext/v1';

    /**
     * Initialize the transcription service with API config
     */
    configure(config: TranscriptionConfig): void {
        // Auto-detect provider based on API key format
        let provider = config.provider;
        if (!provider) {
            if (config.apiKey.startsWith('sk-')) {
                provider = 'openai';
            } else if (config.apiKey.startsWith('02')) {
                provider = 'revai';
            } else {
                // Default to Rev.ai
                provider = 'revai';
            }
        }

        this.config = {
            ...config,
            provider,
            skipDiarization: config.skipDiarization ?? false,
            diarizationType: config.diarizationType ?? 'standard',
        };
        console.log(`Transcription service configured with ${provider === 'openai' ? 'OpenAI Whisper' : 'Rev.ai'}`);
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

        console.log('Transcription service started with Rev.ai');
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

            // Check minimum duration (Rev.ai requires at least 0.5 seconds)
            const durationSeconds = combinedAudio.length / this.SAMPLE_RATE;
            if (durationSeconds < 0.5) {
                console.warn(`Audio too short (${durationSeconds.toFixed(2)}s), skipping transcription`);
                this.isProcessing = false;
                return;
            }

            console.log(`Processing ${durationSeconds.toFixed(2)}s of audio...`);

            // Convert to WAV
            const wavBlob = this.audioToWav(combinedAudio);

            // Use appropriate provider
            if (this.config.provider === 'openai') {
                await this.processWithOpenAI(wavBlob, timestamp);
            } else {
                await this.processWithRevAi(wavBlob, timestamp);
            }
        } catch (error) {
            console.error('Transcription error:', error);
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Process with OpenAI Whisper
     */
    private async processWithOpenAI(audioBlob: Blob, timestamp: number): Promise<void> {
        if (!this.config) return;

        try {
            console.log('Sending audio to OpenAI Whisper...');
            
            const formData = new FormData();
            formData.append('file', audioBlob, 'audio.wav');
            formData.append('model', 'whisper-1');
            
            if (this.config.language) {
                formData.append('language', this.config.language);
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
                throw new Error(error.error?.message || 'OpenAI Whisper transcription failed');
            }

            const data = await response.json();
            const text = data.text?.trim();

            if (text) {
                console.log(`Transcribed: ${text}`);
                
                const result: TranscriptionResult = {
                    text,
                    timestamp,
                    confidence: 1.0,
                    language: this.config.language || 'en',
                };

                // Notify callbacks
                this.callbacks.forEach(cb => cb(result));
            } else {
                console.warn('OpenAI Whisper returned no text');
            }
        } catch (error) {
            console.error('OpenAI Whisper error:', error);
            throw error;
        }
    }

    /**
     * Process with Rev.ai
     */
    private async processWithRevAi(audioBlob: Blob, timestamp: number): Promise<void> {
        if (!this.config) return;

        try {
            console.log('Sending audio to Rev.ai...');
            const transcript = await this.sendToRevAi(audioBlob);

            if (transcript && transcript.monologues) {
                console.log(`Rev.ai returned ${transcript.monologues.length} speaker segments`);
                
                // Process each monologue (speaker segment)
                for (const monologue of transcript.monologues) {
                    const speakerId = `speaker-${monologue.speaker}`;
                    const speakerName = `Speaker ${monologue.speaker}`;
                    
                    // Combine text elements
                    let text = '';
                    let confidence = 0;
                    let count = 0;

                    for (const element of monologue.elements) {
                        if (element.type === 'text') {
                            text += element.value + ' ';
                            if (element.confidence) {
                                confidence += element.confidence;
                                count++;
                            }
                        } else if (element.type === 'punct') {
                            text = text.trim() + element.value + ' ';
                        }
                    }

                    text = text.trim();
                    const avgConfidence = count > 0 ? confidence / count : 1.0;

                    if (text) {
                        console.log(`Transcribed: [${speakerName}] ${text}`);
                        
                        const result: TranscriptionResult = {
                            text,
                            timestamp,
                            confidence: avgConfidence,
                            language: this.config.language || 'en',
                            speakerId,
                            speakerName,
                        };

                        // Notify callbacks
                        this.callbacks.forEach(cb => cb(result));
                    }
                }
            } else {
                console.warn('Rev.ai returned no transcript data');
            }
        } catch (error) {
            console.error('Rev.ai error:', error);
            throw error;
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
     * Send audio to Rev.ai API
     */
    private async sendToRevAi(audioBlob: Blob): Promise<RevAiTranscript | null> {
        if (!this.config) return null;

        try {
            // Use Tauri if available, otherwise use fetch (with CORS limitations)
            if (tauriInvoke) {
                return await this.sendToRevAiViaTauri(audioBlob);
            } else {
                return await this.sendToRevAiViaFetch(audioBlob);
            }
        } catch (error) {
            console.error('Rev.ai API error:', error);
            throw error;
        }
    }

    /**
     * Send to Rev.ai via Tauri (bypasses CORS)
     */
    private async sendToRevAiViaTauri(audioBlob: Blob): Promise<RevAiTranscript | null> {
        if (!this.config || !tauriInvoke) return null;

        // Convert blob to base64 for Tauri
        const arrayBuffer = await audioBlob.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);
        
        // Build multipart form data manually
        const boundary = '----WebKitFormBoundary' + Math.random().toString(36).substring(2);
        const parts: Uint8Array[] = [];
        
        // Add media file
        const encoder = new TextEncoder();
        parts.push(encoder.encode(`--${boundary}\r\n`));
        parts.push(encoder.encode(`Content-Disposition: form-data; name="media"; filename="audio.wav"\r\n`));
        parts.push(encoder.encode(`Content-Type: audio/wav\r\n\r\n`));
        parts.push(uint8Array);
        parts.push(encoder.encode(`\r\n`));
        
        // Add skip_diarization
        parts.push(encoder.encode(`--${boundary}\r\n`));
        parts.push(encoder.encode(`Content-Disposition: form-data; name="skip_diarization"\r\n\r\n`));
        parts.push(encoder.encode(String(this.config.skipDiarization)));
        parts.push(encoder.encode(`\r\n`));
        
        // Add language if specified
        if (this.config.language) {
            parts.push(encoder.encode(`--${boundary}\r\n`));
            parts.push(encoder.encode(`Content-Disposition: form-data; name="language"\r\n\r\n`));
            parts.push(encoder.encode(this.config.language));
            parts.push(encoder.encode(`\r\n`));
        }
        
        // Add speakers_count if specified
        if (this.config.speakersCount) {
            parts.push(encoder.encode(`--${boundary}\r\n`));
            parts.push(encoder.encode(`Content-Disposition: form-data; name="speakers_count"\r\n\r\n`));
            parts.push(encoder.encode(String(this.config.speakersCount)));
            parts.push(encoder.encode(`\r\n`));
        }
        
        // Add diarization_type if specified
        if (this.config.diarizationType) {
            parts.push(encoder.encode(`--${boundary}\r\n`));
            parts.push(encoder.encode(`Content-Disposition: form-data; name="diarization_type"\r\n\r\n`));
            parts.push(encoder.encode(this.config.diarizationType));
            parts.push(encoder.encode(`\r\n`));
        }
        
        // End boundary
        parts.push(encoder.encode(`--${boundary}--\r\n`));
        
        // Combine all parts
        const totalLength = parts.reduce((sum, part) => sum + part.length, 0);
        const body = new Uint8Array(totalLength);
        let offset = 0;
        for (const part of parts) {
            body.set(part, offset);
            offset += part.length;
        }

        // Submit job via Tauri command
        const headers = {
            'Authorization': `Bearer ${this.config.apiKey}`,
        };

        const jobResponse = await tauriInvoke('http_post', {
            url: `${this.API_BASE}/jobs`,
            headers,
            body: Array.from(body),
            contentType: `multipart/form-data; boundary=${boundary}`,
        });

        const job = jobResponse as RevAiJob;
        console.log('Rev.ai job submitted successfully:', {
            id: job.id,
            status: job.status,
            created_on: job.created_on,
        });

        // Poll for completion
        const transcript = await this.pollForTranscript(job.id);
        return transcript;
    }

    /**
     * Send to Rev.ai via fetch (may have CORS issues in browser)
     */
    private async sendToRevAiViaFetch(audioBlob: Blob): Promise<RevAiTranscript | null> {
        if (!this.config) return null;

        console.warn('Using fetch for Rev.ai (may have CORS issues). Use Tauri mode for best results.');

        // Step 1: Submit job
        const formData = new FormData();
        formData.append('media', audioBlob, 'audio.wav');
        formData.append('skip_diarization', String(this.config.skipDiarization));
        
        if (this.config.language) {
            formData.append('language', this.config.language);
        }
        
        if (this.config.speakersCount) {
            formData.append('speakers_count', String(this.config.speakersCount));
        }
        
        if (this.config.diarizationType) {
            formData.append('diarization_type', this.config.diarizationType);
        }

        const submitResponse = await fetch(`${this.API_BASE}/jobs`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.config.apiKey}`,
            },
            body: formData,
        });

        if (!submitResponse.ok) {
            const error = await submitResponse.json();
            throw new Error(error.title || 'Rev.ai job submission failed');
        }

        const job: RevAiJob = await submitResponse.json();
        console.log('Rev.ai job submitted:', job.id);

        // Step 2: Poll for completion
        const transcript = await this.pollForTranscript(job.id);
        return transcript;
    }

    /**
     * Poll Rev.ai job until complete
     */
    private async pollForTranscript(jobId: string, maxAttempts: number = 30): Promise<RevAiTranscript | null> {
        if (!this.config) return null;

        const headers = {
            'Authorization': `Bearer ${this.config.apiKey}`,
        };

        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            try {
                // Check job status
                let job: RevAiJob;
                
                if (tauriInvoke) {
                    job = await tauriInvoke('http_get', {
                        url: `${this.API_BASE}/jobs/${jobId}`,
                        headers,
                    }) as RevAiJob;
                } else {
                    const response = await fetch(`${this.API_BASE}/jobs/${jobId}`, { headers });
                    if (!response.ok) throw new Error('Failed to check job status');
                    job = await response.json();
                }

                if (job.status === 'transcribed') {
                    // Get transcript
                    const transcriptHeaders = {
                        ...headers,
                        'Accept': 'application/vnd.rev.transcript.v1.0+json',
                    };

                    let transcript: RevAiTranscript;
                    
                    if (tauriInvoke) {
                        transcript = await tauriInvoke('http_get', {
                            url: `${this.API_BASE}/jobs/${jobId}/transcript`,
                            headers: transcriptHeaders,
                        }) as RevAiTranscript;
                    } else {
                        const response = await fetch(`${this.API_BASE}/jobs/${jobId}/transcript`, { 
                            headers: transcriptHeaders 
                        });
                        if (!response.ok) throw new Error('Failed to get transcript');
                        transcript = await response.json();
                    }

                    console.log('Rev.ai transcript received');
                    return transcript;
                } else if (job.status === 'failed') {
                    console.error('Rev.ai job failed. Job details:', job);
                    throw new Error(`Rev.ai job failed: ${JSON.stringify(job)}`);
                }

                // Wait before next poll (2 seconds)
                await new Promise(resolve => setTimeout(resolve, 2000));
            } catch (error) {
                console.error('Polling error:', error);
                if (attempt === maxAttempts - 1) {
                    throw error;
                }
            }
        }

        throw new Error('Rev.ai job timeout');
    }

    /**
     * Transcribe a complete audio file
     */
    async transcribeFile(audioBlob: Blob): Promise<string> {
        if (!this.config) {
            throw new Error('Transcription service not configured');
        }

        const transcript = await this.sendToRevAi(audioBlob);
        
        if (!transcript || !transcript.monologues) {
            return '';
        }

        // Combine all text
        let fullText = '';
        for (const monologue of transcript.monologues) {
            for (const element of monologue.elements) {
                if (element.type === 'text') {
                    fullText += element.value + ' ';
                } else if (element.type === 'punct') {
                    fullText = fullText.trim() + element.value + ' ';
                }
            }
        }

        return fullText.trim();
    }
}

// Singleton instance
export const transcriptionService = new TranscriptionService();
