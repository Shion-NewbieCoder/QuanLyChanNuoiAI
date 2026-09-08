"""Developer-only HTTP/process acceptance harness; never bundled into DEMO.exe.

Run with the developer Python after BUILD_DEMO.bat. Opens the default browser
as the real executable does. Only the generated distribution is copied to TEMP.
"""
from html.parser import HTMLParser
import http.cookiejar
import json
import os
from pathlib import Path
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8000"
REPORT = ROOT / "build" / "portable-verification.json"
SLUGS = ("herds", "animals", "animal-groups", "pens", "care", "feed", "medicine",
         "vaccines", "vaccination-records", "growth", "reproduction", "sales")


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        key = "href" if tag in ("link", "use") else "src" if tag in ("img", "script") else None
        if key and attrs.get(key):
            self.urls.add(attrs[key].split("#")[0])


class Browser:
    def __init__(self):
        self.cookies = http.cookiejar.CookieJar()
        self.client = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(self.cookies))
        self.assets = Assets()

    def request(self, path, payload=None, expected=200):
        data = None
        headers = {}
        if payload is not None:
            token = next(c.value for c in self.cookies if c.name == "csrftoken")
            data = urllib.parse.urlencode({**payload, "csrfmiddlewaretoken": token}).encode()
            headers["Referer"] = BASE + path
        request = urllib.request.Request(BASE + path, data=data, headers=headers)
        try:
            response = self.client.open(request, timeout=15)
        except urllib.error.HTTPError as error:
            response = error
        body = response.read().decode("utf-8", errors="replace")
        assert response.status == expected, (path, response.status, body[:150])
        self.assets.feed(body)
        return body, response.url

    def login(self, username):
        body, _ = self.request("/login/")
        assert all(u in body for u in ("demo_manager", "demo_technician", "demo_employee", "DemoOnly-2026!"))
        body, url = self.request("/login/", {"username": username, "password": "DemoOnly-2026!", "next": "/dashboard/"})
        assert url == BASE + "/dashboard/", url
        return body


def snapshot_database(db):
    with sqlite3.connect(db) as connection:
        tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        counts = {table: connection.execute('SELECT COUNT(*) FROM "' + table + '"').fetchone()[0]
                  for table in tables if table not in ("django_session", "sqlite_sequence")}
        users = connection.execute("SELECT username FROM auth_user ORDER BY username").fetchall()
        migrations = connection.execute("SELECT app, name FROM django_migrations ORDER BY app, name").fetchall()
    return {"counts": counts, "users": users, "migrations": migrations}


def start(exe, env, label, command=None, cwd=None):
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    process = subprocess.Popen(command or [str(exe)], cwd=cwd or exe.parent, env=env,
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", creationflags=subprocess.CREATE_NEW_CONSOLE, startupinfo=startup)
    lines = []
    def collect():
        for line in process.stdout:
            lines.append(line)
            (ROOT / "build" / f"portable-{label}.log").write_text("".join(lines), encoding="utf-8")
    threading.Thread(target=collect, daemon=True).start()
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if any("[BROWSER_OPENED]" in line for line in lines):
            assert sum(line.strip() == "[DEMO_READY]" for line in lines) == 1
            return process, lines
        if process.poll() is not None:
            raise AssertionError((label, process.returncode, "".join(lines)))
        time.sleep(.2)
    process.terminate()
    raise AssertionError((label, "readiness/browser timeout", "".join(lines)))


def stop(process, expected_codes=(0,)):
    # A separate test helper attaches to the owned EXE console and sends real Ctrl+C.
    helper = "import ctypes,time; k=ctypes.windll.kernel32; k.FreeConsole(); assert k.AttachConsole(" + str(process.pid) + "); k.SetConsoleCtrlHandler(None,True); assert k.GenerateConsoleCtrlEvent(0,0); time.sleep(1); k.FreeConsole()"
    subprocess.run([sys.executable, "-c", helper], check=True, timeout=10)
    assert process.wait(timeout=15) in expected_codes, process.returncode
    with socket.socket() as probe:
        assert probe.connect_ex(("127.0.0.1", 8000)) != 0, "port still open after shutdown"


def process_evidence(process):
    utf8 = "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); "
    command = utf8 + "Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,ExecutablePath | ConvertTo-Json -Compress"
    records = json.loads(subprocess.check_output(["powershell.exe", "-NoProfile", "-Command", command], text=True, encoding="utf-8-sig"))
    ids = {process.pid}
    while True:
        children = {p["ProcessId"] for p in records if p["ParentProcessId"] in ids}
        expanded = ids | children
        if expanded == ids:
            break
        ids = expanded
    tree = [p for p in records if p["ProcessId"] in ids]
    assert not any(p["Name"].lower() in ("python.exe", "pythonw.exe", "py.exe", "pip.exe", "node.exe") for p in tree), tree
    command = utf8 + f"(Get-Process -Id {process.pid}).Modules | Where-Object ModuleName -Like 'python*.dll' | Select-Object ModuleName,FileName | ConvertTo-Json -Compress"
    modules = json.loads(subprocess.check_output(["powershell.exe", "-NoProfile", "-Command", command], text=True, encoding="utf-8-sig"))
    if isinstance(modules, dict):
        modules = [modules]
    assert modules and all("_internal" in m["FileName"] for m in modules), modules
    return {"tree": tree, "python_runtime_modules": modules}


def main():
    result = {"status": "RUNNING", "offline_method": "Unreachable HTTP(S)/ALL proxies in child environment; loopback-only HTTP/asset checks. Network adapter remains connected."}
    process = None
    try:
        outside = Path(tempfile.mkdtemp(prefix="Nhóm 08 Demo ")) / "DEMO_PORTABLE"
        shutil.copytree(ROOT / "DEMO_PORTABLE", outside)
        exe = outside / "DEMO.exe"
        db = outside / "data" / "db.sqlite3"
        assert not db.exists(), "Release must not contain a database before first run"
        forbidden = [str(p.relative_to(outside)) for p in outside.rglob("*") if p.name in (".venv", "node_modules", "__pycache__", ".env", "debug.log") or p.suffix in (".pyc", ".pyo")]
        assert not forbidden, forbidden
        env = os.environ.copy()
        for key in ("PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV", "AI_PROVIDER", "AI_API_KEY", "DJANGO_SECRET_KEY"):
            env.pop(key, None)
        env.update(PATH=str(Path(os.environ["SystemRoot"]) / "System32"), HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", ALL_PROXY="http://127.0.0.1:9", NO_PROXY="localhost,127.0.0.1")
        result.update(test_directory=str(outside), runtime_path=env["PATH"], forbidden_artifacts=forbidden)
        process, lines = start(exe, env, "first")
        result["process_evidence"] = process_evidence(process)
        assert db.is_file()
        initial = snapshot_database(db)
        result["first_database"] = initial
        assert initial["users"] == [("demo_employee",), ("demo_manager",), ("demo_technician",)]
        manager = Browser()
        manager.login("demo_manager")
        for slug in SLUGS:
            body, _ = manager.request(f"/{slug}/")
            assert f'/{slug}/create/' in body
            manager.request(f"/{slug}/create/")
            records = re.findall(r'href="(/' + re.escape(slug) + r'/\d+/)"', body)
            assert records, (slug, "no seeded records")
            manager.request(records[0])
            manager.request(records[0] + "edit/")
            manager.request(records[0] + "delete/")
        manager.request("/statistics/")
        ai, _ = manager.request("/ai/")
        assert "chưa" in ai.lower() and "cấu hình" in ai.lower()
        ai, _ = manager.request("/ai/", {"feature": "herd_summary", "herd_summary-target_id": "1"})
        assert "AI hiện chưa được cấu hình" in ai
        payload = dict(code="PORTABLE-CHECK", name="Đàn kiểm thử độc lập", animal_type="bò", management_mode="group", quantity="2", status="active", avatar="cow")
        _, detail = manager.request("/herds/create/", payload)
        assert re.search(r'/herds/\d+/$', detail), detail
        detail = detail.removeprefix(BASE)
        payload["name"] = "Đã sửa, giữ qua lần chạy lại"
        manager.request(detail + "edit/", payload)
        assert payload["name"] in manager.request(detail)[0]
        result["template_routes"] = "login/dashboard; all 12 resource list/create/detail/edit/delete; statistics; AI GET+POST; 403"
        roles = {}
        for role in ("technician", "employee"):
            client = Browser()
            client.login("demo_" + role)
            for path, allowed in (("/herds/", True), ("/herds/create/", False), ("/growth/create/", role == "technician"), ("/care/create/", True)):
                body, _ = client.request(path, expected=200 if allowed else 403)
                if path == "/herds/":
                    assert "/herds/create/" not in body
            client.request("/herds/create/", payload, expected=403)
            body, _ = client.request("/growth/")
            assert ("/growth/create/" in body) == (role == "technician")
            roles[role] = "login; hidden unauthorized controls; direct forbidden GET/POST 403; allowed care form"
            manager.assets.urls.update(client.assets.urls)
        result["roles"] = {"manager": "12 create/edit/delete controls and herd CRUD", **roles}
        assets = sorted(url for url in manager.assets.urls if url)
        assert assets and all(url.startswith("/static/") for url in assets), assets
        for url in assets:
            manager.request(url)
        result["assets"] = assets
        conflict = subprocess.run([str(exe)], cwd=outside, env=env, input="\n", capture_output=True, text=True, encoding="utf-8", timeout=15)
        assert conflict.returncode == 1 and "PORT_UNAVAILABLE" in conflict.stdout
        manager.request("/dashboard/")
        result["port_conflict"] = "PASS: second EXE refused, original server remained healthy"
        before = snapshot_database(db)
        stop(process)
        process = None
        result["first_run"] = "PASS"
        process, lines = start(exe, env, "second")
        assert "No migrations to apply" in "".join(lines)
        after = snapshot_database(db)
        assert before == after, "non-session counts/users/migration history changed"
        manager = Browser()
        manager.login("demo_manager")
        assert payload["name"] in manager.request(detail)[0]
        manager.request(detail + "delete/")
        manager.request(detail + "delete/", {})
        manager.request(detail, expected=404)
        assert snapshot_database(db) == initial, "CRUD cleanup did not restore initial counts"
        result["second_run"] = "PASS: unchanged counts, migrations, users; added/edited data persisted; delete successful"
        result["crud"] = "PASS: create/read/edit/persist/restart/delete via CSRF-protected HTTP forms"
        stop(process)
        process = None
        result["shutdown"] = "PASS: actual Ctrl+C exits code 0 and releases port on both runs"
        configuration = json.loads((ROOT / ".vscode/launch.json").read_text(encoding="utf-8"))["configurations"][0]
        assert configuration["type"] == "node-terminal" and configuration["cwd"] == "${workspaceFolder}"
        process, lines = start(exe, env, "f5-command", command=configuration["command"], cwd=outside.parent)
        Browser().login("demo_manager")
        stop(process, expected_codes=(0, 1, -1073741510, 3221225786))
        process = None
        assert any("[DEMO_STOPPED]" in line for line in lines)
        result["f5_command"] = "PASS: exact launch.json command in copied parent with no Python on PATH; login/browser/shutdown. Actual VS Code F5 keypress not automated."
        result["status"] = "PASS"
    except Exception as error:
        result["status"] = "FAIL"
        result["error"] = repr(error)
        raise
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        REPORT.parent.mkdir(exist_ok=True)
        REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
