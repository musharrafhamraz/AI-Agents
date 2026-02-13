// Simplified Windows activity tracking
// This is a placeholder implementation that avoids complex Windows API calls
// TODO: Implement proper window tracking with safer FFI bindings

use super::ActivitySnapshot;
use chrono::Utc;

#[cfg(windows)]
pub fn get_active_window() -> Option<ActivitySnapshot> {
    // Generate varying mock data to simulate activity changes
    let timestamp = Utc::now().timestamp();
    let app_index = (timestamp / 10) % 3; // Change app every 10 seconds
    
    let (app_name, window_title) = match app_index {
        0 => ("Visual Studio Code", "work-insights-app - Dashboard.tsx"),
        1 => ("Google Chrome", "Work Insights Documentation"),
        2 => ("Terminal", "PowerShell"),
        _ => ("System", "Desktop"),
    };
    
    Some(ActivitySnapshot {
        app_name: String::from(app_name),
        window_title: String::from(window_title),
        timestamp,
    })
}
