#!/usr/bin/env bash
set -euo pipefail

# Build MingDeng desktop app with bundled Python backend.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Create/refresh backend virtualenv
if [ ! -d "backend-venv" ]; then
  python3 -m venv backend-venv
fi

# Pick the right pip depending on platform
if [ -x "backend-venv/bin/pip" ]; then
  PIP_BIN="backend-venv/bin/pip"
else
  PIP_BIN="backend-venv/Scripts/pip.exe"
fi

"$PIP_BIN" install -r backend/requirements.txt

# Install JS deps and build the Tauri bundle
npm install
npx tauri build

echo "✅ Desktop bundle ready. Check src-tauri/target/release/bundle/ for installers."
