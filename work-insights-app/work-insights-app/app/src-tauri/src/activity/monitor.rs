use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use chrono::Utc;

use crate::database::{DbConnection, queries::{Activity, insert_activity}};
use super::get_current_activity;

pub struct ActivityMonitor {
    db: DbConnection,
    is_running: Arc<Mutex<bool>>,
    last_activity: Arc<Mutex<Option<String>>>,
    last_timestamp: Arc<Mutex<i64>>,
}

impl ActivityMonitor {
    pub fn new(db: DbConnection) -> Self {
        Self {
            db,
            is_running: Arc::new(Mutex::new(false)),
            last_activity: Arc::new(Mutex::new(None)),
            last_timestamp: Arc::new(Mutex::new(Utc::now().timestamp())),
        }
    }

    pub fn start(&self) {
        let mut is_running = self.is_running.lock().unwrap();
        *is_running = true;
        
        let db = Arc::clone(&self.db);
        let is_running_clone = Arc::clone(&self.is_running);
        let last_activity = Arc::clone(&self.last_activity);
        let last_timestamp = Arc::clone(&self.last_timestamp);

        thread::spawn(move || {
            loop {
                thread::sleep(Duration::from_secs(10));

                let should_continue = {
                    let running = is_running_clone.lock().unwrap();
                    *running
                };

                if !should_continue {
                    break;
                }

                if let Some(snapshot) = get_current_activity() {
                    let current_key = format!("{}:{}", snapshot.app_name, snapshot.window_title);
                    let now = Utc::now().timestamp();

                    let (should_insert, duration, _prev_app) = {
                        let mut last_act = last_activity.lock().unwrap();
                        let mut last_ts = last_timestamp.lock().unwrap();

                        let duration = (now - *last_ts) as i32;
                        let prev_app = last_act.clone();
                        
                        if let Some(ref last_key) = *last_act {
                            if last_key != &current_key {
                                // Activity changed, insert the previous activity
                                let old_key = last_key.clone();
                                *last_act = Some(current_key.clone());
                                *last_ts = now;
                                (true, duration, Some(old_key))
                            } else {
                                // Same activity, just update timestamp
                                *last_ts = now;
                                (false, 0, None)
                            }
                        } else {
                            // First activity
                            *last_act = Some(current_key.clone());
                            *last_ts = now;
                            (false, 0, None)
                        }
                    };

                    if should_insert && duration > 0 {
                        if let Some(prev_key) = _prev_app {
                            let parts: Vec<&str> = prev_key.split(':').collect();
                            if parts.len() >= 2 {
                                let activity = Activity {
                                    id: None,
                                    timestamp: now - duration as i64,
                                    app_name: parts[0].to_string(),
                                    window_title: Some(parts[1..].join(":")),
                                    duration_seconds: duration,
                                    is_idle: false,
                                    category: None,
                                };

                                if let Ok(conn) = db.lock() {
                                    match insert_activity(&conn, &activity) {
                                        Ok(id) => {
                                            println!("✅ Inserted activity: {} for {}s (ID: {})", activity.app_name, duration, id);
                                        }
                                        Err(e) => {
                                            eprintln!("❌ Failed to insert activity: {}", e);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        });
    }

    pub fn stop(&self) {
        let mut is_running = self.is_running.lock().unwrap();
        *is_running = false;
    }

    pub fn is_running(&self) -> bool {
        *self.is_running.lock().unwrap()
    }
}
