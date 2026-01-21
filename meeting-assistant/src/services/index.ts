// Services barrel export
export { audioCapture } from './audioCapture';
export type { AudioDevice, RecordingState, AudioChunk } from './audioCapture';

export { transcriptionService } from './transcription';
export type { TranscriptionResult, TranscriptionConfig } from './transcription';

export { aiChatService } from './aiChat';
export type { ChatMessage, AIProvider, AIConfig, AIResponse } from './aiChat';

export { databaseService } from './database';
export type { Meeting, Participant, TranscriptEntry, Note, ExportResult } from './database';

export { speakerDiarizationService } from './speakerDiarization';
export type { SpeakerSegment, DiarizationConfig } from './speakerDiarization';

export { noteGenerationService } from './noteGeneration';
export type { NoteGenerationConfig } from './noteGeneration';

export { screenCaptureService } from './screenCapture';
export type { ScreenCaptureConfig } from './screenCapture';
