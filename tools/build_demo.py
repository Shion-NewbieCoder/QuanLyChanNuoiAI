"""Developer-only build helper. Never shipped as the teacher runtime."""
import shutil
import subprocess
import sys
from pathlib import Path

import run_demo

ROOT = Path(__file__).resolve().parents[1]


def remove_generated(path, boundary):
    path = path.resolve()
    boundary = boundary.resolve()
    if path == boundary or not path.is_relative_to(boundary):
        raise RuntimeError("Refusing to remove a path outside the generated build directory")
    if path.exists():
        shutil.rmtree(path)


def main():
    if run_demo.ensure_supported_python() or run_demo.ensure_virtual_environment() or run_demo.ensure_dependencies():
        return 1
    python = str(run_demo.VENV_PYTHON)
    subprocess.run([python, "-m", "pip", "install", "-r", str(ROOT / "packaging/requirements-build.txt")], check=True)
    for asset in ("bootstrap.min.css", "bootstrap.bundle.min.js", "LICENSE"):
        if not (ROOT / "backend/static/vendor/bootstrap" / asset).is_file():
            raise RuntimeError("Missing vendored Bootstrap asset: " + asset)
    build = ROOT / "build"
    stage = build / "portable-stage"
    work = build / "pyinstaller"
    remove_generated(stage, build)
    remove_generated(work, build)
    subprocess.run([python, "-m", "PyInstaller", "--noconfirm", "--clean", "--distpath", str(stage),
                    "--workpath", str(work), str(ROOT / "packaging/DEMO.spec")], cwd=ROOT, check=True)
    source = stage / "DEMO_PORTABLE"
    destination = ROOT / "DEMO_PORTABLE"
    destination.mkdir(exist_ok=True)
    # A rebuild replaces generated runtime files only, preserving portable user data.
    remove_generated(destination / "_internal", destination)
    shutil.copytree(source / "_internal", destination / "_internal")
    shutil.copy2(source / "DEMO.exe", destination / "DEMO.exe")
    shutil.copy2(ROOT / "packaging/README_DEMO.txt", destination / "README_DEMO.txt")
    (destination / "data").mkdir(exist_ok=True)
    print(f"BUILD_COMPLETE: {destination / 'DEMO.exe'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
