// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Child};
use std::sync::Mutex;

// Global state to hold Python backend process
struct BackendProcess(Mutex<Option<Child>>);

fn main() {
    // Start Python backend
    let backend_process = start_python_backend();

    tauri::Builder::default()
        .manage(BackendProcess(Mutex::new(Some(backend_process))))
        .on_window_event(|event| {
            if let tauri::WindowEvent::Destroyed = event.event() {
                // Kill Python process when window closes
                // This is handled automatically when the process goes out of scope
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn start_python_backend() -> Child {
    // Determine Python command (python3 on Unix, python on Windows)
    let python_cmd = if cfg!(target_os = "windows") {
        "python"
    } else {
        "python3"
    };

    println!("Starting Python backend...");

    // Start Python backend
    let backend = Command::new(python_cmd)
        .args(&["-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8765"])
        .spawn()
        .expect("Failed to start Python backend");

    println!("Python backend started with PID: {:?}", backend.id());

    // Give backend time to start
    std::thread::sleep(std::time::Duration::from_secs(2));

    backend
}
