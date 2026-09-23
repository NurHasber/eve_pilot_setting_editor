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
5. **Backup masters** — copies the selected master files into a unique folder  
   `%LOCALAPPDATA%\EveSettingsCopy\Backups\backup_YYYY-MM-DD_HH-MM-SS\`.

Close EVE before copying. Always keep a backup if you care about existing alt layouts.

## Compared to CopyEveLayoutTool

| | CopyEveLayoutTool | EVE Settings Copy |
|---|---|---|
| Master files | Select each session | Saved and restored automatically |
| Targets | Manually add “slaves” | All other valid `core_*` files in the folder |
| Backups | Manual | One-click dated backup of masters |
| UI | Classic tool window | EVE-inspired dark UI |

## Run (Windows)

1. Download `EveSettingsCopy_vX.Y.Z.exe` from the repository root.
2. Run it once — it **installs** the real app into  
   `%LOCALAPPDATA%\EveSettingsCopy\app\` (only when missing or when the version changes).
3. It then starts the installed app. Later launches of the **installed** app are instant (no full unpack).

For the fastest daily use, start:

`%LOCALAPPDATA%\EveSettingsCopy\app\EveSettingsCopy.exe`

(or pin that file to the taskbar). The versioned GitHub `.exe` is a bootstrapper; classic PyInstaller one-file mode cannot skip unpacking itself on every double-click.

Only the **latest** `EveSettingsCopy_v*.exe` is kept in the repo.

**Requirements:** Windows 10/11.

## Build from source

```text
Python 3.11+ recommended
pip install pyinstaller pillow
cd _src
python tools\build_release.py
```

This builds an onedir app, zips it as payload, and produces `EveSettingsCopy_vX.Y.Z.exe` in the project root.

## Project layout

```text
_src/
  app.py           # installed app entry
  launcher.py      # versioned bootstrap exe entry
  tools/build_release.py
  core/            # path discovery, copy, backup, config
  ui/              # window, tabs, theme, widgets
  assets/icons/    # logo and app icon
```

## Credits

- Inspired by [CopyEveLayoutTool](https://github.com/kshannoninnes/CopyEveLayoutTool) by kshannoninnes  
- Vibe-coded in Cursor by pilot **HesBi**  

Flag save capsulir!
