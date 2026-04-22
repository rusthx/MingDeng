// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use portpicker::pick_unused_port;
#[cfg(windows)]
use std::os::windows::process::CommandExt;
use std::{
    env,
    path::{Path, PathBuf},
    process::{Child, Command, Stdio},
    sync::Mutex,
    time::Duration,
};

use tauri::{AppHandle, Manager, State, WindowEvent};

struct BackendHandle {
    child: Child,
    port: u16,
}

struct BackendState(Mutex<Option<BackendHandle>>);

impl BackendState {
    fn set(&self, child: Child, port: u16) {
        let mut guard = self.0.lock().expect("failed to lock backend state");
        *guard = Some(BackendHandle { child, port });
    }

    fn origin(&self) -> Option<String> {
        self.0.lock().ok().and_then(|guard| {
            guard
                .as_ref()
                .map(|backend| format!("http://127.0.0.1:{}", backend.port))
        })
    }

    fn shutdown(&self) {
        if let Ok(mut guard) = self.0.lock() {
            if let Some(mut backend) = guard.take() {
                let _ = backend.child.kill();
            }
        }
    }
}

#[tauri::command]
async fn ensure_backend(app: AppHandle, state: State<'_, BackendState>) -> Result<String, String> {
    // 如果已有后端，先检查是否还存活
    if let Some(origin) = state.origin() {
        if let Ok(resp) = reqwest::get(format!("{}/", origin)).await {
            if resp.status().is_success() {
                return Ok(origin);
            }
        }
        state.shutdown();
    }

    let backend_dir = resolve_backend_dir(&app)?;
    let python = resolve_python(&backend_dir)?;
    let port = pick_unused_port().ok_or_else(|| "No free port found".to_string())?;
    let data_dir = resolve_data_dir(&app, &backend_dir)?;
    std::fs::create_dir_all(&data_dir).map_err(|e| e.to_string())?;

    // 智能选择日志路径：C盘安装时用 AppData 避免权限问题，其他盘写到安装目录
    let install_dir = backend_dir.parent().unwrap_or(&backend_dir);
    let log_dir = if install_dir
        .to_string_lossy()
        .to_lowercase()
        .starts_with("c:\\")
    {
        data_dir.clone()
    } else {
        let dir = install_dir.join("logs");
        std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
        dir
    };
    let log_path = log_dir.join("mingdeng_backend.log");
    let log_file = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_path)
        .map_err(|e| format!("Failed to create log file: {e}"))?;

    let mut cmd = Command::new(&python);
    cmd.current_dir(&backend_dir);
    cmd.env("MINGDENG_DATA_DIR", &data_dir);
    cmd.env("PYTHONUNBUFFERED", "1");
    cmd.args([
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        "0.0.0.0",
        "--port",
        &port.to_string(),
    ]);
    cmd.stdout(Stdio::from(
        log_file.try_clone().map_err(|e| e.to_string())?,
    ));
    cmd.stderr(Stdio::from(log_file));

    // Windows: 隐藏 Python 进程的控制台窗口
    #[cfg(windows)]
    cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW

    let mut child = cmd
        .spawn()
        .map_err(|e| format!("Failed to start Python backend: {e}"))?;

    // 轮询健康检查，最多等待 15 秒
    tokio::time::sleep(Duration::from_millis(300)).await;
    let origin = format!("http://127.0.0.1:{port}");
    for _ in 0..294 {
        tokio::time::sleep(Duration::from_millis(50)).await;

        // 检查子进程是否提前退出
        match child.try_wait() {
            Ok(Some(status)) => {
                let log_content = std::fs::read_to_string(&log_path).unwrap_or_default();
                let recent_logs = log_content
                    .lines()
                    .rev()
                    .take(20)
                    .collect::<Vec<_>>()
                    .join("\n");
                return Err(format!(
                    "Python backend exited early with code: {:?}\nLog: {}\nRecent logs:\n{}",
                    status.code(),
                    log_path.to_string_lossy(),
                    if recent_logs.is_empty() {
                        "(empty)"
                    } else {
                        &recent_logs
                    }
                ));
            }
            Err(e) => return Err(format!("Failed to check child status: {e}")),
            Ok(None) => {}
        }

        if let Ok(resp) = reqwest::get(format!("{}/", origin)).await {
            if resp.status().is_success() {
                state.set(child, port);
                return Ok(origin);
            }
        }
    }

    // 健康检查失败，读取日志并返回详细信息
    let _ = child.kill();
    let log_content = std::fs::read_to_string(&log_path).unwrap_or_default();
    let recent_logs = log_content
        .lines()
        .rev()
        .take(20)
        .collect::<Vec<_>>()
        .join("\n");
    Err(format!(
        "Python backend did not respond within 15 seconds.\nLog: {}\nRecent logs:\n{}",
        log_path.to_string_lossy(),
        if recent_logs.is_empty() {
            "(empty or unreadable)"
        } else {
            &recent_logs
        }
    ))
}

fn resolve_backend_dir(app: &AppHandle) -> Result<PathBuf, String> {
    if let Ok(resource_dir) = app.path().resource_dir() {
        let packaged = resource_dir.join("backend");
        if packaged.exists() {
            return Ok(packaged);
        }
    }

    let base = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    if let Some(parent) = base.parent() {
        let dev_path = parent.join("backend");
        if dev_path.exists() {
            return Ok(dev_path);
        }
    }

    let sibling = base.join("backend");
    if sibling.exists() {
        return Ok(sibling);
    }

    Err("Backend directory not found. Ensure it is bundled or present next to src-tauri.".into())
}

fn resolve_python(backend_dir: &Path) -> Result<PathBuf, String> {
    if let Ok(env_path) = env::var("MINGDENG_PYTHON") {
        return Ok(PathBuf::from(env_path));
    }

    let mut candidates = Vec::new();
    if let Some(parent) = backend_dir.parent() {
        // Windows 嵌入式 Python (CI 打包时使用，exe 直接在根目录)
        candidates.push(parent.join("backend-venv").join("python.exe"));
        // Linux/macOS 标准 venv
        candidates.push(parent.join("backend-venv").join("bin").join("python"));
        // Windows 标准 venv (本地开发时使用)
        candidates.push(
            parent
                .join("backend-venv")
                .join("Scripts")
                .join("python.exe"),
        );
    }

    for path in &candidates {
        if path.exists() {
            return Ok(path.clone());
        }
    }

    // 开发环境回退：检测系统 Python 是否可用
    let default = if cfg!(windows) { "python" } else { "python3" };
    let fallback = PathBuf::from(default);
    if Command::new(&fallback)
        .arg("--version")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
    {
        return Ok(fallback);
    }

    Err(format!(
        "Python executable not found. Checked: {}. Please install Python or ensure backend-venv is bundled.",
        candidates.iter().map(|p| p.display().to_string()).collect::<Vec<_>>().join(", ")
    ))
}

fn resolve_data_dir(app: &AppHandle, backend_dir: &Path) -> Result<PathBuf, String> {
    if let Ok(dir) = app.path().app_data_dir() {
        return Ok(dir);
    }

    Ok(backend_dir.join("data"))
}

fn main() {
    tauri::Builder::default()
        .manage(BackendState(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![ensure_backend])
        .on_window_event(|window, event| {
            if matches!(event, WindowEvent::Destroyed) {
                let state = window.state::<BackendState>();
                state.shutdown();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
