import { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Send, 
  FileText,
  MessageSquare,
  Mic,
  X,
  Sparkles,
  Users
} from 'lucide-react';
import { 
  useMeetingStore, 
  useTranscriptStore, 
  useNotesStore,
  useAIChatStore,
} from '@/store';
import { useAudioRecording, useTranscription, useAIChat, useNoteGeneration } from '@/hooks';
import { audioCapture, transcriptionService, speakerDiarizationService } from '@/services';
import { RecordingControls } from '@/components/RecordingControls';
import { AudioDeviceSelector } from '@/components/AudioDeviceSelector';
import { formatTimestamp } from '@/utils/formatters';
import './MeetingPage.css';

export function MeetingPage() {
  const navigate = useNavigate();
  const { startMeeting, pauseMeeting, resumeMeeting, endMeeting } = useMeetingStore();
  const { entries } = useTranscriptStore();
  const { notes } = useNotesStore();
  const { messages, isLoading, addMessage } = useAIChatStore();
  
  const {
    devices,
    selectedDevice,
    state: audioState,
    error: audioError,
    selectDevice,
    startRecording,
    pauseRecording,
    resumeRecording,
    stopRecording,
    refreshDevices,
    formattedDuration,
  } = useAudioRecording();

  // Transcription hook
  const {
    isConfigured: isTranscriptionConfigured,
    startTranscription,
    stopTranscription,
  } = useTranscription();

  // AI Chat hook
  const {
    isConfigured: isAIConfigured,
    sendMessage,
  } = useAIChat();

  // Note generation hook
  const {
    generateNotesNow,
    isGenerating,
  } = useNoteGeneration();
  
  const [activeTab, setActiveTab] = useState<'transcript' | 'notes'>('transcript');
  const [aiQuestion, setAiQuestion] = useState('');
  const [showAudioSettings, setShowAudioSettings] = useState(false);
  const [showSpeakers, setShowSpeakers] = useState(false);
  const [speakers, setSpeakers] = useState<any[]>([]);

  // Subscribe to audio chunks for transcription
  useEffect(() => {
    const unsubscribe = audioCapture.onAudioChunk((chunk) => {
      if (isTranscriptionConfigured) {
        transcriptionService.addAudioChunk(chunk);
      }
    });
    return unsubscribe;
  }, [isTranscriptionConfigured]);

  // Update speakers list periodically
  useEffect(() => {
    if (!audioState.isRecording) return;

    const interval = setInterval(() => {
      const currentSpeakers = speakerDiarizationService.getSpeakers();
      setSpeakers(currentSpeakers);
    }, 2000);

    return () => clearInterval(interval);
  }, [audioState.isRecording]);

  // Handle start recording
  const handleStartRecording = useCallback(async () => {
    const success = await startRecording();
    if (success) {
      startMeeting('');
      // Start transcription if configured
      if (isTranscriptionConfigured) {
        startTranscription();
      }
    }
  }, [startRecording, startMeeting, isTranscriptionConfigured, startTranscription]);

  // Handle pause/resume
  const handlePauseResume = useCallback(() => {
    if (audioState.isPaused) {
      resumeRecording();
      resumeMeeting();
    } else {
      pauseRecording();
      pauseMeeting();
    }
  }, [audioState.isPaused, pauseRecording, resumeRecording, pauseMeeting, resumeMeeting]);

  // Handle stop recording
  const handleStopRecording = useCallback(async () => {
    stopTranscription();
    await stopRecording();
    endMeeting();
    navigate('/history');
  }, [stopRecording, stopTranscription, endMeeting, navigate]);

  const handleAskQuestion = async () => {
    if (!aiQuestion.trim()) return;
    
    const question = aiQuestion;
    setAiQuestion('');
    
    if (isAIConfigured) {
      await sendMessage(question);
    } else {
      // Fallback for when AI is not configured
      addMessage({
        id: crypto.randomUUID(),
        role: 'user',
        content: question,
        timestamp: new Date(),
      });
      addMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'AI is not configured. Please add your API key in Settings to enable AI features.',
        timestamp: new Date(),
      });
    }
  };

  return (
    <div className="meeting-page">
      {/* Audio Settings Modal */}
      {showAudioSettings && (
        <div className="modal-overlay" onClick={() => setShowAudioSettings(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Audio Settings</h3>
              <button className="close-btn" onClick={() => setShowAudioSettings(false)}>
                <X />
              </button>
            </div>
            <AudioDeviceSelector
              devices={devices}
              selectedDevice={selectedDevice}
              onSelectDevice={selectDevice}
              onRefresh={refreshDevices}
              error={audioError}
              disabled={audioState.isRecording}
            />
          </div>
        </div>
      )}

      {/* Speakers Modal */}
      {showSpeakers && (
        <div className="modal-overlay" onClick={() => setShowSpeakers(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Identified Speakers</h3>
              <button className="close-btn" onClick={() => setShowSpeakers(false)}>
                <X />
              </button>
            </div>
            <div className="speakers-list">
              {speakers.length === 0 ? (
                <p className="empty-message">No speakers identified yet. Start speaking to detect speakers.</p>
              ) : (
                speakers.map(speaker => (
                  <div key={speaker.id} className="speaker-item">
                    <div 
                      className="speaker-color" 
                      style={{ backgroundColor: speaker.color }}
                    />
                    <div className="speaker-info">
                      <strong>{speaker.name}</strong>
                      <span className="speaker-stats">
                        {speaker.utteranceCount} utterances
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Left Panel: Transcript/Notes */}
      <div className="meeting-panel panel-left">
        <div className="panel-tabs">
          <button 
            className={`panel-tab ${activeTab === 'transcript' ? 'active' : ''}`}
            onClick={() => setActiveTab('transcript')}
          >
            <Mic className="tab-icon" />
            Transcript
          </button>
          <button 
            className={`panel-tab ${activeTab === 'notes' ? 'active' : ''}`}
            onClick={() => setActiveTab('notes')}
          >
            <FileText className="tab-icon" />
            Notes ({notes.length})
          </button>
          {audioState.isRecording && speakers.length > 0 && (
            <button 
              className="panel-tab speakers-btn"
              onClick={() => setShowSpeakers(true)}
              title="View speakers"
            >
              <Users className="tab-icon" />
              {speakers.length}
            </button>
          )}
        </div>
        
        <div className="panel-content">
          {activeTab === 'transcript' ? (
            <TranscriptView entries={entries} isRecording={audioState.isRecording} />
          ) : (
            <NotesView 
              notes={notes} 
              onGenerateNotes={generateNotesNow}
              isGenerating={isGenerating}
              isRecording={audioState.isRecording}
            />
          )}
        </div>
      </div>

      {/* Right Panel: AI Chat */}
      <div className="meeting-panel panel-right">
        <div className="panel-header">
          <MessageSquare className="header-icon" />
          <span>AI Assistant</span>
        </div>
        
        <div className="ai-chat-messages">
          {messages.length === 0 ? (
            <div className="ai-empty-state">
              <MessageSquare className="empty-icon" />
              <p>Ask anything about this meeting</p>
              <span className="empty-hint">
                Try: "What was the main decision?" or "Summarize the last 5 minutes"
              </span>
            </div>
          ) : (
            messages.map((message: { id: string; role: string; content: string }) => (
              <div 
                key={message.id} 
                className={`ai-message ${message.role}`}
              >
                {message.content}
              </div>
            ))
          )}
        </div>
        
        <div className="ai-chat-input">
          <input
            type="text"
            placeholder="Ask a question..."
            value={aiQuestion}
            onChange={(e) => setAiQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
            disabled={!audioState.isRecording}
          />
          <button 
            className="send-button"
            onClick={handleAskQuestion}
            disabled={!aiQuestion.trim() || isLoading || !audioState.isRecording}
          >
            <Send />
          </button>
        </div>
      </div>

      {/* Bottom Control Bar */}
      <div className="meeting-controls-wrapper">
        <RecordingControls
          isRecording={audioState.isRecording}
          isPaused={audioState.isPaused}
          duration={formattedDuration}
          volume={audioState.volume}
          onStart={handleStartRecording}
          onPause={handlePauseResume}
          onResume={handlePauseResume}
          onStop={handleStopRecording}
          onSettings={() => setShowAudioSettings(true)}
        />
      </div>
    </div>
  );
}

// Transcript View Component
function TranscriptView({ entries, isRecording }: { entries: any[]; isRecording: boolean }) {
  if (entries.length === 0) {
    return (
      <div className="empty-panel">
        <Mic className="empty-icon" />
        <p>{isRecording ? 'Listening...' : 'Start recording to begin'}</p>
        <span>
          {isRecording 
            ? 'Your words will appear here as you speak'
            : 'Click "Start Recording" to capture your meeting'
          }
        </span>
      </div>
    );
  }

  return (
    <div className="transcript-list">
      {entries.map(entry => (
        <div key={entry.id} className="transcript-entry">
          <div className="entry-header">
            <span className="entry-speaker">{entry.speakerName}</span>
            <span className="entry-time">{formatTimestamp(entry.timestamp)}</span>
          </div>
          <p className="entry-text">{entry.text}</p>
        </div>
      ))}
    </div>
  );
}

// Notes View Component
function NotesView({ 
  notes, 
  onGenerateNotes, 
  isGenerating,
  isRecording 
}: { 
  notes: any[]; 
  onGenerateNotes: () => void;
  isGenerating: boolean;
  isRecording: boolean;
}) {
  if (notes.length === 0) {
    return (
      <div className="empty-panel">
        <FileText className="empty-icon" />
        <p>No notes yet</p>
        <span>AI will automatically generate notes as the meeting progresses</span>
        {isRecording && (
          <button 
            className="generate-notes-btn"
            onClick={onGenerateNotes}
            disabled={isGenerating}
          >
            <Sparkles />
            {isGenerating ? 'Generating...' : 'Generate Notes Now'}
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="notes-list">
      {isRecording && (
        <div className="notes-header">
          <button 
            className="generate-notes-btn small"
            onClick={onGenerateNotes}
            disabled={isGenerating}
          >
            <Sparkles />
            {isGenerating ? 'Generating...' : 'Generate More Notes'}
          </button>
        </div>
      )}
      {notes.map(note => (
        <div key={note.id} className={`note-item note-${note.type}`}>
          <span className="note-type">{note.type.replace('-', ' ')}</span>
          <p className="note-content">{note.content}</p>
          <span className="note-time">{formatTimestamp(note.timestamp)}</span>
        </div>
      ))}
    </div>
  );
}
