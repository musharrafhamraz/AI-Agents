// Meeting Assistant - Main Tauri Application
// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod db;
mod models;

use std::sync::Arc;
use tauri::{Manager, SystemTray, SystemTrayEvent, SystemTrayMenu, CustomMenuItem};
use commands::AppState;
use db::Database;

fn main() {
    // Initialize logger
    env_logger::init();

    // Create system tray menu
    let tray_menu = SystemTrayMenu::new()
        .add_item(CustomMenuItem::new("show", "Show Window"))
        .add_item(CustomMenuItem::new("hide", "Hide Window"))
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(CustomMenuItem::new("quit", "Quit"));

    let system_tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::LeftClick { .. } => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
            }
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                "hide" => {
                    let window = app.get_window("main").unwrap();
                    window.hide().unwrap();
                }
                "quit" => {
                    std::process::exit(0);
                }
                _ => {}
            },
            _ => {}
        })
        .invoke_handler(tauri::generate_handler![
            commands::start_meeting,
            commands::end_meeting,
            commands::pause_meeting,
            commands::resume_meeting,
            commands::get_meetings,
            commands::get_meeting,
            commands::delete_meeting,
            commands::get_transcript,
            commands::save_transcript_entry,
            commands::save_transcript_batch,
            commands::get_notes,
            commands::add_note,
            commands::update_note,
            commands::delete_note,
            commands::export_meeting_markdown,
            commands::ask_ai,
            commands::get_audio_sources,
            commands::set_audio_sources,
            commands::http_post,
            commands::http_get,
        ])
        .setup(|app| {
            // Initialize database
            let app_dir = app.path_resolver().app_data_dir().unwrap();
            std::fs::create_dir_all(&app_dir).unwrap();
            
            let db_path = app_dir.join("meetings.db");
            db::init_database(&db_path).expect("Failed to initialize database");
            
            // Create database wrapper
            let database = Database::new(&db_path).expect("Failed to create database connection");
            
            // Store in app state
            app.manage(AppState {
                db: Arc::new(database),
                db_path,
            });
            
            log::info!("Meeting Assistant started. Database at: {:?}", app_dir.join("meetings.db"));
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("Error while running Meeting Assistant");
}
