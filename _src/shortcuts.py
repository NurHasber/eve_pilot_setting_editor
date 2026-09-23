"""Create Windows .lnk shortcuts without PowerShell."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def create_shortcut(target: Path, link_path: Path, working_dir: Path | None = None, icon: Path | None = None) -> None:
    target = target.resolve()
    link_path = link_path.resolve()
    work = (working_dir or target.parent).resolve()
    icon_path = (icon or target).resolve()
    link_path.parent.mkdir(parents=True, exist_ok=True)

    # Escape for VBScript string literals
    def esc(p: Path) -> str:
        return str(p).replace("\\", "\\\\").replace('"', '\\"')

    vbs = "\r\n".join(
        [
            'Set oWS = WScript.CreateObject("WScript.Shell")',
            f'sLinkFile = "{esc(link_path)}"',
            "Set oLink = oWS.CreateShortcut(sLinkFile)",
            f'oLink.TargetPath = "{esc(target)}"',
            f'oLink.WorkingDirectory = "{esc(work)}"',
            f'oLink.IconLocation = "{esc(icon_path)},0"',
            'oLink.Description = "EVE Settings Copy"',
            "oLink.Save",
            "",
        ]
    )
    tmp = Path(tempfile.gettempdir()) / "eve_settings_copy_shortcut.vbs"
    tmp.write_text(vbs, encoding="utf-8")
    subprocess.run(["wscript.exe", "//B", str(tmp)], check=False, creationflags=0x08000000)


def ensure_app_shortcuts(installed_exe: Path) -> list[Path]:
    """Create Desktop + Start Menu shortcuts to the fast onedir app."""
    created: list[Path] = []
    desktop = Path.home() / "Desktop"
    start = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    for folder, name in (
        (desktop, "EVE Settings Copy.lnk"),
        (start, "EVE Settings Copy.lnk"),
    ):
        link = folder / name
        try:
            create_shortcut(installed_exe, link)
            if link.is_file():
                created.append(link)
        except Exception:
            pass
    return created
