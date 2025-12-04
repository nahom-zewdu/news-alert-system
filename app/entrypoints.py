# app/entrypoints.py
"""
Entrypoint functions for UV/Hatch console scripts.
Each function simply forwards to the real command.
"""

import uvicorn
import subprocess
import sys
from pathlib import Path


def start_api():
    """Start the FastAPI server (production mode)."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


def dev_api():
    """Start the FastAPI dev server with reload."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


def run_ui():
    """Start Streamlit UI."""
    ui_path = Path(__file__).resolve().parents[1] / "app" / "ui" / "streamlit.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(ui_path)])


def run_scheduler():
    """Run standalone scheduler script."""
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_scheduler.py"
    subprocess.run([sys.executable, str(script)])
