---
name: loupedeck-claude-code
description: Sets up a Loupedeck CT as a control deck for Claude Code (slash-command tiles, terminal tab switching, dials, pixel-art icons, and a tamagotchi mascot on the big wheel that reacts to Claude Code hooks). Use after plugging a Loupedeck CT into a new Windows or macOS machine, or to change the button map, prompts or caption language, or to repair the setup.
---

# Loupedeck CT → Claude Code

Goal: on this machine the Loupedeck CT gets a "Claude Code" profile (default profile and terminal profile),
the ClaudeMascot wheel plugin, and optional Claude Code hooks that drive the mascot. Everything is
idempotent, so the skill can run again at any time. All paths below are relative to this skill's folder.

Read `docs/loupedeck-format.md` before touching profile or plugin code: it records how the undocumented
format works and the traps that already cost hours.

## 0. Recon (always first)

1. OS: `$env:OS` (Windows_NT) or `uname -s` (Darwin).
2. Loupedeck software (Logi Plugin Service 6.x) installed and running:
   - Windows: `Get-Process LogiPluginService`; data in `%LOCALAPPDATA%\Logi\LogiPluginService\`.
   - macOS: `pgrep -il LogiPluginService`; data probably in `~/Library/Application Support/Logi/LogiPluginService/`. Verify, then fix this line.
   - Missing → stop and tell the user to install it from logitech.com / loupedeck.com.
3. Device: Windows `Get-PnpDevice -FriendlyName "*Loupedeck*"`, macOS `system_profiler SPUSBDataType | grep -i loupedeck`.
   The CT is `Loupedeck20`. Check `LastSeenDevice` in `LoupedeckSettings.ini`.
4. Terminal running Claude Code: walk the parent processes of this shell (Windows Terminal, iTerm2, Ghostty…),
   and check whether Claude runs natively or inside WSL. Do not guess.
5. Tooling: `python` + Pillow (`pip install pillow`) and the .NET SDK matching the host. Logi Plugin Service 6.4
   runs on **.NET 10** (`System.Runtime.dll` 10.x in its folder), so `dotnet --list-sdks` must show a 10.x SDK.
   If something is missing, ask the user before installing it (e.g. `winget install Microsoft.DotNet.SDK.10`).

## 1. Language and config

`~/.config/loupedeck-cc/config.json` holds `{"lang": "en" | "de" | "pl"}`. If it does not exist, ask the
user once which language they want for tile captions (Claude Code commands keep their English names
in every language) and write the file.
If `~/.config/loupedeck-cc/prompts.txt` does not exist, copy `docs/prompts.<lang>.txt` there.
Format: `Label | prompt text | icon`, at most 10 lines.

## 2. Terminal shortcuts

The profile only sends keys, so the terminal needs stable shortcuts:

- **Windows Terminal**: `ctrl+alt+1..8` → `switchToTab` index 0..7 are WT defaults; do not add them. Add
  `nextTab` / `prevTab` with `"tabSwitcherMode": "disabled"` on `ctrl+alt+right` / `ctrl+alt+left`.
  WT 1.24+ keeps commands in `actions` (with an `id`) and keys in `keybindings`. Back up `settings.json` first.
- **iTerm2 / Ghostty**: `⌘1..8` and `⌘⇧[` / `⌘⇧]` work out of the box.
- **tmux** (e.g. Claude inside WSL): the generator has no tmux branch yet. Add one (`M-1..8` → `select-window`)
  if the user lives in tmux.

## 3. Build and install

```
C=~/.config/loupedeck-cc
python build_plugin.py --out $C/build-plugin                                   # plugin + wheel frames
python gen_profile.py --os win --out $C/build-win --prompts $C/prompts.txt --wheel-plugin
python gen_profile.py --os win --out $C/build-win --prompts $C/prompts.txt --wheel-plugin --target default
powershell -File install_win.ps1 -Build $C/build-win -Plugin $C/build-plugin/ClaudeMascot -MakeDefault
```

- `--target default` puts the same profile on the system default app (`@_defaultwin`, mode `System`), and
  `-MakeDefault` sets it as the CT default. App-specific profiles (Photoshop…) still switch in. The previous
  default profile stays in place, and the user can select it in the Loupedeck app.
- The installer backs up to `~/.config/loupedeck-cc/backup-*`, stops the service, swaps files and restarts it.
- Before overwriting an installed profile, check that the user has not edited it in the Loupedeck app since
  the last install (`lastModifiedTimeUtc` / file time). If they have, ask first.

## 4. Claude Code hooks (optional, ask first)

`python hooks/install_hooks.py` adds 15 **async**, shell-free hooks to `~/.claude/settings.json`
(backup taken, existing settings merged, `--remove` to undo). Each event runs `hooks/mascot_hook.py`, which
writes `~/.config/loupedeck-cc/sessions/<session>.json`. The plugin reads those files about once a second.
It shows work, attention (with wheel vibration), oops, compact, done and hello, and draws one dot per busy
session. To confirm the hooks fire: make any tool call and check that a file for this session appears.

## 5. Verify with the user

1. A Claude Code terminal is focused. The CT shows the pixel-art tiles. Round button 2 jumps to tab 2.
2. The Compact tile types `/compact` completely. If characters get lost, raise the `("sleep", 80)` in `text_enter`.
3. The wheel shows the mascot full-screen and reacts to tap, double tap and spinning; long press sends Enter.
4. With hooks on: the mascot types while Claude works and waves with a `!` on a permission prompt.
5. Log the result in `~/.config/loupedeck-cc/status.md` (date, OS, terminal, software version, what works).

Logs: `%LOCALAPPDATA%\Logi\LogiPluginService\Logs\plugin_logs\ClaudeMascot.log` and `_errors.log`.
"already loaded" in the log is normal.

## 6. Changing things

- Button map and captions: `gen_profile.py` (`build()` and `LABELS`). Keep README tables in sync.
- Icons: `art/pixelart.py` → `tile()` + `TILE_NAMES`. Wheel animations: `wheel_frame()` + `WHEEL_STATES`.
  Draw everything in code. After changes, run `python art/render_docs.py` and look at `docs/img/*` before installing.
- Mascot behaviour: `plugin/Mascot.cs`. Wheel input: `plugin/WheelToolClawd.cs`.
- The repo is public: github.com/kazziu/loupedeck-claude-code. Commit and push improvements.

## 7. macOS (not tested yet)

- Profiles: confirm the path from step 0. The default app is probably `@_defaultmac`.
- Write `install_mac.sh` modelled on `install_win.ps1` (`pkill LogiPluginService`, copy, `open -a`).
- `gen_profile.py --os mac`: take `layoutId` from any `keyboardKey` in an existing Mac profile, and check
  `processOrBundleName` and the iTerm2 / Ghostty tab shortcuts.
- Plugin: replace `user32` `mouse_event` / `keybd_event` with CGEvent, build to the `mac` folder
  (`pluginFolderMac`) and check `PluginApiDir` in the csproj.

## 8. Fallback

If a future software version changes the format, ask the user to create one profile with a single Text tile
in the Loupedeck app and export it as `~/.config/loupedeck-cc/sample.lp5`. Unzip it (it is a zip), diff it
against `docs/loupedeck-format.md`, update the generator and the notes.

## 9. Optional: auto-run when the CT is plugged in

Only if the user wants it. Windows: Task Scheduler on event ID 2003
(Microsoft-Windows-DriverFrameworks-UserMode) running `claude -p "/loupedeck-claude-code"` only when the
profile is missing. macOS: a Hammerspoon `hs.usb.watcher`. Read the vendor id from step 0; do not hard-code it.
