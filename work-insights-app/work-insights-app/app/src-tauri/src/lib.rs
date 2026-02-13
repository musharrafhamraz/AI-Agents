mod database;
mod activity;
mod commands;

use std::sync::{Arc, Mutex};
use activity::monitor::ActivityMonitor;
use commands::AppState;
use tauri::Manager;
use tauri::{
    menu::{Menu, MenuItem},
    tray::{TrayIconBuilder, TrayIconEvent},
};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            Some(vec!["--minimized"]),
        ))
        .setup(|app| {
            // Initialize database
            let app_data_dir = app.path().app_data_dir()
                .expect("Failed to get app data directory");
            
            std::fs::create_dir_all(&app_data_dir).expect("Failed to create app data directory");
            
            let db_path = app_data_dir.join("work_insights.db");
            let db = database::initialize_database(db_path).expect("Failed to initialize database");
            
            // Initialize activity monitor
            let monitor = Arc::new(Mutex::new(ActivityMonitor::new(Arc::clone(&db))));
            
            // Auto-start tracking if enabled
            let should_auto_start = {
                if let Ok(conn) = db.lock() {
                    database::queries::get_setting(&conn, "auto_start_tracking")
                        .unwrap_or(Some("true".to_string()))
                        .unwrap_or("true".to_string()) == "true"
                } else {
                    true
                }
            };

            if should_auto_start {
                if let Ok(mon) = monitor.lock() {
                    mon.start();
                }
            }
            
            let app_state = AppState {
                monitor: Arc::clone(&monitor),
            };

            app.manage(db);
            app.manage(app_state);

            // Create system tray menu
            let show_i = MenuItem::with_id(app, "show", "Show Dashboard", true, None::<&str>)?;
            let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show_i, &quit_i])?;

            // Build system tray
            let _tray = TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .show_menu_on_left_click(false)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "show" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    "quit" => {
                        app.exit(0);
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click { button: tauri::tray::MouseButton::Left, .. } = event {
                        let app = tray.app_handle();
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                })
                .build(app)?;

            // Handle window close event - minimize to tray instead of closing
            if let Some(window) = app.get_webview_window("main") {
                let app_handle = app.handle().clone();
                window.on_window_event(move |event| {
                    if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                        // Prevent the window from closing
                        api.prevent_close();
                        // Hide the window instead
                        if let Some(win) = app_handle.get_webview_window("main") {
                            let _ = win.hide();
                        }
                    }
                });
            }
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::start_tracking,
            commands::stop_tracking,
            commands::get_tracking_status,
            commands::get_today_statistics,
            commands::get_activities,
            commands::get_current_time,
            commands::get_activity_count,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
