// =============================================
// Meeting Assistant - Core Type Definitions
// =============================================

// Meeting Types
export interface Meeting {
    id: string;
    title: string;
    startTime: Date;
    endTime?: Date;
    participants: Participant[];
    language: string;
    translationTarget?: string;
    status: MeetingStatus;
    audioPath?: string;
    createdAt: Date;
    updatedAt: Date;
}

export type MeetingStatus = 'idle' | 'recording' | 'paused' | 'completed';

export interface Participant {
    id: string;
    name: string;
    color: string;
    isLocal?: boolean;
}

// Transcript Types
export interface TranscriptEntry {
    id: string;
    meetingId: string;
    speakerId: string;
    speakerName: string;
    text: string;
    timestamp: number; // milliseconds from start
    endTimestamp: number;
    confidence: number;
    language: string;
    translation?: string;
    createdAt: Date;
}

export interface TranscriptSegment {
    speakerId: string;
    speakerName: string;
    entries: TranscriptEntry[];
    startTime: number;
    endTime: number;
}

// Screen Capture Types
export interface ScreenCapture {
    id: string;
    meetingId: string;
    timestamp: number;
    imagePath: string;
    ocrText: string;
    relevanceScore: number;
    createdAt: Date;
}

// Note Types
export interface Note {
    id: string;
    meetingId: string;
    type: NoteType;
    content: string;
    timestamp: number;
    sourceRefs: string[]; // transcript entry IDs
    assignee?: string;
    deadline?: Date;
    completed: boolean;
    createdAt: Date;
    updatedAt: Date;
}

export type NoteType =
    | 'key-point'
    | 'action-item'
    | 'decision'
    | 'question'
    | 'follow-up'
    | 'manual';

// AI Types
export interface AIQuery {
    id: string;
    meetingId: string;
    question: string;
    answer: string;
    timestamp: number;
    contextUsed: string[];
    confidence: number;
    createdAt: Date;
}

export interface AIMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    isStreaming?: boolean;
}

// Meeting Summary Types
export interface MeetingSummary {
    id: string;
    meetingId: string;
    executiveSummary: string;
    keyDecisions: string[];
    actionItems: Note[];
    topics: TopicSummary[];
    duration: number;
    participantCount: number;
    generatedAt: Date;
}

export interface TopicSummary {
    id: string;
    title: string;
    summary: string;
    startTime: number;
    endTime: number;
    keyPoints: string[];
}

// Audio Types
export interface AudioSource {
    id: string;
    name: string;
    type: 'microphone' | 'system' | 'virtual';
    isDefault: boolean;
}

export interface AudioState {
    isRecording: boolean;
    isPaused: boolean;
    duration: number;
    volume: number;
    sources: AudioSource[];
    selectedSources: string[];
}

// Settings Types
export interface AppSettings {
    // General
    theme: 'light' | 'dark' | 'system';
    language: string;

    // Transcription
    transcriptionLanguage: string;
    enableSpeakerDiarization: boolean;
    transcriptionModel: 'local' | 'cloud';

    // Translation
    enableTranslation: boolean;
    translationTargetLanguage: string;

    // AI
    aiProvider: 'openai' | 'anthropic' | 'local';
    aiModel: string;
    aiApiKey?: string;

    // Notes
    autoGenerateNotes: boolean;
    noteCategories: NoteType[];

    // Privacy
    enableScreenCapture: boolean;
    privacyZones: PrivacyZone[];
    localProcessingOnly: boolean;

    // Audio
    defaultAudioSources: string[];
    noiseReduction: boolean;
}

export interface PrivacyZone {
    id: string;
    name: string;
    x: number;
    y: number;
    width: number;
    height: number;
}

// UI State Types
export interface PanelState {
    transcript: boolean;
    notes: boolean;
    aiChat: boolean;
    screenPreview: boolean;
}

export interface UIState {
    panels: PanelState;
    sidebarCollapsed: boolean;
    floatingMode: boolean;
    activeTab: 'transcript' | 'notes' | 'ai';
}
