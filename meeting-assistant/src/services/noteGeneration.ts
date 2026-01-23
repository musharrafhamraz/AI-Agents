// Live Note Generation Service
// Automatically generates notes from meeting transcript using AI

import type { Note, NoteType, TranscriptEntry } from '@/types';
import { aiChatService } from './aiChat';
import { integrationService } from './integrations';

export interface NoteGenerationConfig {
    enabled: boolean;
    interval: number; // milliseconds between note generation checks
    minTranscriptLength: number; // minimum words before generating notes
    noteTypes: NoteType[];
}

interface PendingNote {
    type: NoteType;
    content: string;
    confidence: number;
    sourceRefs: string[];
    timestamp: number;
}

type NoteCallback = (note: Note) => void;

class NoteGenerationService {
    private config: NoteGenerationConfig = {
        enabled: true,
        interval: 30000, // Check every 30 seconds
        minTranscriptLength: 50, // At least 50 words
        noteTypes: ['key-point', 'action-item', 'decision', 'question'],
    };

    private intervalId: number | null = null;
    private transcriptBuffer: TranscriptEntry[] = [];
    private lastProcessedIndex = 0;
    private callbacks: NoteCallback[] = [];
    private isProcessing = false;

    /**
     * Configure the note generation service
     */
    configure(config: Partial<NoteGenerationConfig>): void {
        this.config = { ...this.config, ...config };
        console.log('Note generation service configured:', this.config);
    }

    /**
     * Start automatic note generation
     */
    start(): void {
        if (this.intervalId || !this.config.enabled) return;

        this.transcriptBuffer = [];
        this.lastProcessedIndex = 0;

        this.intervalId = window.setInterval(() => {
            this.processTranscript();
        }, this.config.interval);

        console.log('Note generation service started');
    }

    /**
     * Stop automatic note generation
     */
    stop(): void {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }

        // Process any remaining transcript
        if (this.transcriptBuffer.length > this.lastProcessedIndex) {
            this.processTranscript();
        }

        console.log('Note generation service stopped');
    }

    /**
     * Add transcript entry to buffer
     */
    addTranscriptEntry(entry: TranscriptEntry): void {
        this.transcriptBuffer.push(entry);
    }

    /**
     * Subscribe to generated notes
     */
    onNoteGenerated(callback: NoteCallback): () => void {
        this.callbacks.push(callback);
        return () => {
            this.callbacks = this.callbacks.filter(cb => cb !== callback);
        };
    }

    /**
     * Process transcript and generate notes
     */
    private async processTranscript(): Promise<void> {
        if (this.isProcessing || !aiChatService.isConfigured()) return;

        const newEntries = this.transcriptBuffer.slice(this.lastProcessedIndex);
        if (newEntries.length === 0) return;

        // Check if we have enough content
        const wordCount = newEntries.reduce((count, entry) => {
            return count + entry.text.split(/\s+/).length;
        }, 0);

        if (wordCount < this.config.minTranscriptLength) return;

        this.isProcessing = true;

        try {
            // Build context from new entries
            const context = newEntries
                .map(e => `[${this.formatTime(e.timestamp)}] ${e.speakerName}: ${e.text}`)
                .join('\n');

            // Generate notes for each type
            const notes = await this.generateNotesFromContext(context, newEntries);

            // Emit generated notes
            notes.forEach(note => {
                this.callbacks.forEach(cb => cb(note));
                
                // Auto-sync to integrations if enabled
                if (integrationService.isEnabled()) {
                    this.syncNoteToIntegrations(note).catch(err => {
                        console.error('Failed to sync note to integrations:', err);
                    });
                }
            });

            // Update last processed index
            this.lastProcessedIndex = this.transcriptBuffer.length;

            console.log(`Generated ${notes.length} notes from ${newEntries.length} transcript entries`);
        } catch (error) {
            console.error('Failed to generate notes:', error);
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Generate notes from transcript context using AI
     */
    private async generateNotesFromContext(
        context: string,
        entries: TranscriptEntry[]
    ): Promise<Note[]> {
        const notes: Note[] = [];
        const meetingId = entries[0]?.meetingId || '';
        const timestamp = entries[entries.length - 1]?.timestamp || Date.now();

        // Generate different types of notes
        for (const noteType of this.config.noteTypes) {
            try {
                const pendingNotes = await this.generateNoteType(noteType, context);
                
                for (const pending of pendingNotes) {
                    const note: Note = {
                        id: crypto.randomUUID(),
                        meetingId,
                        type: pending.type,
                        content: pending.content,
                        timestamp: pending.timestamp || timestamp,
                        sourceRefs: pending.sourceRefs,
                        completed: false,
                        createdAt: new Date(),
                        updatedAt: new Date(),
                    };

                    notes.push(note);
                }
            } catch (error) {
                console.error(`Failed to generate ${noteType} notes:`, error);
            }
        }

        return notes;
    }

    /**
     * Generate specific type of notes
     */
    private async generateNoteType(
        noteType: NoteType,
        context: string
    ): Promise<PendingNote[]> {
        const prompt = this.buildPromptForNoteType(noteType, context);

        try {
            const response = await aiChatService.sendMessage(prompt);
            return this.parseNoteResponse(response.content, noteType);
        } catch (error) {
            console.error(`Error generating ${noteType}:`, error);
            return [];
        }
    }

    /**
     * Build AI prompt for specific note type
     */
    private buildPromptForNoteType(noteType: NoteType, context: string): string {
        const prompts: Record<NoteType, string> = {
            'key-point': `Analyze this meeting transcript and extract key points discussed. Return ONLY a JSON array of strings, each being a concise key point (max 100 characters each). If no key points found, return empty array [].

Transcript:
${context}

Return format: ["key point 1", "key point 2", ...]`,

            'action-item': `Analyze this meeting transcript and extract action items. Return ONLY a JSON array of objects with format: [{"content": "action description", "assignee": "person name or null"}]. If no action items found, return empty array [].

Transcript:
${context}

Return format: [{"content": "...", "assignee": "..."}]`,

            'decision': `Analyze this meeting transcript and extract decisions made. Return ONLY a JSON array of strings, each being a clear decision (max 150 characters each). If no decisions found, return empty array [].

Transcript:
${context}

Return format: ["decision 1", "decision 2", ...]`,

            'question': `Analyze this meeting transcript and extract unresolved questions. Return ONLY a JSON array of strings, each being a question that needs follow-up. If no questions found, return empty array [].

Transcript:
${context}

Return format: ["question 1?", "question 2?", ...]`,

            'follow-up': `Analyze this meeting transcript and extract items that need follow-up. Return ONLY a JSON array of strings. If none found, return empty array [].

Transcript:
${context}

Return format: ["follow-up 1", "follow-up 2", ...]`,

            'manual': '', // Manual notes are not auto-generated
        };

        return prompts[noteType] || '';
    }

    /**
     * Parse AI response into pending notes
     */
    private parseNoteResponse(response: string, noteType: NoteType): PendingNote[] {
        try {
            // Extract JSON from response (handle markdown code blocks)
            let jsonStr = response.trim();
            
            // Remove markdown code blocks if present
            if (jsonStr.startsWith('```')) {
                jsonStr = jsonStr.replace(/```json?\n?/g, '').replace(/```\n?/g, '').trim();
            }

            const parsed = JSON.parse(jsonStr);

            if (!Array.isArray(parsed)) {
                console.warn('AI response is not an array:', parsed);
                return [];
            }

            // Handle different response formats
            if (noteType === 'action-item' && parsed.length > 0 && typeof parsed[0] === 'object') {
                // Action items with assignees
                return parsed.map((item: any) => ({
                    type: noteType,
                    content: item.content || '',
                    confidence: 0.8,
                    sourceRefs: [],
                    timestamp: Date.now(),
                    assignee: item.assignee || undefined,
                }));
            }

            // Simple string array
            return parsed
                .filter((item: any) => typeof item === 'string' && item.trim().length > 0)
                .map((content: string) => ({
                    type: noteType,
                    content: content.trim(),
                    confidence: 0.8,
                    sourceRefs: [],
                    timestamp: Date.now(),
                }));
        } catch (error) {
            console.error('Failed to parse note response:', error, response);
            return [];
        }
    }

    /**
     * Format timestamp as MM:SS
     */
    private formatTime(ms: number): string {
        const totalSeconds = Math.floor(ms / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    /**
     * Manually generate notes from current transcript
     */
    async generateNotesNow(): Promise<Note[]> {
        if (this.transcriptBuffer.length === 0) {
            return [];
        }

        const context = this.transcriptBuffer
            .map(e => `[${this.formatTime(e.timestamp)}] ${e.speakerName}: ${e.text}`)
            .join('\n');

        return this.generateNotesFromContext(context, this.transcriptBuffer);
    }

    /**
     * Clear transcript buffer
     */
    reset(): void {
        this.transcriptBuffer = [];
        this.lastProcessedIndex = 0;
        console.log('Note generation service reset');
    }

    /**
     * Sync note to external integrations
     */
    private async syncNoteToIntegrations(note: Note): Promise<void> {
        try {
            // Get meeting title from somewhere (you might need to pass this)
            const meetingTitle = 'Current Meeting'; // TODO: Get actual meeting title
            
            const results = await integrationService.syncNote(note, meetingTitle);
            
            results.forEach(result => {
                if (result.success) {
                    console.log(`✅ Synced to ${result.platform}: ${note.content.substring(0, 50)}...`);
                } else {
                    console.warn(`❌ Failed to sync to ${result.platform}: ${result.error}`);
                }
            });
        } catch (error) {
            console.error('Integration sync error:', error);
        }
    }
}

// Singleton instance
export const noteGenerationService = new NoteGenerationService();
