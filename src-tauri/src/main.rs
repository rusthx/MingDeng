// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use portpicker::pick_unused_port;
#[cfg(windows)]
use std::os::windows::process::CommandExt;
use std::{
    env,
    io::{BufRead, Write},
    path::{Path, PathBuf},
    process::{Child, Command, Stdio},
    // sync::Mutex replaced by tokio::sync::Mutex below
    thread,
    time::Duration,
};

use tauri::{AppHandle, Manager, State, WindowEvent};
use tokio::sync::Mutex;

struct BackendHandle {
    child: Child,
    port: u16,
}

struct BackendState(Mutex<Option<BackendHandle>>);

impl BackendState {
    async fn set(&self, child: Child, port: u16) {
        let mut guard = self.0.lock().await;
        *guard = Some(BackendHandle { child, port });
    }

    async fn origin(&self) -> Option<String> {
        let guard = self.0.lock().await;
        guard
            .as_ref()
            .map(|backend| format!("http://127.0.0.1:{}", backend.port))
    }

    async fn shutdown(&self) {
        let mut guard = self.0.lock().await;
        if let Some(mut backend) = guard.take() {
            let _ = backend.child.kill();
        }
    }
}

/// 移除 Windows UNC 路径前缀 (\\?\)，避免某些子进程处理异常
fn normalize_path(path: &Path) -> PathBuf {
    #[cfg(windows)]
    {
        let s = path.to_string_lossy();
        if s.starts_with(r"\\?\") {
            return PathBuf::from(&s[4..]);
        }
    }
    path.to_path_buf()
}

#[tauri::command]
async fn ensure_backend(app: AppHandle, state: State<'_, BackendState>) -> Result<String, String> {
    // 如果已有后端，先检查是否还存活
    if let Some(origin) = state.origin().await {
        if let Ok(resp) = reqwest::get(format!("{}/", origin)).await {
            if resp.status().is_success() {
                return Ok(origin);
            }
        }
        state.shutdown().await;
    }

    let backend_dir = resolve_backend_dir(&app)?;
    let backend_dir = normalize_path(&backend_dir);
    let python = resolve_python(&backend_dir)?;
    let python = normalize_path(&python);
    let port = pick_unused_port().ok_or_else(|| "No free port found".to_string())?;
    let data_dir = resolve_data_dir(&app, &backend_dir)?;
    let data_dir = normalize_path(&data_dir);
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
    // 日志文件由后台线程打开，此处预先创建目录即可
    let _ = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_path)
        .map_err(|e| format!("Failed to create log file: {e}"))?;

    let mut cmd = Command::new(&python);
    cmd.current_dir(&backend_dir);
    cmd.env("MINGDENG_DATA_DIR", &data_dir);
    cmd.env("PYTHONUNBUFFERED", "1");
    cmd.env("PYTHONIOENCODING", "utf-8");
    cmd.args([
        "-u",
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        "127.0.0.1",
        "--port",
        &port.to_string(),
        "--log-level",
        "info",
    ]);
    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());

    // Windows: 隐藏 Python 进程的控制台窗口
    #[cfg(windows)]
    cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW

    let mut child = cmd.spawn().map_err(|e| {
        format!(
            "Failed to start Python backend: {}\nCommand: {:?}\nCWD: {:?}\nDataDir: {:?}",
            e, python, backend_dir, data_dir
        )
    })?;

    // 后台线程读取 stdout/stderr 写入日志，避免 Windows 上文件重定向导致子进程阻塞
    let log_path_stdout = log_path.clone();
    if let Some(stdout) = child.stdout.take() {
        thread::spawn(move || {
            let reader = std::io::BufReader::new(stdout);
            let mut file = match std::fs::OpenOptions::new()
                .create(true)
                .append(true)
                .open(&log_path_stdout)
            {
                Ok(f) => f,
                Err(e) => {
                    eprintln!("[Backend] Failed to open log for stdout: {}", e);
                    return;
                }
            };
            for l in reader.lines().map_while(Result::ok) {
                let _ = writeln!(file, "{}", l);
                let _ = file.flush();
            }
        });
    }
    let log_path_stderr = log_path.clone();
    if let Some(stderr) = child.stderr.take() {
        thread::spawn(move || {
            let reader = std::io::BufReader::new(stderr);
            let mut file = match std::fs::OpenOptions::new()
                .create(true)
                .append(true)
                .open(&log_path_stderr)
            {
                Ok(f) => f,
                Err(e) => {
                    eprintln!("[Backend] Failed to open log for stderr: {}", e);
                    return;
                }
            };
            for l in reader.lines().map_while(Result::ok) {
                let _ = writeln!(file, "{}", l);
                let _ = file.flush();
            }
        });
    }

    // 使用短超时客户端进行健康检查，避免单次请求卡住；禁用系统代理防止干扰本地连接
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(1))
        .no_proxy()
        .build()
        .map_err(|e| e.to_string())?;

    // 轮询健康检查，最多等待 8 秒（后端实际通常 2-3 秒即可启动）
    tokio::time::sleep(Duration::from_millis(500)).await;
    let origin = format!("http://127.0.0.1:{port}");
    for _ in 0..150 {
        tokio::time::sleep(Duration::from_millis(50)).await;

        // 检查子进程是否提前退出
        match child.try_wait() {
            Ok(Some(status)) => {
                // 给后台线程一点时间写入日志
                tokio::time::sleep(Duration::from_millis(500)).await;
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

        // 先进行 TCP 端口探测，确认端口是否真正开放
        if tokio::net::TcpStream::connect(format!("127.0.0.1:{}", port))
            .await
            .is_ok()
        {
            if let Ok(resp) = client.get(format!("{}/", origin)).send().await {
                if resp.status().is_success() {
                    state.set(child, port).await;
                    return Ok(origin);
                }
            }
        }
    }

    // 健康检查失败，读取日志并返回详细信息
    let _ = child.kill();
    // 给后台线程一点时间写入日志
    tokio::time::sleep(Duration::from_millis(800)).await;
    let log_content = std::fs::read_to_string(&log_path).unwrap_or_default();
    let recent_logs = log_content
        .lines()
        .rev()
        .take(20)
        .collect::<Vec<_>>()
        .join("\n");
    let tcp_reachable = tokio::net::TcpStream::connect(format!("127.0.0.1:{}", port))
        .await
        .is_ok();
    Err(format!(
        "Python backend did not respond within 8 seconds.\nPort: {}\nTCP reachable: {}\nLog: {}\nRecent logs:\n{}",
        port,
        tcp_reachable,
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
        let packaged = normalize_path(&resource_dir).join("backend");
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

#[cfg(windows)]
fn verify_python(path: &Path) -> bool {
    if !path.exists() {
        return false;
    }
    let mut cmd = Command::new(path);
    cmd.arg("--version");
    cmd.stdout(Stdio::null());
    cmd.stderr(Stdio::null());
    cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
    cmd.status().map(|s| s.success()).unwrap_or(false)
}

#[cfg(not(windows))]
fn verify_python(path: &Path) -> bool {
    if !path.exists() {
        return false;
    }
    Command::new(path)
        .arg("--version")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

fn resolve_python(backend_dir: &Path) -> Result<PathBuf, String> {
    if let Ok(env_path) = env::var("MINGDENG_PYTHON") {
        let path = PathBuf::from(env_path);
        if verify_python(&path) {
            return Ok(path);
        }
    }

    let mut candidates = Vec::new();
    if let Some(parent) = backend_dir.parent() {
        let parent = normalize_path(parent);
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
        if verify_python(path) {
            return Ok(path.clone());
        }
    }

    // 开发环境回退：检测系统 Python 是否可用
    let default = if cfg!(windows) { "python" } else { "python3" };
    let fallback = PathBuf::from(default);
    if verify_python(&fallback) {
        return Ok(fallback);
    }

    Err(format!(
        "Python executable not found or not working. Checked: {}. Please install Python or ensure backend-venv is bundled.",
        candidates.iter().map(|p| p.display().to_string()).collect::<Vec<_>>().join(", ")
    ))
}

fn resolve_data_dir(app: &AppHandle, backend_dir: &Path) -> Result<PathBuf, String> {
    if let Ok(dir) = app.path().app_data_dir() {
        return Ok(normalize_path(&dir));
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
                tauri::async_runtime::block_on(state.shutdown());
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
