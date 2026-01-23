// Database Module - SQLite operations

use rusqlite::{Connection, Result, params, OptionalExtension};
use std::path::Path;
use std::sync::Mutex;
use chrono::{DateTime, Utc};

use crate::models::{Meeting, MeetingStatus, Participant, TranscriptEntry, Note, NoteType};

/// Database wrapper for thread-safe access
pub struct Database {
    conn: Mutex<Connection>,
}

impl Database {
    pub fn new(db_path: &Path) -> Result<Self> {
        let conn = Connection::open(db_path)?;
        // Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON", [])?;
        Ok(Database {
            conn: Mutex::new(conn),
        })
    }

    // ========================================
    // Meeting Operations
    // ========================================

    pub fn save_meeting(&self, meeting: &Meeting) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        
        conn.execute(
            "INSERT OR REPLACE INTO meetings (id, title, start_time, end_time, language, translation_target, status, audio_path, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)",
            params![
                meeting.id,
                meeting.title,
                meeting.start_time.to_rfc3339(),
                meeting.end_time.map(|t| t.to_rfc3339()),
                meeting.language,
                meeting.translation_target,
                status_to_string(&meeting.status),
                meeting.audio_path,
                meeting.created_at.to_rfc3339(),
                meeting.updated_at.to_rfc3339(),
            ],
        )?;

        // Save participants
        for participant in &meeting.participants {
            conn.execute(
                "INSERT OR REPLACE INTO participants (id, meeting_id, name, color, is_local)
                 VALUES (?1, ?2, ?3, ?4, ?5)",
                params![
                    participant.id,
                    meeting.id,
                    participant.name,
                    participant.color,
                    participant.is_local as i32,
                ],
            )?;
        }

        Ok(())
    }

    pub fn get_meeting(&self, meeting_id: &str) -> Result<Option<Meeting>> {
        let conn = self.conn.lock().unwrap();
        
        let mut stmt = conn.prepare(
            "SELECT id, title, start_time, end_time, language, translation_target, status, audio_path, created_at, updated_at
             FROM meetings WHERE id = ?1"
        )?;

        let meeting = stmt.query_row(params![meeting_id], |row| {
            Ok(Meeting {
                id: row.get(0)?,
                title: row.get(1)?,
                start_time: parse_datetime(row.get::<_, String>(2)?),
                end_time: row.get::<_, Option<String>>(3)?.map(parse_datetime),
                participants: vec![], // Will be populated below
                language: row.get(4)?,
                translation_target: row.get(5)?,
                status: string_to_status(&row.get::<_, String>(6)?),
                audio_path: row.get(7)?,
                created_at: parse_datetime(row.get::<_, String>(8)?),
                updated_at: parse_datetime(row.get::<_, String>(9)?),
            })
        }).optional()?;

        if let Some(mut meeting) = meeting {
            // Get participants
            meeting.participants = self.get_participants(&meeting.id)?;
            Ok(Some(meeting))
        } else {
            Ok(None)
        }
    }

    pub fn get_all_meetings(&self) -> Result<Vec<Meeting>> {
        let conn = self.conn.lock().unwrap();
        
        let mut stmt = conn.prepare(
            "SELECT id, title, start_time, end_time, language, translation_target, status, audio_path, created_at, updated_at
             FROM meetings ORDER BY start_time DESC"
        )?;

        let meetings_iter = stmt.query_map([], |row| {
            Ok(Meeting {
                id: row.get(0)?,
                title: row.get(1)?,
                start_time: parse_datetime(row.get::<_, String>(2)?),
                end_time: row.get::<_, Option<String>>(3)?.map(parse_datetime),
                participants: vec![],
                language: row.get(4)?,
                translation_target: row.get(5)?,
                status: string_to_status(&row.get::<_, String>(6)?),
                audio_path: row.get(7)?,
                created_at: parse_datetime(row.get::<_, String>(8)?),
                updated_at: parse_datetime(row.get::<_, String>(9)?),
            })
        })?;

        let mut meetings = Vec::new();
        for meeting in meetings_iter {
            let mut m = meeting?;
            m.participants = self.get_participants(&m.id)?;
            meetings.push(m);
        }
        
        Ok(meetings)
    }

    pub fn delete_meeting(&self, meeting_id: &str) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute("DELETE FROM meetings WHERE id = ?1", params![meeting_id])?;
        Ok(())
    }

    fn get_participants(&self, meeting_id: &str) -> Result<Vec<Participant>> {
        let conn = self.conn.lock().unwrap();
        
        let mut stmt = conn.prepare(
            "SELECT id, name, color, is_local FROM participants WHERE meeting_id = ?1"
        )?;

        let participants = stmt.query_map(params![meeting_id], |row| {
            Ok(Participant {
                id: row.get(0)?,
                name: row.get(1)?,
                color: row.get(2)?,
                is_local: row.get::<_, i32>(3)? != 0,
            })
        })?.collect::<Result<Vec<_>, _>>()?;

        Ok(participants)
    }

    // ========================================
    // Transcript Operations
    // ========================================

    pub fn save_transcript_entry(&self, entry: &TranscriptEntry) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        
        conn.execute(
            "INSERT OR REPLACE INTO transcript_entries (id, meeting_id, speaker_id, speaker_name, text, timestamp, end_timestamp, confidence, language, translation, created_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)",
            params![
                entry.id,
                entry.meeting_id,
                entry.speaker_id,
                entry.speaker_name,
                entry.text,
                entry.timestamp,
                entry.end_timestamp,
                entry.confidence,
                entry.language,
                entry.translation,
                entry.created_at.to_rfc3339(),
            ],
        )?;

        Ok(())
    }

    pub fn get_transcript(&self, meeting_id: &str) -> Result<Vec<TranscriptEntry>> {
        let conn = self.conn.lock().unwrap();
        
        let mut stmt = conn.prepare(
            "SELECT id, meeting_id, speaker_id, speaker_name, text, timestamp, end_timestamp, confidence, language, translation, created_at
             FROM transcript_entries WHERE meeting_id = ?1 ORDER BY timestamp"
        )?;

        let entries = stmt.query_map(params![meeting_id], |row| {
            Ok(TranscriptEntry {
                id: row.get(0)?,
                meeting_id: row.get(1)?,
                speaker_id: row.get(2)?,
                speaker_name: row.get(3)?,
                text: row.get(4)?,
                timestamp: row.get(5)?,
                end_timestamp: row.get(6)?,
                confidence: row.get(7)?,
                language: row.get(8)?,
                translation: row.get(9)?,
                created_at: parse_datetime(row.get::<_, String>(10)?),
            })
        })?.collect::<Result<Vec<_>, _>>()?;

        Ok(entries)
    }

    pub fn save_transcript_batch(&self, entries: &[TranscriptEntry]) -> Result<()> {
        for entry in entries {
            self.save_transcript_entry(entry)?;
        }
        Ok(())
    }

    // ========================================
    // Notes Operations
    // ========================================

    pub fn save_note(&self, note: &Note) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        
        conn.execute(
            "INSERT OR REPLACE INTO notes (id, meeting_id, note_type, content, timestamp, assignee, deadline, completed, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)",
            params![
                note.id,
                note.meeting_id,
                note_type_to_string(&note.note_type),
                note.content,
                note.timestamp,
                note.assignee,
                note.deadline.map(|d| d.to_rfc3339()),
                note.completed as i32,
                note.created_at.to_rfc3339(),
                note.updated_at.to_rfc3339(),
            ],
        )?;

        Ok(())
    }

    pub fn get_notes(&self, meeting_id: &str) -> Result<Vec<Note>> {
        let conn = self.conn.lock().unwrap();
        
        let mut stmt = conn.prepare(
            "SELECT id, meeting_id, note_type, content, timestamp, assignee, deadline, completed, created_at, updated_at
             FROM notes WHERE meeting_id = ?1 ORDER BY timestamp"
        )?;

        let notes = stmt.query_map(params![meeting_id], |row| {
            Ok(Note {
                id: row.get(0)?,
                meeting_id: row.get(1)?,
                note_type: NoteType::from_str(&row.get::<_, String>(2)?),
                content: row.get(3)?,
                timestamp: row.get(4)?,
                source_refs: vec![],
                assignee: row.get(5)?,
                deadline: row.get::<_, Option<String>>(6)?.map(parse_datetime),
                completed: row.get::<_, i32>(7)? != 0,
                created_at: parse_datetime(row.get::<_, String>(8)?),
                updated_at: parse_datetime(row.get::<_, String>(9)?),
            })
        })?.collect::<Result<Vec<_>, _>>()?;

        Ok(notes)
    }

    pub fn update_note(&self, note_id: &str, content: Option<&str>, completed: Option<bool>) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        
        if let Some(c) = content {
            conn.execute(
                "UPDATE notes SET content = ?1, updated_at = ?2 WHERE id = ?3",
                params![c, Utc::now().to_rfc3339(), note_id],
            )?;
        }
        
        if let Some(comp) = completed {
            conn.execute(
                "UPDATE notes SET completed = ?1, updated_at = ?2 WHERE id = ?3",
                params![comp as i32, Utc::now().to_rfc3339(), note_id],
            )?;
        }

        Ok(())
    }

    pub fn delete_note(&self, note_id: &str) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute("DELETE FROM notes WHERE id = ?1", params![note_id])?;
        Ok(())
    }

    pub fn get_note(&self, note_id: &str) -> Result<Option<Note>> {
        let conn = self.conn.lock().unwrap();
        
        let mut stmt = conn.prepare(
            "SELECT id, meeting_id, note_type, content, timestamp, assignee, deadline, completed, created_at, updated_at
             FROM notes WHERE id = ?1"
        )?;

        let note = stmt.query_row(params![note_id], |row| {
            Ok(Note {
                id: row.get(0)?,
                meeting_id: row.get(1)?,
                note_type: NoteType::from_str(&row.get::<_, String>(2)?),
                content: row.get(3)?,
                timestamp: row.get(4)?,
                source_refs: vec![],
                assignee: row.get(5)?,
                deadline: row.get::<_, Option<String>>(6)?.map(parse_datetime),
                completed: row.get::<_, i32>(7)? != 0,
                created_at: parse_datetime(row.get::<_, String>(8)?),
                updated_at: parse_datetime(row.get::<_, String>(9)?),
            })
        }).optional()?;

        Ok(note)
    }
}

// Helper functions
fn parse_datetime(s: String) -> DateTime<Utc> {
    DateTime::parse_from_rfc3339(&s)
        .map(|dt| dt.with_timezone(&Utc))
        .unwrap_or_else(|_| Utc::now())
}

fn status_to_string(status: &MeetingStatus) -> &'static str {
    match status {
        MeetingStatus::Idle => "idle",
        MeetingStatus::Recording => "recording",
        MeetingStatus::Paused => "paused",
        MeetingStatus::Completed => "completed",
    }
}

fn string_to_status(s: &str) -> MeetingStatus {
    match s {
        "recording" => MeetingStatus::Recording,
        "paused" => MeetingStatus::Paused,
        "completed" => MeetingStatus::Completed,
        _ => MeetingStatus::Idle,
    }
}

fn note_type_to_string(note_type: &NoteType) -> &'static str {
    match note_type {
        NoteType::KeyPoint => "key-point",
        NoteType::ActionItem => "action-item",
        NoteType::Decision => "decision",
        NoteType::Question => "question",
        NoteType::FollowUp => "follow-up",
        NoteType::Manual => "manual",
    }
}

/// Initialize the SQLite database with required tables
pub fn init_database(db_path: &Path) -> Result<()> {
    let conn = Connection::open(db_path)?;

    // Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON", [])?;

    // Create meetings table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            language TEXT NOT NULL DEFAULT 'en',
            translation_target TEXT,
            status TEXT NOT NULL DEFAULT 'idle',
            audio_path TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )",
        [],
    )?;

    // Create participants table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS participants (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            is_local INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
        )",
        [],
    )?;

    // Create transcript_entries table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS transcript_entries (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            speaker_id TEXT NOT NULL,
            speaker_name TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            end_timestamp INTEGER NOT NULL,
            confidence REAL NOT NULL DEFAULT 0.0,
            language TEXT NOT NULL DEFAULT 'en',
            translation TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
        )",
        [],
    )?;

    // Create notes table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            note_type TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            assignee TEXT,
            deadline TEXT,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
        )",
        [],
    )?;

    // Create indexes for performance
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_transcript_meeting ON transcript_entries(meeting_id)",
        [],
    )?;
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_notes_meeting ON notes(meeting_id)",
        [],
    )?;

    log::info!("Database initialized successfully at {:?}", db_path);
    Ok(())
}

/// Get a connection to the database
pub fn get_connection(db_path: &Path) -> Result<Connection> {
    Connection::open(db_path)
}
