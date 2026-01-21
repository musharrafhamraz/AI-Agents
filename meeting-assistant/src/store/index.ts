import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
    Meeting,
    TranscriptEntry,
    Note,
    AIMessage,
    MeetingStatus,
    AudioState,
    UIState,
    PanelState
} from '@/types';

// =============================================
// Meeting Store
// =============================================

interface MeetingState {
    currentMeeting: Meeting | null;
    meetings: Meeting[];

    // Actions
    startMeeting: (title: string) => void;
    pauseMeeting: () => void;
    resumeMeeting: () => void;
    endMeeting: () => void;
    updateMeetingTitle: (title: string) => void;
    setMeetings: (meetings: Meeting[]) => void;
    loadMeeting: (id: string) => void;
}

export const useMeetingStore = create<MeetingState>((set, get) => ({
    currentMeeting: null,
    meetings: [],

    startMeeting: (title: string) => {
        const meeting: Meeting = {
            id: crypto.randomUUID(),
            title: title || `Meeting ${new Date().toLocaleDateString()}`,
            startTime: new Date(),
            participants: [],
            language: 'en',
            status: 'recording',
            createdAt: new Date(),
            updatedAt: new Date(),
        };
        set({ currentMeeting: meeting });
    },

    pauseMeeting: () => {
        set(state => ({
            currentMeeting: state.currentMeeting
                ? { ...state.currentMeeting, status: 'paused' as MeetingStatus }
                : null
        }));
    },

    resumeMeeting: () => {
        set(state => ({
            currentMeeting: state.currentMeeting
                ? { ...state.currentMeeting, status: 'recording' as MeetingStatus }
                : null
        }));
    },

    endMeeting: () => {
        const { currentMeeting, meetings } = get();
        if (currentMeeting) {
            const completedMeeting: Meeting = {
                ...currentMeeting,
                endTime: new Date(),
                status: 'completed',
                updatedAt: new Date(),
            };
            set({
                currentMeeting: null,
                meetings: [completedMeeting, ...meetings]
            });
        }
    },

    updateMeetingTitle: (title: string) => {
        set(state => ({
            currentMeeting: state.currentMeeting
                ? { ...state.currentMeeting, title }
                : null
        }));
    },

    setMeetings: (meetings: Meeting[]) => set({ meetings }),

    loadMeeting: (id: string) => {
        const { meetings } = get();
        const meeting = meetings.find(m => m.id === id);
        if (meeting) {
            set({ currentMeeting: meeting });
        }
    },
}));


// =============================================
// Transcript Store
// =============================================

interface TranscriptState {
    entries: TranscriptEntry[];
    isProcessing: boolean;

    // Actions
    addEntry: (entry: TranscriptEntry) => void;
    updateEntry: (id: string, updates: Partial<TranscriptEntry>) => void;
    clearEntries: () => void;
    setEntries: (entries: TranscriptEntry[]) => void;
    setIsProcessing: (processing: boolean) => void;
}

export const useTranscriptStore = create<TranscriptState>((set) => ({
    entries: [],
    isProcessing: false,

    addEntry: (entry) => {
        set(state => ({
            entries: [...state.entries, entry]
        }));
    },

    updateEntry: (id, updates) => {
        set(state => ({
            entries: state.entries.map(e =>
                e.id === id ? { ...e, ...updates } : e
            )
        }));
    },

    clearEntries: () => set({ entries: [] }),

    setEntries: (entries) => set({ entries }),

    setIsProcessing: (processing) => set({ isProcessing: processing }),
}));


// =============================================
// Notes Store
// =============================================

interface NotesState {
    notes: Note[];

    // Actions
    addNote: (note: Note) => void;
    updateNote: (id: string, updates: Partial<Note>) => void;
    deleteNote: (id: string) => void;
    toggleNoteComplete: (id: string) => void;
    clearNotes: () => void;
    setNotes: (notes: Note[]) => void;
}

export const useNotesStore = create<NotesState>((set) => ({
    notes: [],

    addNote: (note) => {
        set(state => ({
            notes: [...state.notes, note]
        }));
    },

    updateNote: (id, updates) => {
        set(state => ({
            notes: state.notes.map(n =>
                n.id === id ? { ...n, ...updates, updatedAt: new Date() } : n
            )
        }));
    },

    deleteNote: (id) => {
        set(state => ({
            notes: state.notes.filter(n => n.id !== id)
        }));
    },

    toggleNoteComplete: (id) => {
        set(state => ({
            notes: state.notes.map(n =>
                n.id === id ? { ...n, completed: !n.completed } : n
            )
        }));
    },

    clearNotes: () => set({ notes: [] }),

    setNotes: (notes) => set({ notes }),
}));


// =============================================
// AI Chat Store
// =============================================

interface AIChatState {
    messages: AIMessage[];
    isLoading: boolean;

    // Actions
    addMessage: (message: AIMessage) => void;
    updateLastMessage: (content: string) => void;
    setIsLoading: (loading: boolean) => void;
    clearMessages: () => void;
}

export const useAIChatStore = create<AIChatState>((set) => ({
    messages: [],
    isLoading: false,

    addMessage: (message) => {
        set(state => ({
            messages: [...state.messages, message]
        }));
    },

    updateLastMessage: (content) => {
        set(state => ({
            messages: state.messages.map((m, i) =>
                i === state.messages.length - 1
                    ? { ...m, content, isStreaming: false }
                    : m
            )
        }));
    },

    setIsLoading: (loading) => set({ isLoading: loading }),

    clearMessages: () => set({ messages: [] }),
}));


// =============================================
// Audio Store
// =============================================

interface AudioStoreState extends AudioState {
    setIsRecording: (recording: boolean) => void;
    setIsPaused: (paused: boolean) => void;
    setDuration: (duration: number) => void;
    setVolume: (volume: number) => void;
    setSelectedSources: (sources: string[]) => void;
}

export const useAudioStore = create<AudioStoreState>((set) => ({
    isRecording: false,
    isPaused: false,
    duration: 0,
    volume: 0,
    sources: [],
    selectedSources: [],

    setIsRecording: (recording) => set({ isRecording: recording }),
    setIsPaused: (paused) => set({ isPaused: paused }),
    setDuration: (duration) => set({ duration }),
    setVolume: (volume) => set({ volume }),
    setSelectedSources: (sources) => set({ selectedSources: sources }),
}));


// =============================================
// UI Store (Persisted)
// =============================================

interface UIStoreState extends UIState {
    togglePanel: (panel: keyof PanelState) => void;
    toggleSidebar: () => void;
    setFloatingMode: (floating: boolean) => void;
    setActiveTab: (tab: 'transcript' | 'notes' | 'ai') => void;
}

export const useUIStore = create<UIStoreState>()(
    persist(
        (set) => ({
            panels: {
                transcript: true,
                notes: true,
                aiChat: true,
                screenPreview: false,
            },
            sidebarCollapsed: false,
            floatingMode: false,
            activeTab: 'transcript',

            togglePanel: (panel) => {
                set(state => ({
                    panels: {
                        ...state.panels,
                        [panel]: !state.panels[panel]
                    }
                }));
            },

            toggleSidebar: () => {
                set(state => ({ sidebarCollapsed: !state.sidebarCollapsed }));
            },

            setFloatingMode: (floating) => set({ floatingMode: floating }),

            setActiveTab: (tab) => set({ activeTab: tab }),
        }),
        {
            name: 'meeting-assistant-ui',
        }
    )
);
