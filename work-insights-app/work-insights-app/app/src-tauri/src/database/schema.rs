use rusqlite::{Connection, Result};

pub fn create_tables(conn: &Connection) -> Result<()> {
    // Activities table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            app_name TEXT NOT NULL,
            window_title TEXT,
            duration_seconds INTEGER NOT NULL DEFAULT 0,
            is_idle BOOLEAN NOT NULL DEFAULT 0,
            category TEXT
        )",
        [],
    )?;

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_timestamp ON activities(timestamp)",
        [],
    )?;

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_app_name ON activities(app_name)",
        [],
    )?;

    // Settings table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )",
        [],
    )?;

    // Insights cache table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS insights_cache (
            week_start INTEGER PRIMARY KEY,
            insights_json TEXT NOT NULL,
            generated_at INTEGER NOT NULL
        )",
        [],
    )?;

    // Initialize default settings if not exists
    conn.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES 
            ('tracking_enabled', 'true'),
            ('idle_timeout_seconds', '300'),
            ('data_retention_days', '30'),
            ('blocked_apps', '[]')",
        [],
    )?;

    Ok(())
}
