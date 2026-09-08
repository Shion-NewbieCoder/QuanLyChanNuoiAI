"""Teacher runtime: PyInstaller bundles this program and its Python interpreter.

No subprocess, pip, venv or external Python is used at runtime.
"""
import http.client
import os
from pathlib import Path
import secrets
import socket
import sys
import threading
import time
import webbrowser

HOST, PORT = "127.0.0.1", 8000
LOGIN_URL = f"http://{HOST}:{PORT}/login/?next=/dashboard/"


def message(text):
    print(text, flush=True)


def paths():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS), Path(sys.executable).resolve().parent
    root = Path(__file__).resolve().parents[1]
    return root / "backend", root / "build" / "portable-source-run"


def port_available():
    try:
        with socket.socket() as probe:
            if os.name == "nt":
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            probe.bind((HOST, PORT))
        return True
    except OSError:
        return False


def wait_http(finished, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and not finished.is_set():
        connection = http.client.HTTPConnection(HOST, PORT, timeout=1)
        try:
            connection.request("GET", "/login/")
            response = connection.getresponse()
            response.read()
            if 200 <= response.status < 400 and not finished.is_set():
                return True
        except (OSError, http.client.HTTPException):
            pass
        finally:
            connection.close()
        finished.wait(0.25)
    return False


def run():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    message("[DEMO_BOOTSTRAP] HỆ THỐNG QUẢN LÝ CHĂN NUÔI AI — DEMO")
    if not port_available():
        message("PORT_UNAVAILABLE: Cổng 8000 đang được sử dụng. Đóng demo/server cũ rồi chạy lại.")
        return 1

    resources, distribution = paths()
    data = distribution / "data"
    try:
        data.mkdir(parents=True, exist_ok=True)
        # Fail early with an actionable message for a read-only extracted folder.
        with (data / ".write-check").open("w", encoding="utf-8") as check:
            check.write("")
        (data / ".write-check").unlink()
    except OSError:
        message("DATA_NOT_WRITABLE: Hãy giải nén demo vào thư mục bạn có quyền ghi, rồi chạy lại.")
        return 1

    sys.path.insert(0, str(resources))
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
    os.environ["DJANGO_SECRET_KEY"] = secrets.token_urlsafe(48)
    os.environ["DJANGO_DEBUG"] = "true"
    os.environ["DJANGO_ALLOWED_HOSTS"] = "127.0.0.1,localhost"
    os.environ["DJANGO_DEMO_DB_PATH"] = str(data / "db.sqlite3")
    os.environ["DJANGO_PORTABLE_DEMO"] = "true"
    os.environ.pop("AI_PROVIDER", None)
    os.environ.pop("AI_API_KEY", None)

    import django
    from django.core.management import call_command
    django.setup()
    message("Đang chuẩn bị dữ liệu...")
    call_command("migrate", interactive=False, verbosity=1)
    call_command("seed_demo")
    if not port_available():
        message("PORT_UNAVAILABLE: Đóng demo/server khác đang dùng cổng 8000 rồi thử lại.")
        return 1

    finished = threading.Event()
    def server():
        try:
            call_command("runserver", f"{HOST}:{PORT}", use_reloader=False, verbosity=1)
        except (Exception, SystemExit):
            message("SERVER_START_FAILED: Không thể duy trì server demo. Đóng cửa sổ và thử lại.")
        finally:
            finished.set()

    message("Đang khởi động hệ thống...")
    # The server lives in this executable; closing it cannot leave a child server.
    threading.Thread(target=server, name="django-demo", daemon=True).start()
    if not wait_http(finished):
        message("HTTP_NOT_READY: Trang đăng nhập chưa sẵn sàng sau 30 giây. Hãy chạy lại demo.")
        return 1
    message("[DEMO_READY]")
    message("============================================================")
    message(f"Trang đăng nhập: {LOGIN_URL}")
    message("Quản lý: demo_manager | Kỹ thuật viên: demo_technician | Nhân viên: demo_employee")
    message("Mật khẩu chung: DemoOnly-2026!")
    message("Đóng cửa sổ này hoặc nhấn Ctrl+C để dừng demo.")
    message("============================================================")
    try:
        # Windows default browser, after HTTP success. No hard-coded browser binary.
        if not webbrowser.open(LOGIN_URL):
            message("BROWSER_NOT_OPENED: Mở đường dẫn đăng nhập phía trên trong trình duyệt.")
        else:
            message("[BROWSER_OPENED] Đã gửi trang đăng nhập đến trình duyệt mặc định.")
    except OSError:
        message("BROWSER_NOT_OPENED: Mở đường dẫn đăng nhập phía trên trong trình duyệt.")
    while not finished.wait(0.5):
        pass
    return 1


def main():
    try:
        code = run()
    except KeyboardInterrupt:
        message("\n[DEMO_STOPPED] Đã dừng demo.")
        return 0
    except Exception:
        message("DEMO_START_FAILED: Không thể chuẩn bị demo. Kiểm tra quyền ghi thư mục và giải nén lại đầy đủ bộ portable.")
        code = 1
    if code and sys.stdin is not None and sys.stdin.isatty():
        try:
            input("Nhấn Enter để đóng cửa sổ...")
        except (EOFError, KeyboardInterrupt):
            pass
    return code


if __name__ == "__main__":
    raise SystemExit(main())
