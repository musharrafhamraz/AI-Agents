pub mod monitor;

#[cfg(windows)]
pub mod windows;

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActivitySnapshot {
    pub app_name: String,
    pub window_title: String,
    pub timestamp: i64,
}

pub fn get_current_activity() -> Option<ActivitySnapshot> {
    #[cfg(windows)]
    return windows::get_active_window();

    #[cfg(not(windows))]
    {
        // Placeholder for other platforms
        None
    }
}
