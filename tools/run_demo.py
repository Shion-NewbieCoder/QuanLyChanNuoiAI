#!/usr/bin/env python3
"""Bootstrap and run the local academic demo without machine-specific paths."""

import argparse
import hashlib
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
REQUIREMENTS_FILE = BACKEND_DIR / "requirements.txt"
VENV_DIR = PROJECT_ROOT / ".venv"
VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
DEPENDENCY_MARKER = VENV_DIR / ".requirements.sha256"
HOST = "127.0.0.1"
PORT = 8000
DASHBOARD_URL = f"http://{HOST}:{PORT}/dashboard/"


def message(text=""):
    print(text, flush=True)


def fail(code, detail, next_action):
    message(f"[{code}] {detail}")
    message(f"Next action: {next_action}")
    return 1


def run_stage(stage, command, environment=None):
    message(f"[DEMO] {stage}...")
    try:
        result = subprocess.run(
            [str(part) for part in command],
            cwd=str(BACKEND_DIR),
            env=environment,
            check=False,
        )
    except OSError as exc:
        message(f"[{stage.upper().replace(' ', '_')}_FAILED] Could not start the command: {exc}")
        return False
    return result.returncode == 0


def port_is_in_use():
    try:
        with socket.create_connection((HOST, PORT), timeout=0.4):
            return True
    except OSError:
        return False


def ensure_supported_python():
    if sys.version_info.major != 3 or sys.version_info < (3, 9):
        return fail(
            "PYTHON_UNSUPPORTED",
            "Python 3.9 or newer is required.",
            "Install a supported Python 3 release and run the demo again.",
        )
    return 0


def ensure_virtual_environment():
    if VENV_PYTHON.is_file():
        message("[DEMO] Reusing project-local .venv.")
        return 0

    if VENV_DIR.exists():
        return fail(
            "VENV_CREATE_FAILED",
            ".venv exists but its Windows Python executable is missing.",
            "Move the incomplete .venv aside and run the demo again.",
        )

    message("[DEMO] Creating project-local .venv...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            cwd=str(PROJECT_ROOT),
            check=False,
        )
    except OSError as exc:
        return fail(
            "VENV_CREATE_FAILED",
            f"The virtual environment command could not start: {exc}",
            "Check that the installed Python includes the venv module.",
        )

    if result.returncode != 0 or not VENV_PYTHON.is_file():
        return fail(
            "VENV_CREATE_FAILED",
            "Python could not create .venv.",
            "Check the Python installation and write access to the project folder.",
        )
    return 0


def requirements_digest():
    return hashlib.sha256(REQUIREMENTS_FILE.read_bytes()).hexdigest()


def dependencies_importable():
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", "import django, rest_framework"],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def ensure_dependencies():
    digest = requirements_digest()
    marker_matches = (
        DEPENDENCY_MARKER.is_file()
        and DEPENDENCY_MARKER.read_text(encoding="utf-8").strip() == digest
    )
    if marker_matches and dependencies_importable():
        message("[DEMO] Dependencies are current; installation skipped.")
        return 0

    message("[DEMO] Installing backend requirements...")
    try:
        result = subprocess.run(
            [
                str(VENV_PYTHON),
                "-m",
                "pip",
                "install",
                "-r",
                str(REQUIREMENTS_FILE),
            ],
            cwd=str(PROJECT_ROOT),
            check=False,
        )
    except OSError as exc:
        return fail(
            "PIP_INSTALL_FAILED",
            f"pip could not start: {exc}",
            "Check the Python installation and network connection, then retry.",
        )

    if result.returncode != 0:
        return fail(
            "PIP_INSTALL_FAILED",
            "Backend requirements were not installed.",
            "Review the pip output above, check network access, and run the demo again.",
        )

    DEPENDENCY_MARKER.write_text(digest + "\n", encoding="utf-8")
    return 0


def local_demo_environment():
    environment = os.environ.copy()
    environment["DJANGO_SECRET_KEY"] = secrets.token_urlsafe(48)
    environment["DJANGO_DEBUG"] = "true"
    environment["DJANGO_ALLOWED_HOSTS"] = "127.0.0.1,localhost"
    return environment


def prepare_database(environment):
    if not run_stage(
        "Applying database migrations",
        [VENV_PYTHON, "manage.py", "migrate", "--noinput"],
        environment,
    ):
        return fail(
            "MIGRATION_FAILED",
            "Django migrations did not complete.",
            "Review the migration output above and correct the reported local setup issue.",
        )

    if not run_stage(
        "Creating or restoring demo data",
        [VENV_PYTHON, "manage.py", "seed_demo"],
        environment,
    ):
        return fail(
            "SEED_FAILED",
            "The deterministic demo dataset was not prepared.",
            "Review the seed output above; confirm the local demo uses DEBUG=true.",
        )
    return 0


def wait_for_server(process, timeout_seconds=20):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        if port_is_in_use():
            return True
        time.sleep(0.2)
    return False


def run_server(environment):
    message("[DEMO] Starting Django server...")
    try:
        process = subprocess.Popen(
            [str(VENV_PYTHON), "manage.py", "runserver", f"{HOST}:{PORT}"],
            cwd=str(BACKEND_DIR),
            env=environment,
        )
    except OSError as exc:
        return fail(
            "SERVER_START_FAILED",
            f"Django runserver could not start: {exc}",
            "Review the error and run the demo again.",
        )

    if not wait_for_server(process):
        if process.poll() is None:
            process.terminate()
        return fail(
            "SERVER_START_FAILED",
            "Django did not become ready on port 8000 within 20 seconds.",
            "Review the server output above and ensure port 8000 is available.",
        )

    message(f"[DEMO_READY] {DASHBOARD_URL}")
    message("============================================================")
    message(" LIVESTOCK MANAGEMENT AI - LOCAL DEMO")
    message("============================================================")
    message(f"Dashboard: {DASHBOARD_URL}")
    message("Demo account:")
    message("Username: demo_manager")
    message("Password: DemoOnly-2026!")
    message("Press Ctrl+C to stop the server.")
    message("============================================================")

    try:
        return_code = process.wait()
    except KeyboardInterrupt:
        message("\n[DEMO] Server stopped.")
        return 0

    if return_code != 0:
        return fail(
            "SERVER_START_FAILED",
            f"Django server exited with code {return_code}.",
            "Review the server output above and run the demo again.",
        )
    return 0


def parse_arguments():
    parser = argparse.ArgumentParser(description="Prepare and run the local livestock demo.")
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Create/reuse the environment, migrate, and seed without starting the server.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    message("[DEMO_BOOTSTRAP] Preparing Livestock Management local demo.")

    if ensure_supported_python() != 0:
        return 1
    if port_is_in_use() and not args.setup_only:
        return fail(
            "PORT_UNAVAILABLE",
            "Port 8000 is already in use; no process was stopped.",
            "Close the existing local server/process using port 8000, then press F5 again.",
        )
    if ensure_virtual_environment() != 0:
        return 1
    if ensure_dependencies() != 0:
        return 1

    environment = local_demo_environment()
    if prepare_database(environment) != 0:
        return 1

    if args.setup_only:
        message("[DEMO_SETUP_READY] Environment, migrations, and demo data are ready.")
        return 0
    return run_server(environment)


if __name__ == "__main__":
    raise SystemExit(main())
