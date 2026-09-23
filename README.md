# EVE Settings Copy

A small Windows tool for copying EVE Online client layout/settings from one account/character to all others.

This project is an improved take on [CopyEveLayoutTool](https://github.com/kshannoninnes/CopyEveLayoutTool): same core idea (overwrite other `core_user_*.dat` / `core_char_*.dat` files with your master files), but with less manual work — it **remembers your master pilot files** between launches and can **create dated backups in one click**.

Copyright © HesBi. **All Rights Reserved.** See [LICENSE](LICENSE) and [GitHub’s guidance on projects with no open-source license](https://choosealicense.com/no-permission/).

## What it does

EVE stores UI/settings per account and character in:

`%LOCALAPPDATA%\CCP\EVE\d_eve_tq_tranquility\settings_Default`

- `core_user_<accountId>.dat` — account settings  
- `core_char_<characterId>.dat` — character settings  

The app:

1. **Finds** that settings folder for the current Windows user automatically.
2. Lets you pick **master** `core_user_*.dat` and/or `core_char_*.dat` (the pilot whose layout you want everywhere).
3. **Remembers** those masters in `%LOCALAPPDATA%\EveSettingsCopy\config.json`.
4. **Copy to all others** — copies master file contents onto every other matching `core_user_*.dat` / `core_char_*.dat`, keeping each target’s filename (so account/character IDs stay correct).
5. **Backup masters** — creates a dated folder inside the EVE `settings_Default` path  
   (e.g. `...\settings_Default\backup_YYYY-MM-DD_HH-MM-SS\`) and copies the selected master files there.

Close EVE before copying. Always keep a backup if you care about existing alt layouts.

## Compared to CopyEveLayoutTool

| | CopyEveLayoutTool | EVE Settings Copy |
|---|---|---|
| Master files | Select each session | Saved and restored automatically |
| Targets | Manually add “slaves” | All other valid `core_*` files in the folder |
| Backups | Manual | One-click dated folder inside `settings_Default` |
| UI | Classic tool window | EVE-inspired dark UI |

## Run (Windows)

**Daily use:** open the Desktop shortcut **EVE Settings Copy** (created on first run). That launches the installed app under `%LOCALAPPDATA%\EveSettingsCopy\app\` — near-instant, no splash, window opens centered.

**First install / update:**

1. Download the latest `EveSettingsCopy_vX.Y.Z.exe` from this repo.
2. Run it once. It unpacks/installs into LocalAppData and refreshes the Desktop + Start Menu shortcuts.
3. Prefer the shortcut afterward; the versioned `.exe` is only a bootstrapper.

The versioned file is a ~40MB one-file bootstrap. Windows must unpack it before Python can start — a short splash appears **only during that unpack**. The installed onedir app itself has **no** loading animation.

Only the **latest** `EveSettingsCopy_v*.exe` is kept in the repo.

## Build from source

```text
Python 3.11+ recommended
pip install pyinstaller pillow
cd _src
python tools\build_release.py
```

This builds an onedir app, zips it as payload, and produces `EveSettingsCopy_vX.Y.Z.exe` in the project root. It also installs into LocalAppData and refreshes shortcuts for local testing.

## Project layout

```text
_src/
  app.py           # installed app entry (no splash)
  launcher.py      # versioned bootstrap exe (PyInstaller splash on unpack)
  shortcuts.py     # Desktop / Start Menu .lnk helpers
  single_instance.py
  tools/build_release.py
  core/            # path discovery, copy, backup, config
  ui/              # window, tabs, theme, widgets
  assets/icons/    # logo, app icon, bootloader splash image
```

## Credits

- Inspired by [CopyEveLayoutTool](https://github.com/kshannoninnes/CopyEveLayoutTool) by kshannoninnes  
- Vibe-coded in Cursor by pilot **HesBi**  

Flag save capsulir!
