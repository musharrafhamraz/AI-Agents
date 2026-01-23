// Tauri Commands - Bridge between frontend and backend

use serde::Serialize;
use tauri::State;
use uuid::Uuid;
use chrono::Utc;
use std::sync::Arc;
use std::path::PathBuf;

use crate::db::Database;
use crate::models::{Meeting, MeetingStatus, TranscriptEntry, Note, NoteType, AudioSource};

// Database state wrapper
pub struct AppState {
    pub db: Arc<Database>,
    pub db_path: PathBuf,
}

// ============================================================
// Meeting Commands
// ============================================================

#[tauri::command]
pub async fn start_meeting(title: String, state: State<'_, AppState>) -> Result<Meeting, String> {
    let meeting = Meeting {
        id: Uuid::new_v4().to_string(),
        title: if title.is_empty() {
            format!("Meeting {}", chrono::Local::now().format("%Y-%m-%d %H:%M"))
        } else {
            title
        },
        start_time: Utc::now(),
        end_time: None,
        participants: vec![],
        language: "en".to_string(),
        translation_target: None,
        status: MeetingStatus::Recording,
        audio_path: None,
        created_at: Utc::now(),
        updated_at: Utc::now(),
    };

    // Save to database
    state.db.save_meeting(&meeting)
        .map_err(|e| format!("Failed to save meeting: {}", e))?;

    log::info!("Started meeting: {}", meeting.id);
    Ok(meeting)
}

#[tauri::command]
pub async fn end_meeting(meeting_id: String, state: State<'_, AppState>) -> Result<Meeting, String> {
    // Get existing meeting
    let meeting = state.db.get_meeting(&meeting_id)
        .map_err(|e| format!("Database error: {}", e))?
        .ok_or_else(|| "Meeting not found".to_string())?;

    // Update meeting
    let updated_meeting = Meeting {
        end_time: Some(Utc::now()),
        status: MeetingStatus::Completed,
        updated_at: Utc::now(),
        ..meeting
    };

    state.db.save_meeting(&updated_meeting)
        .map_err(|e| format!("Failed to update meeting: {}", e))?;

    log::info!("Ended meeting: {}", meeting_id);
    Ok(updated_meeting)
}

#[tauri::command]
pub async fn pause_meeting(meeting_id: String, state: State<'_, AppState>) -> Result<(), String> {
    let meeting = state.db.get_meeting(&meeting_id)
        .map_err(|e| format!("Database error: {}", e))?
        .ok_or_else(|| "Meeting not found".to_string())?;

    let updated = Meeting {
        status: MeetingStatus::Paused,
        updated_at: Utc::now(),
        ..meeting
    };

    state.db.save_meeting(&updated)
        .map_err(|e| format!("Failed to update meeting: {}", e))?;

    log::info!("Paused meeting: {}", meeting_id);
    Ok(())
}

#[tauri::command]
pub async fn resume_meeting(meeting_id: String, state: State<'_, AppState>) -> Result<(), String> {
    let meeting = state.db.get_meeting(&meeting_id)
        .map_err(|e| format!("Database error: {}", e))?
        .ok_or_else(|| "Meeting not found".to_string())?;

    let updated = Meeting {
        status: MeetingStatus::Recording,
        updated_at: Utc::now(),
        ..meeting
    };

    state.db.save_meeting(&updated)
        .map_err(|e| format!("Failed to update meeting: {}", e))?;

    log::info!("Resumed meeting: {}", meeting_id);
    Ok(())
}

#[tauri::command]
pub async fn get_meetings(state: State<'_, AppState>) -> Result<Vec<Meeting>, String> {
    state.db.get_all_meetings()
        .map_err(|e| format!("Failed to fetch meetings: {}", e))
}

#[tauri::command]
pub async fn get_meeting(meeting_id: String, state: State<'_, AppState>) -> Result<Meeting, String> {
    state.db.get_meeting(&meeting_id)
        .map_err(|e| format!("Database error: {}", e))?
        .ok_or_else(|| "Meeting not found".to_string())
}

#[tauri::command]
pub async fn delete_meeting(meeting_id: String, state: State<'_, AppState>) -> Result<(), String> {
    state.db.delete_meeting(&meeting_id)
        .map_err(|e| format!("Failed to delete meeting: {}", e))?;
    
    log::info!("Deleted meeting: {}", meeting_id);
    Ok(())
}

// ============================================================
// Transcript Commands
// ============================================================

#[tauri::command]
pub async fn get_transcript(meeting_id: String, state: State<'_, AppState>) -> Result<Vec<TranscriptEntry>, String> {
    state.db.get_transcript(&meeting_id)
        .map_err(|e| format!("Failed to fetch transcript: {}", e))
}

#[tauri::command]
pub async fn save_transcript_entry(entry: TranscriptEntry, state: State<'_, AppState>) -> Result<(), String> {
    state.db.save_transcript_entry(&entry)
        .map_err(|e| format!("Failed to save transcript entry: {}", e))
}

#[tauri::command]
pub async fn save_transcript_batch(entries: Vec<TranscriptEntry>, state: State<'_, AppState>) -> Result<(), String> {
    state.db.save_transcript_batch(&entries)
        .map_err(|e| format!("Failed to save transcript batch: {}", e))
}

// ============================================================
// Notes Commands
// ============================================================

#[tauri::command]
pub async fn get_notes(meeting_id: String, state: State<'_, AppState>) -> Result<Vec<Note>, String> {
    state.db.get_notes(&meeting_id)
        .map_err(|e| format!("Failed to fetch notes: {}", e))
}

#[tauri::command]
pub async fn add_note(
    meeting_id: String,
    note_type: String,
    content: String,
    timestamp: i64,
    state: State<'_, AppState>,
) -> Result<Note, String> {
    let note = Note {
        id: Uuid::new_v4().to_string(),
        meeting_id,
        note_type: NoteType::from_str(&note_type),
        content,
        timestamp,
        source_refs: vec![],
        assignee: None,
        deadline: None,
        completed: false,
        created_at: Utc::now(),
        updated_at: Utc::now(),
    };

    state.db.save_note(&note)
        .map_err(|e| format!("Failed to save note: {}", e))?;
    
    Ok(note)
}

#[tauri::command]
pub async fn update_note(
    note_id: String,
    content: Option<String>,
    completed: Option<bool>,
    state: State<'_, AppState>,
) -> Result<Note, String> {
    state.db.update_note(&note_id, content.as_deref(), completed)
        .map_err(|e| format!("Failed to update note: {}", e))?;
    
    state.db.get_note(&note_id)
        .map_err(|e| format!("Failed to fetch note: {}", e))?
        .ok_or_else(|| "Note not found".to_string())
}

#[tauri::command]
pub async fn delete_note(note_id: String, state: State<'_, AppState>) -> Result<(), String> {
    state.db.delete_note(&note_id)
        .map_err(|e| format!("Failed to delete note: {}", e))
}

// ============================================================
// Export Commands
// ============================================================

#[derive(Serialize)]
pub struct ExportResult {
    pub file_path: String,
    pub content: String,
}

#[tauri::command]
pub async fn export_meeting_markdown(
    meeting_id: String, 
    include_transcript: bool,
    include_notes: bool,
    include_summary: Option<String>,
    state: State<'_, AppState>,
) -> Result<ExportResult, String> {
    // Get meeting data
    let meeting = state.db.get_meeting(&meeting_id)
        .map_err(|e| format!("Database error: {}", e))?
        .ok_or_else(|| "Meeting not found".to_string())?;

    let transcript = if include_transcript {
        state.db.get_transcript(&meeting_id)
            .map_err(|e| format!("Failed to fetch transcript: {}", e))?
    } else {
        vec![]
    };

    let notes = if include_notes {
        state.db.get_notes(&meeting_id)
            .map_err(|e| format!("Failed to fetch notes: {}", e))?
    } else {
        vec![]
    };

    // Generate markdown content
    let mut md = String::new();
    
    // Title
    md.push_str(&format!("# {}\n\n", meeting.title));
    
    // Metadata
    md.push_str("## Meeting Information\n\n");
    md.push_str(&format!("- **Date**: {}\n", meeting.start_time.format("%B %d, %Y")));
    md.push_str(&format!("- **Start Time**: {}\n", meeting.start_time.format("%H:%M")));
    if let Some(end) = meeting.end_time {
        md.push_str(&format!("- **End Time**: {}\n", end.format("%H:%M")));
        let duration = end.signed_duration_since(meeting.start_time);
        let hours = duration.num_hours();
        let mins = duration.num_minutes() % 60;
        if hours > 0 {
            md.push_str(&format!("- **Duration**: {}h {}m\n", hours, mins));
        } else {
            md.push_str(&format!("- **Duration**: {}m\n", mins));
        }
    }
    md.push_str(&format!("- **Participants**: {}\n", 
        if meeting.participants.is_empty() { 
            "N/A".to_string() 
        } else { 
            meeting.participants.iter().map(|p| p.name.clone()).collect::<Vec<_>>().join(", ")
        }
    ));
    md.push_str("\n---\n\n");

    // Summary (if provided)
    if let Some(summary) = include_summary {
        md.push_str("## Summary\n\n");
        md.push_str(&summary);
        md.push_str("\n\n---\n\n");
    }

    // Notes
    if !notes.is_empty() {
        md.push_str("## Notes\n\n");
        
        // Group notes by type
        let action_items: Vec<_> = notes.iter().filter(|n| matches!(n.note_type, NoteType::ActionItem)).collect();
        let key_points: Vec<_> = notes.iter().filter(|n| matches!(n.note_type, NoteType::KeyPoint)).collect();
        let decisions: Vec<_> = notes.iter().filter(|n| matches!(n.note_type, NoteType::Decision)).collect();
        let other_notes: Vec<_> = notes.iter().filter(|n| !matches!(n.note_type, NoteType::ActionItem | NoteType::KeyPoint | NoteType::Decision)).collect();

        if !action_items.is_empty() {
            md.push_str("### Action Items\n\n");
            for note in action_items {
                let checkbox = if note.completed { "[x]" } else { "[ ]" };
                md.push_str(&format!("- {} {}", checkbox, note.content));
                if let Some(ref assignee) = note.assignee {
                    md.push_str(&format!(" *({})*", assignee));
                }
                md.push('\n');
            }
            md.push('\n');
        }

        if !key_points.is_empty() {
            md.push_str("### Key Points\n\n");
            for note in key_points {
                md.push_str(&format!("- {}\n", note.content));
            }
            md.push('\n');
        }

        if !decisions.is_empty() {
            md.push_str("### Decisions\n\n");
            for note in decisions {
                md.push_str(&format!("- {}\n", note.content));
            }
            md.push('\n');
        }

        if !other_notes.is_empty() {
            md.push_str("### Other Notes\n\n");
            for note in other_notes {
                md.push_str(&format!("- {}\n", note.content));
            }
            md.push('\n');
        }

        md.push_str("---\n\n");
    }

    // Transcript
    if !transcript.is_empty() {
        md.push_str("## Transcript\n\n");
        
        for entry in &transcript {
            let time = format_timestamp(entry.timestamp);
            md.push_str(&format!("**[{}] {}**: {}\n\n", time, entry.speaker_name, entry.text));
        }
    }

    // Footer
    md.push_str("\n---\n\n");
    md.push_str(&format!("*Exported from Meeting Assistant on {}*\n", Utc::now().format("%Y-%m-%d %H:%M UTC")));

    Ok(ExportResult {
        file_path: format!("{}.md", meeting.title.replace(" ", "_").replace("/", "-")),
        content: md,
    })
}

fn format_timestamp(ms: i64) -> String {
    let total_secs = ms / 1000;
    let hours = total_secs / 3600;
    let mins = (total_secs % 3600) / 60;
    let secs = total_secs % 60;

    if hours > 0 {
        format!("{:02}:{:02}:{:02}", hours, mins, secs)
    } else {
        format!("{:02}:{:02}", mins, secs)
    }
}

// ============================================================
// AI Commands
// ============================================================

#[derive(Serialize)]
pub struct AIResponse {
    pub answer: String,
    pub context_used: Vec<String>,
    pub confidence: f64,
}

#[tauri::command]
pub async fn ask_ai(
    meeting_id: String,
    question: String,
) -> Result<AIResponse, String> {
    // AI is handled on the frontend for now using the AI Chat service
    log::info!("AI query for meeting {}: {}", meeting_id, question);

    Ok(AIResponse {
        answer: "AI queries are handled by the frontend service. Please use the AI chat panel.".to_string(),
        context_used: vec![],
        confidence: 0.0,
    })
}

// ============================================================
// Audio Commands
// ============================================================

#[tauri::command]
pub async fn get_audio_sources() -> Result<Vec<AudioSource>, String> {
    // Audio capture is handled by the frontend using Web Audio API
    Ok(vec![
        AudioSource {
            id: "default-mic".to_string(),
            name: "Default Microphone".to_string(),
            source_type: "microphone".to_string(),
            is_default: true,
        },
    ])
}

#[tauri::command]
pub async fn set_audio_sources(source_ids: Vec<String>) -> Result<(), String> {
    log::info!("Set audio sources: {:?}", source_ids);
    Ok(())
}

// ============================================================
// HTTP Proxy Commands (for CORS bypass)
// ============================================================

use reqwest;
use serde_json::Value;

#[tauri::command]
pub async fn http_post(
    url: String,
    headers: std::collections::HashMap<String, String>,
    body: Vec<u8>,
    content_type: String,
) -> Result<Value, String> {
    let client = reqwest::Client::new();
    
    let mut request = client.post(&url);
    
    // Add headers
    for (key, value) in headers {
        request = request.header(&key, &value);
    }
    
    // Add body
    request = request.header("Content-Type", content_type);
    request = request.body(body);
    
    // Send request
    let response = request.send().await
        .map_err(|e| format!("HTTP request failed: {}", e))?;
    
    // Check status
    if !response.status().is_success() {
        let status = response.status();
        let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
        return Err(format!("HTTP {} error: {}", status, error_text));
    }
    
    // Parse JSON response
    let json = response.json::<Value>().await
        .map_err(|e| format!("Failed to parse JSON response: {}", e))?;
    
    Ok(json)
}

#[tauri::command]
pub async fn http_get(
    url: String,
    headers: std::collections::HashMap<String, String>,
) -> Result<Value, String> {
    let client = reqwest::Client::new();
    
    let mut request = client.get(&url);
    
    // Add headers
    for (key, value) in headers {
        request = request.header(&key, &value);
    }
    
    // Send request
    let response = request.send().await
        .map_err(|e| format!("HTTP request failed: {}", e))?;
    
    // Check status
    if !response.status().is_success() {
        let status = response.status();
        let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
        return Err(format!("HTTP {} error: {}", status, error_text));
    }
    
    // Parse JSON response
    let json = response.json::<Value>().await
        .map_err(|e| format!("Failed to parse JSON response: {}", e))?;
    
    Ok(json)
}
