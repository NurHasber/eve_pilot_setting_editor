"""Build versioned release: onedir app + onefile launcher with payload.zip."""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
PROJ = SRC.parent
sys.path.insert(0, str(SRC))
from core.logic import APP_VERSION  # noqa: E402

APP_INTERNAL_NAME = "EveSettingsCopy"
LAUNCHER_NAME = f"EveSettingsCopy_v{APP_VERSION}"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(SRC))


def main() -> None:
    work = SRC / "build_release"
    dist = work / "dist"
    if work.exists():
        shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)

    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onedir",
            "--windowed",
            f"--name={APP_INTERNAL_NAME}",
            f"--icon={SRC / 'assets' / 'icons' / 'app.ico'}",
            f"--add-data={SRC / 'assets'};assets",
            "--hidden-import=PIL",
            "--hidden-import=PIL.Image",
            "--hidden-import=PIL.ImageDraw",
            "--collect-submodules=ui",
            "--collect-submodules=core",
            f"--distpath={dist}",
            f"--workpath={work / 'work_app'}",
            f"--specpath={work}",
            str(SRC / "app.py"),
        ]
    )

    app_dir = dist / APP_INTERNAL_NAME
    payload = work / "payload.zip"
    with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in app_dir.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(app_dir).as_posix())
    print("payload", payload, payload.stat().st_size)

    payload_copy = SRC / "payload.zip"
    shutil.copy2(payload, payload_copy)

    # Sync launcher version constant from core
    launcher_src = SRC / "launcher.py"
    text = launcher_src.read_text(encoding="utf-8")
    import re

    text2, n = re.subn(
        r'APP_VERSION = "[^"]*"',
        f'APP_VERSION = "{APP_VERSION}"',
        text,
        count=1,
    )
    if n != 1:
        raise RuntimeError("Failed to sync APP_VERSION in launcher.py")
    launcher_src.write_text(text2, encoding="utf-8")

    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onefile",
            "--windowed",
            f"--name={LAUNCHER_NAME}",
            f"--icon={SRC / 'assets' / 'icons' / 'app.ico'}",
            f"--add-data={payload_copy};.",
            f"--distpath={PROJ}",
            f"--workpath={work / 'work_launcher'}",
            f"--specpath={work}",
            str(SRC / "launcher.py"),
        ]
    )

    payload_copy.unlink(missing_ok=True)

    for old in PROJ.glob("EveSettingsCopy_v*.exe"):
        if old.name != f"{LAUNCHER_NAME}.exe":
            print("remove old", old.name)
            old.unlink()

    # Also install app onedir into LocalAppData now for instant local runs
    local_app = Path.home() / "AppData" / "Local" / "EveSettingsCopy" / "app"
    if local_app.exists():
        shutil.rmtree(local_app, ignore_errors=True)
    shutil.copytree(app_dir, local_app)
    (local_app / "version.txt").write_text(APP_VERSION + "\n", encoding="utf-8")

    out = PROJ / f"{LAUNCHER_NAME}.exe"
    print("RELEASE:", out, out.stat().st_size)
    print("INSTALLED:", local_app)


if __name__ == "__main__":
    main()
