use tauri::State;
use std::sync::{Arc, Mutex};
use chrono::Utc;

use crate::activity::monitor::ActivityMonitor;
use crate::database::{DbConnection, queries::{get_today_stats, get_activities_by_date_range, TodayStats, Activity}};

pub struct AppState {
    pub monitor: Arc<Mutex<ActivityMonitor>>,
}

#[tauri::command]
pub fn start_tracking(state: State<AppState>) -> Result<(), String> {
    let monitor = state.monitor.lock().map_err(|e| e.to_string())?;
    monitor.start();
    Ok(())
}

#[tauri::command]
pub fn stop_tracking(state: State<AppState>) -> Result<(), String> {
    let monitor = state.monitor.lock().map_err(|e| e.to_string())?;
    monitor.stop();
    Ok(())
}

#[tauri::command]
pub fn get_tracking_status(state: State<AppState>) -> Result<bool, String> {
    let monitor = state.monitor.lock().map_err(|e| e.to_string())?;
    Ok(monitor.is_running())
}

#[tauri::command]
pub fn get_today_statistics(db: State<DbConnection>) -> Result<TodayStats, String> {
    let conn = db.lock().map_err(|e| e.to_string())?;
    get_today_stats(&conn).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn get_activities(
    db: State<DbConnection>,
    start_timestamp: i64,
    end_timestamp: i64,
) -> Result<Vec<Activity>, String> {
    let conn = db.lock().map_err(|e| e.to_string())?;
    get_activities_by_date_range(&conn, start_timestamp, end_timestamp)
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn get_current_time() -> i64 {
    Utc::now().timestamp()
}

#[tauri::command]
pub fn get_activity_count(db: State<DbConnection>) -> Result<i64, String> {
    let conn = db.lock().map_err(|e| e.to_string())?;
    let count: i64 = conn
        .query_row("SELECT COUNT(*) FROM activities", [], |row| row.get(0))
        .map_err(|e| e.to_string())?;
    Ok(count)
}
