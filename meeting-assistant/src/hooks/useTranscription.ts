// Transcription Hook
// Integrates transcription service with audio recording and speaker diarization

import { useEffect, useCallback, useRef } from 'react';
import { 
    transcriptionService, 
    aiChatService, 
    speakerDiarizationService,
    noteGenerationService,
    audioCapture
} from '@/services';
import type { TranscriptionResult } from '@/services';
import { useTranscriptStore } from '@/store';
import type { TranscriptEntry } from '@/types';

interface UseTranscriptionReturn {
    isConfigured: boolean;
    isProcessing: boolean;
    startTranscription: () => void;
    stopTranscription: () => void;
    entries: TranscriptEntry[];
}

export function useTranscription(): UseTranscriptionReturn {
    const { addEntry, entries, setIsProcessing, isProcessing, clearEntries } = useTranscriptStore();
    const transcriptRef = useRef<string>('');
    const unsubscribeRef = useRef<(() => void) | null>(null);
    const audioChunkBuffer = useRef<Float32Array[]>([]);

    // Load settings and configure services on mount
    useEffect(() => {
        const savedSettings = localStorage.getItem('meeting-assistant-settings');
        if (savedSettings) {
            try {
                const settings = JSON.parse(savedSettings);

                // Configure transcription service (Rev.ai)
                if (settings.apiKeys?.openaiKey) {
                    transcriptionService.configure({
                        apiKey: settings.apiKeys.openaiKey,
                        language: settings.transcriptionLanguage || undefined,
                        skipDiarization: false, // Enable Rev.ai's built-in diarization
                        diarizationType: 'standard',
                    });
                }

                // Configure speaker diarization
                speakerDiarizationService.configure({
                    method: 'simple', // Use simple method for now
                    minSpeakers: 1,
                    maxSpeakers: 4,
                });

                // Configure note generation
                noteGenerationService.configure({
                    enabled: settings.autoGenerateNotes !== false,
                    interval: 30000, // Every 30 seconds
                    minTranscriptLength: 50,
                    noteTypes: ['key-point', 'action-item', 'decision', 'question'],
                });

                // Configure AI chat service
                let aiApiKey: string;
                if (settings.aiProvider === 'openai') {
                    aiApiKey = settings.apiKeys?.openaiKey;
                } else if (settings.aiProvider === 'groq') {
                    aiApiKey = settings.apiKeys?.groqKey;
                } else {
                    aiApiKey = settings.apiKeys?.anthropicKey;
                }

                if (aiApiKey) {
                    aiChatService.configure({
                        provider: {
                            type: settings.aiProvider || 'openai',
                            apiKey: aiApiKey,
                            model: settings.aiModel,
                        },
                    });
                }
            } catch (e) {
                console.error('Failed to load settings for transcription:', e);
            }
        }
    }, []);

    // Handle transcription results with speaker diarization
    const handleTranscriptionResult = useCallback(async (result: TranscriptionResult) => {
        // If Rev.ai provided speaker info, use it directly
        if (result.speakerId && result.speakerName) {
            const entry: TranscriptEntry = {
                id: crypto.randomUUID(),
                meetingId: '', // Will be set by the meeting context
                speakerId: result.speakerId,
                speakerName: result.speakerName,
                text: result.text,
                timestamp: result.timestamp,
                endTimestamp: result.timestamp + 1000,
                confidence: result.confidence || 1.0,
                language: result.language || 'en',
                createdAt: new Date(),
            };

            addEntry(entry);
            noteGenerationService.addTranscriptEntry(entry);

            // Update transcript context for AI
            transcriptRef.current += `\n[${new Date(result.timestamp).toLocaleTimeString()}] ${entry.speakerName}: ${result.text}`;
            aiChatService.updateTranscriptContext(transcriptRef.current);

            setIsProcessing(false);
            return;
        }

        // Fallback: Use simple speaker diarization for OpenAI Whisper
        const audioFeatures = audioChunkBuffer.current.length > 0
            ? speakerDiarizationService.analyzeAudioFeatures(
                  audioChunkBuffer.current[audioChunkBuffer.current.length - 1],
                  16000
              )
            : undefined;

        // Create temporary entry for speaker identification
        const tempEntry: TranscriptEntry = {
            id: crypto.randomUUID(),
            meetingId: '', // Will be set by the meeting context
            speakerId: 'speaker-1',
            speakerName: 'Speaker',
            text: result.text,
            timestamp: result.timestamp,
            endTimestamp: result.timestamp + 1000,
            confidence: result.confidence || 1.0,
            language: result.language || 'en',
            createdAt: new Date(),
        };

        // Identify speaker
        const speakerInfo = await speakerDiarizationService.identifySpeaker(tempEntry, audioFeatures);

        // Create final entry with speaker info
        const entry: TranscriptEntry = {
            ...tempEntry,
            speakerId: speakerInfo.speakerId,
            speakerName: speakerInfo.speakerName,
            confidence: speakerInfo.confidence,
        };

        addEntry(entry);

        // Add to note generation service
        noteGenerationService.addTranscriptEntry(entry);

        // Update transcript context for AI
        transcriptRef.current += `\n[${new Date(result.timestamp).toLocaleTimeString()}] ${entry.speakerName}: ${result.text}`;
        aiChatService.updateTranscriptContext(transcriptRef.current);

        setIsProcessing(false);
    }, [addEntry, setIsProcessing]);

    // Start transcription
    const startTranscription = useCallback(() => {
        if (!transcriptionService.isConfigured()) {
            console.warn('Transcription service not configured. Please add your Rev.ai API key in Settings.');
            return;
        }

        // Clear previous entries
        clearEntries();
        transcriptRef.current = '';
        audioChunkBuffer.current = [];
        aiChatService.clearHistory();

        // Reset services
        speakerDiarizationService.reset();
        noteGenerationService.reset();

        // Subscribe to transcription results
        unsubscribeRef.current = transcriptionService.onTranscription(handleTranscriptionResult);

        // Subscribe to audio chunks for speaker analysis
        const audioUnsubscribe = audioCapture.onAudioChunk((chunk) => {
            audioChunkBuffer.current.push(chunk.data);
            // Keep only last 10 chunks for analysis
            if (audioChunkBuffer.current.length > 10) {
                audioChunkBuffer.current.shift();
            }
        });

        // Start the transcription service
        transcriptionService.start();
        
        // Start note generation service
        noteGenerationService.start();
        
        setIsProcessing(true);

        // Store audio unsubscribe for cleanup
        return () => {
            audioUnsubscribe();
        };
    }, [handleTranscriptionResult, setIsProcessing, clearEntries]);

    // Stop transcription
    const stopTranscription = useCallback(() => {
        transcriptionService.stop();

        if (unsubscribeRef.current) {
            unsubscribeRef.current();
            unsubscribeRef.current = null;
        }

        setIsProcessing(false);
    }, [setIsProcessing]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (unsubscribeRef.current) {
                unsubscribeRef.current();
            }
        };
    }, []);

    return {
        isConfigured: transcriptionService.isConfigured(),
        isProcessing,
        startTranscription,
        stopTranscription,
        entries,
    };
}
