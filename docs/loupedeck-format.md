# Logi Plugin Service 6.x: profile & plugin format notes

Reverse-engineered on Windows 11 with Logi Plugin Service **6.4.1** and a **Loupedeck CT**, from the
profiles that ship with the software, the configuration UI bundle (`configui2/resources/app.asar`) and
reflection over the service's own assemblies. Nothing here is official. It worked on 2026-10-28.

## Where things live

| | Windows | macOS |
|---|---|---|
| Profiles | `%LOCALAPPDATA%\Logi\LogiPluginService\Applications\<Device>\<app>\Profiles\<GUID>\` | `~/Library/Application Support/Logi/LogiPluginService/Applications/...` |
| Plugins | `%LOCALAPPDATA%\Logi\LogiPluginService\Plugins\<Name>\` | `~/Library/Application Support/Logi/LogiPluginService/Plugins/<Name>/` (DLL in `mac/`) |
| Plugin logs | `%LOCALAPPDATA%\Logi\LogiPluginService\Logs\plugin_logs\<Name>.log`, `_errors.log` | `.../LogiPluginService/Logs/plugin_logs/` |
| Settings | `%LOCALAPPDATA%\Logi\LogiPluginService\LoupedeckSettings.ini` (written on exit; *"Don't modify while running"*) | `.../LogiPluginService/LoupedeckSettings.ini` |
| Service | `C:\Program Files\Logi\LogiPluginService\LogiPluginService.exe` (.NET **10**) | `/Applications/Utilities/LogiPluginService.app`, started by launch agent `com.logi.pluginservice.launch` |

The old Loupedeck 5 path `%LOCALAPPDATA%\Loupedeck\Applications\...` is gone.

**Device codes:** `Loupedeck10` Original, `15` Loupedeck+, `20` **CT**, `30` Live, `40` Razer Stream Controller,
`50` Live S, `60` Razer Stream Controller X, `70` MX Creative Keypad, `71` MX Creative Dialpad, `72` Actions Ring.

**Restarting:** stop `LogiPluginService` and `Loupedeck` (UI) processes, edit files, start
`LogiPluginService.exe` again. Edits made while it runs may be overwritten.

## Applications

`Applications/<Device>/<app>/ApplicationInfo.json`:

```json
{
  "$type": "Loupedeck.Service.SupportedApplicationInfo, LoupedeckService",
  "name": "windowsterminal", "displayName": "Windows Terminal", "deviceType": "Loupedeck20",
  "nativePluginName": null, "hasNativePlugin": false,
  "processOrBundleName": "windowsterminal",
  "modes": [{"$type": "Loupedeck.Service.ApplicationMode, LoupedeckService", "name": "main", "parentModeName": null, "displayName": "Main"}],
  "defaultProfileName": "<profile GUID>", "isEnabled": true
}
```

- A custom app = a folder with this file. `processOrBundleName` is the process name, lower case, without `.exe` (bundle id on macOS).
- The system default app is `@_defaultwin` (native plugin `DefaultWin`, mode **`System`**). Setting its `defaultProfileName` makes a profile the device default; other app profiles still switch in with "follow active application".
- A profile folder only needs `ProfileInfo.json`. `ActionIcons/`, `ActionImages/` and `metadata/` are optional.

## `.lp5` package

A zip with `ApplicationInfo.json`, `ProfileInfo.json`, `metadata/LoupedeckPackage.yaml` (`type: Profile5`) and
optionally `ActionIcons/*.ict`. Import with *Import profile* in the app.

## ProfileInfo.json, CT layout

```
layout.layoutModes[] (one per app mode)
  touchPages[]    12 touch tiles each (index 0..11, row by row)
  encoderPages[]  6 dials: 0..2 left (L1..L3), 3..5 right; each has pressAction + rotateAction
  wheelPages[]    { templateName, parameters: { actions, adjustment } }
  workspaces[]    { touchPageNames[], encoderPageNames[], wheelPageNames[] }; several touch pages = swipe
layout.roundPage   8 round buttons (0..7)
layout.squarePage  12 square buttons; factory profiles use 1 = Undo, 3 = Enter, 4 = Save,
                   6/7/9/10 = up/left/down/right, 11 = extra; 0/2/5/8 are never assigned (hardware keys)
```

Every button has `pressAction` and `fnPressAction` (with Fn held). Action strings:

| Action | String |
|---|---|
| user macro | `$@Generic___@Macro___<GUID>` |
| macro dial (left/right) | `$@Generic___@MacroAdjustment___<GUID>` |
| next / previous touch page | `$@Generic___@NextTouchPage`, `$@Generic___@PreviousTouchPage` |
| change workspace | `$@Generic___@ChangeWorkspace___<mode>\|<workspaceGUID>` |
| mouse wheel | `$@Generic___@MouseWheel` |
| system volume | `$DefaultWin___Volume` (rotate), `$DefaultWin___ResetVolume` (press); needs `DefaultWin` in `additionalNativePluginNames` |
| plugin action | `$<PluginName>___<Namespace.ClassName>` |
| nothing | `$@Generic___@None` or `null` |

## Macros

```json
{
  "$type": "Loupedeck.Service.ApplicationProfileMacroCommand, LoupedeckService",
  "isCommand": true, "name": "<GUID>", "displayName": "Compact", "groupName": "Claude Code",
  "superGroupName": "@macro", "supportedOs": "All", "supportedModes": ["main"],
  "actionEditorCommands": [
    {"$type": "Loupedeck.Service.MacroActionEditorCommand, LoupedeckService", "name": "<GUID1>",
     "templateName": "$@Generic___@SendText",
     "actionParameters": {"$type": "System.Collections.Generic.Dictionary`2[[System.String, System.Private.CoreLib],[System.String, System.Private.CoreLib]], System.Private.CoreLib",
                          "text": "/compact", "useClipboard": "false"}},
    {"...": "...", "name": "<GUID2>", "templateName": "$@Generic___@KeyboardKey",
     "actionParameters": {"...": "...", "keyboardKey": "Return___68486165___Return___"}}
  ],
  "actions": ["<GUID1>", "$@Generic___@Sleep___80", "<GUID2>"]
}
```

- `displayName` is the tile caption when there is no icon. A literal `\n` breaks the line.
- `keyboardKey` = `<Mod+...+Key>___<keyboardLayoutId>___<display label>___`. The layout id is the Windows HKL as decimal, e.g. `68486165` = `0x04150415` (Polish). Longer variants with `win-<vk>#¤%&+?...` exist but are not required.
- Macro dials (`macroAdjustments`) have `actionsLeft` / `actionsRight` lists plus `clickRateLimit`.

### Key names (from the UI's key table)

Modifiers: `ControlOrCommand` (Ctrl on Windows, **Cmd** on macOS), `Control` (always Ctrl), `AltOrOption`, `Shift`, `Windows`.

Keys: `KeyA`–`KeyZ`, `Key0`–`Key9`, `F1`–`F24`, `Back` (Backspace), `Return`, `Escape`, `Tab`, `Space`, `Minus`, `Equals`,
`Comma`, `Period`, `Oem1` `;`, `Oem2` `/`, `Oem3` `` ` ``, `Oem4` `[`, `Oem5` `\`, `Oem6` `]`, `Oem7` `'`,
`ArrowUp/Down/Left/Right`, `Home`, `End`, `PageUp`, `PageDown`, `Insert`, `Delete`,
`Add`/`Subtract`/`Multiply`/`Divide`/`Decimal` (numpad), `NumPad0`–`NumPad9`, `VolumeUp/Down/Mute`, `MediaPlayPause`…

## Tile icons (`.ict`)

`Profiles/<GUID>/ActionIcons/<actionId>.ict`, for example `$@Generic___@Macro___<GUID>.ict` or even
`$@Generic___@NextTouchPage.ict`:

```json
{"backgroundColor": 4278190080, "items": [
  {"itemType": "Image", "image": "<base64 PNG>", "imageFileName": "x.png", "imageColor": 4294967295,
   "imageRotation": "None", "isVisible": true, "area": {"x": 12, "y": 0, "width": 76, "height": 76}},
  {"itemType": "Text", "text": "Compact", "originalText": null, "textColor": 4294967295, "fontSize": 4,
   "fontName": "Arial", "isVisible": true, "area": {"x": 0, "y": 76, "width": 100, "height": 24}}]}
```

`area` is in **percent** of the tile. Colors are ARGB as unsigned ints.

## Plugins (C#)

- Package: `Plugins/<Name>/metadata/LoupedeckPackage.yaml` (`type: plugin4`, `pluginFileName`, `pluginFolderWin: win`, `supportedDevices`) + `win/<Name>Plugin.dll`.
- Reference `C:\Program Files\Logi\LogiPluginService\PluginApi.dll` (6.4.1 targets **net10.0**; a net8 project cannot reference it). Shipped plugins built against PluginApi 6.0 / net8 still load.
- Required classes: `<Name>Plugin : Plugin` **and** a `ClientApplication` subclass, even for universal plugins (`HasNoApplication => true`). Without the latter: *"Cannot load plugin"*.
- The DLL is loaded **from memory**, so `Assembly.Location` is `""`. Embed assets (`EmbeddedResource`) and read them with `GetManifestResourceStream`.
- Useful API: `BitmapImage.FromArray(png)`, `new BitmapBuilder(w, h)`, `DrawImage`, `FillRectangle`, `FillCircle`, `ToImage()`; `PluginDynamicCommand` / `PluginDynamicAdjustment` with `ActionImageChanged()` for live images.
- *"Cannot load plugin … already loaded"* in the log is normal (two scans). A plugin whose `Load()` throws goes on an in-memory disabled list until restart.

### Full-screen wheel (CT)

`WheelToolGeneric1x1` only shows an action image as a small icon with its caption. For the whole
240×240 round screen, subclass `Loupedeck.Devices.Loupedeck2Devices.WheelTool`:

```csharp
public class WheelToolClawd : WheelTool
{
    public WheelToolClawd() : base("Clawd", "Claude Code") { }
    protected override void OnStart() { /* subscribe, then */ this.Draw(image); }
    protected override BitmapImage CreateImage() => ...;           // 240x240
    protected override void OnEncoderEvent(DeviceEncoderEvent e) { /* e.Clicks */ }
    protected override void OnTouchEvent(DeviceTouchEvent e) { /* e.EventType: Tap, DoubleTap, LongPress, Move… */ }
    // this.Vibrate(waveformIndex) triggers wheel haptics; invalid indices are corrected by the service
}
```

Reference it in the profile as **`"templateName": "<PluginName>___<ClassName>"`**.
`PluginManager.CreateWheelTool` splits the name on `___` (`CombinedString.Separator`). With two parts it
looks the class up in that plugin, matching the **short** class name. With one part it only searches
PluginApi, the service itself and the profile's **native** plugin, so a plain `"WheelToolClawd"` in a profile
whose native plugin is DefaultWin gives a dead wheel without any log entry.
