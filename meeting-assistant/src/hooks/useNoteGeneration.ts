// Note Generation Hook
// Integrates automatic note generation with the UI

import { useEffect, useCallback, useState } from 'react';
import { noteGenerationService } from '@/services';
import { useNotesStore } from '@/store';
import type { Note } from '@/types';

export interface UseNoteGenerationReturn {
    generateNotesNow: () => Promise<void>;
    isGenerating: boolean;
}

export function useNoteGeneration(): UseNoteGenerationReturn {
    const { addNote } = useNotesStore();
    const [isGenerating, setIsGenerating] = useState(false);

    // Subscribe to auto-generated notes
    useEffect(() => {
        const unsubscribe = noteGenerationService.onNoteGenerated((note: Note) => {
            console.log('Auto-generated note:', note.type, note.content);
            addNote(note);
        });

        return unsubscribe;
    }, [addNote]);

    // Manually trigger note generation
    const generateNotesNow = useCallback(async () => {
        setIsGenerating(true);
        try {
            const notes = await noteGenerationService.generateNotesNow();
            notes.forEach(note => addNote(note));
            console.log(`Manually generated ${notes.length} notes`);
        } catch (error) {
            console.error('Failed to generate notes:', error);
        } finally {
            setIsGenerating(false);
        }
    }, [addNote]);

    return {
        generateNotesNow,
        isGenerating,
    };
}
