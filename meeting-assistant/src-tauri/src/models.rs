// Data Models

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

// ============================================================
// Meeting
// ============================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Meeting {
    pub id: String,
    pub title: String,
    pub start_time: DateTime<Utc>,
    pub end_time: Option<DateTime<Utc>>,
    pub participants: Vec<Participant>,
    pub language: String,
    pub translation_target: Option<String>,
    pub status: MeetingStatus,
    pub audio_path: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum MeetingStatus {
    Idle,
    Recording,
    Paused,
    Completed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Participant {
    pub id: String,
    pub name: String,
    pub color: String,
    pub is_local: bool,
}

// ============================================================
// Transcript
// ============================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TranscriptEntry {
    pub id: String,
    pub meeting_id: String,
    pub speaker_id: String,
    pub speaker_name: String,
    pub text: String,
    pub timestamp: i64, // milliseconds from meeting start
    pub end_timestamp: i64,
    pub confidence: f64,
    pub language: String,
    pub translation: Option<String>,
    pub created_at: DateTime<Utc>,
}

// ============================================================
// Notes
// ============================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Note {
    pub id: String,
    pub meeting_id: String,
    pub note_type: NoteType,
    pub content: String,
    pub timestamp: i64,
    pub source_refs: Vec<String>,
    pub assignee: Option<String>,
    pub deadline: Option<DateTime<Utc>>,
    pub completed: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum NoteType {
    KeyPoint,
    ActionItem,
    Decision,
    Question,
    FollowUp,
    Manual,
}

impl NoteType {
    pub fn from_str(s: &str) -> Self {
        match s {
            "key-point" => NoteType::KeyPoint,
            "action-item" => NoteType::ActionItem,
            "decision" => NoteType::Decision,
            "question" => NoteType::Question,
            "follow-up" => NoteType::FollowUp,
            _ => NoteType::Manual,
        }
    }
}

// ============================================================
// Screen Capture
// ============================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScreenCapture {
    pub id: String,
    pub meeting_id: String,
    pub timestamp: i64,
    pub image_path: String,
    pub ocr_text: String,
    pub relevance_score: f64,
    pub created_at: DateTime<Utc>,
}

// ============================================================
// AI
// ============================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIQuery {
    pub id: String,
    pub meeting_id: String,
    pub question: String,
    pub answer: String,
    pub timestamp: i64,
    pub context_used: Vec<String>,
    pub confidence: f64,
    pub created_at: DateTime<Utc>,
}

// ============================================================
// Audio
// ============================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AudioSource {
    pub id: String,
    pub name: String,
    pub source_type: String, // microphone, system, virtual
    pub is_default: bool,
}

// ============================================================
// Meeting Summary
// ============================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MeetingSummary {
    pub id: String,
    pub meeting_id: String,
    pub executive_summary: String,
    pub key_decisions: Vec<String>,
    pub action_items: Vec<Note>,
    pub topics: Vec<TopicSummary>,
    pub duration: i64,
    pub participant_count: usize,
    pub generated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TopicSummary {
    pub id: String,
    pub title: String,
    pub summary: String,
    pub start_time: i64,
    pub end_time: i64,
    pub key_points: Vec<String>,
}
