"""Developer-only release inventory and frozen archive path/artifact checks."""
import hashlib
import json
import marshal
from pathlib import Path
import re
import zipfile

from PyInstaller.archive.readers import CArchiveReader

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "DEMO_PORTABLE"
exe = RELEASE / "DEMO.exe"
files = [p for p in RELEASE.rglob("*") if p.is_file()]
path_patterns = (b"F:\\", b"C:\\Users\\Admin\\", b"QuanLyChanNuoiGiaSucAI\\.venv")
path_hits = []
secret_hits = []
forbidden = []


def inspect(name, data):
    if any(pattern in data or pattern.decode().encode("utf-16-le") in data for pattern in path_patterns):
        path_hits.append(name)
    # Known credential formats and private-key headers, not demo-only passwords.
    if re.search(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{32,}|\bAKIA[0-9A-Z]{16}\b", data):
        secret_hits.append(name)


for path in files:
    name = str(path.relative_to(RELEASE))
    if path.suffix in (".pyc", ".pyo", ".sqlite3", ".log") or any(part in (".venv", "node_modules", "__pycache__", ".git", ".env", "tests") for part in path.relative_to(RELEASE).parts):
        forbidden.append(name)
    inspect(name, path.read_bytes())
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            for member in archive.namelist():
                inspect(name + ":" + member, archive.read(member))

archive = CArchiveReader(str(exe))
for name in archive.toc:
    inspect("EXE:" + name, archive.extract(name))
pyz = archive.open_embedded_archive("PYZ.pyz")
project_modules = []
project_test_modules = []
for name in pyz.toc:
    code = pyz.extract(name)
    inspect("PYZ:" + name, marshal.dumps(code))
    if name.startswith(("apps.", "config.")):
        project_modules.append(name)
        if any(part.startswith("test") for part in name.split(".")):
            project_test_modules.append(name)

result = {
    "exe_bytes": exe.stat().st_size,
    "total_bytes": sum(p.stat().st_size for p in files),
    "file_count": len(files),
    "exe_sha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
    "absolute_path_hits": path_hits,
    "credential_pattern_hits": secret_hits,
    "forbidden_files": forbidden,
    "project_test_modules": project_test_modules,
    "project_modules": project_modules,
    "note": "base_library.zip contains bundled Python bytecode by design; no loose pyc/cache directories. Pattern scans cannot prove absence of every possible secret.",
}
(ROOT / "build/release-inventory.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({key: value for key, value in result.items() if key != "project_modules"}, indent=2))
assert not (path_hits or secret_hits or forbidden or project_test_modules), "Review release inventory findings"
