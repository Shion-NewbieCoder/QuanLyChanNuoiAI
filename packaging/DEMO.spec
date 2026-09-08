# Reproducible Windows onedir build. Run through BUILD_DEMO.bat.
from pathlib import Path
from importlib.metadata import distribution
import os
import secrets
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

root = Path(SPECPATH).parent
backend = root / "backend"
sys.path.insert(0, str(backend))
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
os.environ["DJANGO_SECRET_KEY"] = secrets.token_urlsafe(48)

def runtime_module(name):
    return not any(part == "tests" or part.startswith("test_") or part.startswith("tests_") for part in name.split("."))

hidden = collect_submodules("apps", filter=runtime_module)
hidden += collect_submodules("config", filter=runtime_module)
hidden += collect_submodules("rest_framework", filter=runtime_module)
hidden += ["django.db.backends.sqlite3", "django.forms.renderers", "django.template.loaders.app_directories"]
datas = [(str(backend / "templates"), "templates"), (str(backend / "static"), "static")]
datas += collect_data_files("rest_framework")
# Redistribute the licenses belonging to the runtime and its dependencies.
datas.append((str(Path(sys.base_prefix) / "LICENSE.txt"), "licenses/Python"))
for package in ("Django", "djangorestframework", "asgiref", "sqlparse", "tzdata", "PyInstaller"):
    metadata = distribution(package)
    for file in metadata.files or []:
        if Path(file).name.upper().startswith(("LICENSE", "COPYING", "NOTICE")):
            datas.append((str(metadata.locate_file(file)), f"licenses/{package}"))
for app in (backend / "apps").iterdir():
    if app.is_dir() and (app / "templates").is_dir():
        datas.append((str(app / "templates"), f"apps/{app.name}/templates"))
# Physical migration/command source enables Django/pkgutil discovery in frozen mode.
for folder in (backend / "apps").rglob("*"):
    if folder.is_dir() and folder.name in ("migrations", "commands"):
        for source in folder.glob("*.py"):
            datas.append((str(source), str(source.parent.relative_to(backend))))

a = Analysis([str(root / "tools" / "portable_demo.py")], pathex=[str(backend)],
             binaries=[], datas=datas, hiddenimports=hidden,
             hookspath=[str(root / "packaging" / "hooks")],
             excludes=["pytest", "pip", "IPython", "tkinter"], noarchive=False)
# Never ship development DBs, secrets, loose bytecode or test artifacts.
a.datas = [item for item in a.datas if not (
    item[0].endswith((".sqlite3", ".pyc", ".pyo", ".log"))
    or any(part in (".env", "__pycache__", "tests") for part in Path(item[0]).parts)
)]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="DEMO", debug=False,
          bootloader_ignore_signals=False, strip=False, upx=False, console=True,
          contents_directory="_internal")
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="DEMO_PORTABLE")
