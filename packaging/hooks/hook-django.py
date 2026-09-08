"""Collect the Django runtime without the stock hook's development DB copying."""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

def runtime_module(name):
    parts = name.split(".")
    return not (
        any(part == "tests" or part.startswith("test_") for part in parts)
        or name.startswith(("django.contrib.gis", "django.contrib.postgres", "django.db.backends.mysql",
                            "django.db.backends.oracle", "django.db.backends.postgresql"))
    )

hiddenimports = collect_submodules("django", filter=runtime_module, on_error="ignore")
datas = collect_data_files("django", excludes=["**/test*", "**/__pycache__/**"])
