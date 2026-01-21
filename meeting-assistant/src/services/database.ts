// Database Service
// TypeScript wrapper for Tauri database commands

import { invoke } from '@tauri-apps/api/tauri';
import { save } from '@tauri-apps/api/dialog';
import { writeTextFile } from '@tauri-apps/api/fs';

// Types matching Rust models
export interface Meeting {
    id: string;
    title: string;
    start_time: string;
    end_time: string | null;
    participants: Participant[];
    language: string;
    translation_target: string | null;
    status: 'idle' | 'recording' | 'paused' | 'completed';
    audio_path: string | null;
    created_at: string;
    updated_at: string;
}

export interface Participant {
    id: string;
    name: string;
    color: string;
    is_local: boolean;
}

export interface TranscriptEntry {
    id: string;
    meeting_id: string;
    speaker_id: string;
    speaker_name: string;
    text: string;
    timestamp: number;
    end_timestamp: number;
    confidence: number;
    language: string;
    translation: string | null;
    created_at: string;
}

export interface Note {
    id: string;
    meeting_id: string;
    note_type: 'key-point' | 'action-item' | 'decision' | 'question' | 'follow-up' | 'manual';
    content: string;
    timestamp: number;
    source_refs: string[];
    assignee: string | null;
    deadline: string | null;
    completed: boolean;
    created_at: string;
    updated_at: string;
}

export interface ExportResult {
    file_path: string;
    content: string;
}

class DatabaseService {
    // ========================================
    // Meeting Operations
    // ========================================

    async startMeeting(title: string): Promise<Meeting> {
        return invoke<Meeting>('start_meeting', { title });
    }

    async endMeeting(meetingId: string): Promise<Meeting> {
        return invoke<Meeting>('end_meeting', { meetingId });
    }

    async pauseMeeting(meetingId: string): Promise<void> {
        return invoke<void>('pause_meeting', { meetingId });
    }

    async resumeMeeting(meetingId: string): Promise<void> {
        return invoke<void>('resume_meeting', { meetingId });
    }

    async getMeetings(): Promise<Meeting[]> {
        return invoke<Meeting[]>('get_meetings');
    }

    async getMeeting(meetingId: string): Promise<Meeting> {
        return invoke<Meeting>('get_meeting', { meetingId });
    }

    async deleteMeeting(meetingId: string): Promise<void> {
        return invoke<void>('delete_meeting', { meetingId });
    }

    // ========================================
    // Transcript Operations
    // ========================================

    async getTranscript(meetingId: string): Promise<TranscriptEntry[]> {
        return invoke<TranscriptEntry[]>('get_transcript', { meetingId });
    }

    async saveTranscriptEntry(entry: TranscriptEntry): Promise<void> {
        return invoke<void>('save_transcript_entry', { entry });
    }

    async saveTranscriptBatch(entries: TranscriptEntry[]): Promise<void> {
        return invoke<void>('save_transcript_batch', { entries });
    }

    // ========================================
    // Notes Operations
    // ========================================

    async getNotes(meetingId: string): Promise<Note[]> {
        return invoke<Note[]>('get_notes', { meetingId });
    }

    async addNote(meetingId: string, noteType: string, content: string, timestamp: number): Promise<Note> {
        return invoke<Note>('add_note', { meetingId, noteType, content, timestamp });
    }

    async updateNote(noteId: string, content?: string, completed?: boolean): Promise<Note> {
        return invoke<Note>('update_note', { noteId, content, completed });
    }

    async deleteNote(noteId: string): Promise<void> {
        return invoke<void>('delete_note', { noteId });
    }

    // ========================================
    // Export Operations
    // ========================================

    async exportMeetingMarkdown(
        meetingId: string,
        options: {
            includeTranscript?: boolean;
            includeNotes?: boolean;
            includeSummary?: string;
        } = {}
    ): Promise<ExportResult> {
        return invoke<ExportResult>('export_meeting_markdown', {
            meetingId,
            includeTranscript: options.includeTranscript ?? true,
            includeNotes: options.includeNotes ?? true,
            includeSummary: options.includeSummary,
        });
    }

    /**
     * Export meeting to markdown file and prompt user to save
     */
    async exportAndSave(
        meetingId: string,
        options: {
            includeTranscript?: boolean;
            includeNotes?: boolean;
            includeSummary?: string;
        } = {}
    ): Promise<string | null> {
        try {
            // Generate markdown content
            const result = await this.exportMeetingMarkdown(meetingId, options);

            // Prompt user to save file
            const filePath = await save({
                defaultPath: result.file_path,
                filters: [{ name: 'Markdown', extensions: ['md'] }],
            });

            if (filePath) {
                // Write file
                await writeTextFile(filePath, result.content);
                return filePath;
            }

            return null;
        } catch (error) {
            console.error('Export failed:', error);
            throw error;
        }
    }

    /**
     * Generate markdown content without saving (for preview/clipboard)
     */
    async generateMarkdownContent(
        meetingId: string,
        options: {
            includeTranscript?: boolean;
            includeNotes?: boolean;
            includeSummary?: string;
        } = {}
    ): Promise<string> {
        const result = await this.exportMeetingMarkdown(meetingId, options);
        return result.content;
    }
}

// Singleton instance
export const databaseService = new DatabaseService();
