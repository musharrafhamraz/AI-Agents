use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use chrono::Utc;

#[derive(Debug, Serialize, Deserialize)]
pub struct Activity {
    pub id: Option<i64>,
    pub timestamp: i64,
    pub app_name: String,
    pub window_title: Option<String>,
    pub duration_seconds: i32,
    pub is_idle: bool,
    pub category: Option<String>,
}

pub fn insert_activity(conn: &Connection, activity: &Activity) -> Result<i64> {
    conn.execute(
        "INSERT INTO activities (timestamp, app_name, window_title, duration_seconds, is_idle, category)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
        params![
            activity.timestamp,
            activity.app_name,
            activity.window_title,
            activity.duration_seconds,
            activity.is_idle,
            activity.category,
        ],
    )?;
    Ok(conn.last_insert_rowid())
}

pub fn get_activities_by_date_range(
    conn: &Connection,
    start_timestamp: i64,
    end_timestamp: i64,
) -> Result<Vec<Activity>> {
    let mut stmt = conn.prepare(
        "SELECT id, timestamp, app_name, window_title, duration_seconds, is_idle, category
         FROM activities
         WHERE timestamp BETWEEN ?1 AND ?2
         ORDER BY timestamp ASC",
    )?;

    let activities = stmt
        .query_map(params![start_timestamp, end_timestamp], |row| {
            Ok(Activity {
                id: Some(row.get(0)?),
                timestamp: row.get(1)?,
                app_name: row.get(2)?,
                window_title: row.get(3)?,
                duration_seconds: row.get(4)?,
                is_idle: row.get(5)?,
                category: row.get(6)?,
            })
        })?
        .collect::<Result<Vec<_>>>()?;

    Ok(activities)
}

pub fn get_today_stats(conn: &Connection) -> Result<TodayStats> {
    let today_start = chrono::Local::now()
        .date_naive()
        .and_hms_opt(0, 0, 0)
        .unwrap()
        .and_utc()
        .timestamp();

    let mut stmt = conn.prepare(
        "SELECT 
            SUM(CASE WHEN is_idle = 0 THEN duration_seconds ELSE 0 END) as active_time,
            SUM(CASE WHEN is_idle = 1 THEN duration_seconds ELSE 0 END) as idle_time,
            COUNT(DISTINCT app_name) as app_switches
         FROM activities
         WHERE timestamp >= ?1",
    )?;

    let stats = stmt.query_row(params![today_start], |row| {
        Ok(TodayStats {
            active_time_seconds: row.get::<_, Option<i64>>(0)?.unwrap_or(0),
            idle_time_seconds: row.get::<_, Option<i64>>(1)?.unwrap_or(0),
            context_switches: row.get::<_, i64>(2)?,
        })
    })?;

    Ok(stats)
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TodayStats {
    pub active_time_seconds: i64,
    pub idle_time_seconds: i64,
    pub context_switches: i64,
}

pub fn get_setting(conn: &Connection, key: &str) -> Result<Option<String>> {
    let mut stmt = conn.prepare("SELECT value FROM settings WHERE key = ?1")?;
    let result = stmt.query_row(params![key], |row| row.get(0));
    
    match result {
        Ok(value) => Ok(Some(value)),
        Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
        Err(e) => Err(e),
    }
}

pub fn set_setting(conn: &Connection, key: &str, value: &str) -> Result<()> {
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?1, ?2)",
        params![key, value],
    )?;
    Ok(())
}

pub fn delete_old_activities(conn: &Connection, days: i64) -> Result<usize> {
    let cutoff = Utc::now().timestamp() - (days * 24 * 60 * 60);
    conn.execute("DELETE FROM activities WHERE timestamp < ?1", params![cutoff])
}
