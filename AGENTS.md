# Repository Guidelines

## Project Structure & Module Organization
- backend/: FastAPI app (main.py) with core/ modules for config, todo/plan, library, backup, memory, and AI; stores JSON under data/ (gitignored) and listens on 127.0.0.1:8765.
- src/: static HTML/CSS/JS front end; main.js drives routing/API calls, pages/ holds fragments, style.css layers utility-first styling.
- src-tauri/: Rust wrapper for the desktop shell; tauri.conf.json wires windows. dist/ carries build outputs; run_dev.sh/run_dev.bat start the backend plus a simple web server.

## Build, Test, and Development Commands
- npm install sets up the Tauri CLI; npm run install-deps installs Python requirements in backend/.
- npm run backend (or python -m uvicorn main:app --reload --host 127.0.0.1 --port 8765) starts the API.
- ./run_dev.sh creates a venv, installs deps, starts the backend, and serves src/ on :8000.
- npm run dev launches the Tauri app; npm run build produces the desktop bundle.
- Quick sanity: curl http://127.0.0.1:8765/ and curl http://127.0.0.1:8765/api/today.

## Coding Style & Naming Conventions
- Python: 4-space indents, PEP 8, snake_case, type-hinted pydantic models; reuse managers in core/ and return dicts with success flags.
- JavaScript: 4-space indents with semicolons; camelCase functions, const/let; route new UI through navigateToPage/initializePage and the apiCall wrapper.
- CSS: extend style.css utilities, keep dark-mode classes intact, avoid inline styling.

## Testing Guidelines
- No automated suite yet; follow TESTING.md curl checks (health, /api/config, /api/today, /api/plan/generate) and load http://localhost:8000 for UI smoke tests.
- For desktop, run npm run dev and exercise plan creation, today view, library, and chat; confirm requests hit 127.0.0.1:8765.
- Capture manual steps and sample payloads in PRs; add small scripts under backend/ only when they speed repeatable checks.

## Commit & Pull Request Guidelines
- Keep commits short and imperative, mirroring history (Create LICENSE, Fix bug in #2 & implement feature for #1); reference issue numbers.
- PRs should state what/why, list commands/tests run, include screenshots/GIFs for UI changes, call out data migrations, and update README/QUICKSTART/TESTING/DEVELOPMENT when behavior changes.

## Security & Configuration Tips
- API keys live in data/config.json (masked in responses); keep data/ out of commits and use placeholders in examples.
- Align API_BASE in src/main.js, Tauri config, and docs if the backend host/port changes from 127.0.0.1:8765.
- Backups are handled by core/backup_manager.py; verify restores before pruning old files.
