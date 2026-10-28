# Format profili Loupedeck (Logi Plugin Service 6.x): notatki

Rozpracowane 2026-10-28 na Windows 11, Logi Plugin Service 6.4.1, Loupedeck CT. Nie trzeba było `sample.lp5`,
bo na dysku leżało ~88 profili do analizy.

## Gdzie co leży
- Windows: `%LOCALAPPDATA%\Logi\LogiPluginService\Applications\Loupedeck20\<app>\Profiles\<GUID>\ProfileInfo.json`
  (ścieżka `%LOCALAPPDATA%\Loupedeck\Applications\...` dotyczyła Loupedeck 5 i już nie obowiązuje)
- macOS (do sprawdzenia): `~/Library/Application Support/Logi/LogiPluginService/Applications/Loupedeck20/`
- `Loupedeck20` = Loupedeck CT (Live = 30, Live S = 40 itd.).
- Własna aplikacja = folder `<app>` z `ApplicationInfo.json` (`processOrBundleName` = nazwa procesu małymi literami, bez .exe,
  np. `windowsterminal`) + `Profiles/<GUID>/ProfileInfo.json`. Sam ProfileInfo wystarcza, ikony i obrazki są opcjonalne.
- `.lp5` = zip: `ApplicationInfo.json`, `ProfileInfo.json`, `metadata/LoupedeckPackage.yaml` (+ opcjonalnie ActionImages/ActionIcons).
- Usługę trzeba zatrzymać przed zmianą plików (`LoupedeckSettings.ini` mówi wprost: nie ruszać, gdy działa).
  Restart: `Stop-Process LogiPluginService, Loupedeck`, potem `Start-Process "C:\Program Files\Logi\LogiPluginService\LogiPluginService.exe"`.

## Układ CT w `layout`
- `layoutModes[].touchPages[]`: 12 kafelków (indeks 0–11, wierszami). Kilka stron w jednym workspace = przesuwanie palcem
  oraz `$@Generic___@NextTouchPage` / `$@Generic___@PreviousTouchPage`.
- `encoderPages[].controls`: 6 pokręteł, 0–2 lewe (L1–L3), 3–5 prawe; każde ma `pressAction` i `rotateAction`.
- `wheelPages[]`: szablon `WheelToolAnalogClock`, `parameters.adjustment` = obrót koła, `parameters.actions` = dotyk.
- `roundPage`: 8 przycisków okrągłych (0–7). `squarePage`: 12 kwadratowych; w fabrycznych profilach 1 = Undo,
  3 = Enter, 4 = Save, 6/7/9/10 = góra/lewo/dół/prawo, 11 = dodatkowy. Indeksy 0, 2, 5, 8 nigdzie nie są używane
  (prawdopodobnie przyciski sprzętowe).
- Każdy przycisk ma `pressAction` i `fnPressAction` (z przytrzymanym Fn).

## Akcje
- Makro: wpis w `macroCommands` (`name` = GUID, `displayName` = etykieta na kafelku, `\n` = nowa linia),
  `actionEditorCommands` = kroki z parametrami, `actions` = kolejność (nazwy kroków albo `$@Generic___@Sleep___<ms>`).
  Na kafelek: `$@Generic___@Macro___<GUID>`.
- Krok klawisz: `templateName: $@Generic___@KeyboardKey`, `keyboardKey: "<Mod+...+Key>___<layoutId>___<etykieta>___"`.
  layoutId 68486165 = 0x04150415 = układ polski.
- Krok tekst: `templateName: $@Generic___@SendText`, `text`, `useClipboard: "false"`.
- Pokrętło-makro: `macroAdjustments` z `actionsLeft` / `actionsRight`, na pokrętło `$@Generic___@MacroAdjustment___<GUID>`.
- Gotowe: `$@Generic___@MouseWheel`, `$DefaultWin___Volume` / `$DefaultWin___ResetVolume` (wymaga `DefaultWin`
  w `additionalNativePluginNames`), `$@Generic___@ChangeWorkspace___<mode>|<wsGUID>`.

## Nazwy klawiszy (z tabeli UI: configui2/resources/app.asar)
Modyfikatory: `ControlOrCommand` (Ctrl na Windows, Cmd na Macu), `Control` (zawsze Ctrl), `AltOrOption`, `Shift`, `Windows`.
Klawisze: `KeyA`–`KeyZ`, `Key0`–`Key9`, `F1`–`F24`, `Back` (Backspace), `Return`, `Escape`, `Tab`, `Space`, `Minus`, `Equals`,
`Comma`, `Period`, `Oem1` (;), `Oem2` (/), `Oem3` (`), `Oem4` ([), `Oem6` (]), `Oem5` (\), `Oem7` ('), `ArrowUp/Down/Left/Right`,
`Home`, `End`, `PageUp`, `PageDown`, `Insert`, `Delete`, `Add`/`Subtract`/`Multiply`/`Divide` (numeryczna), `NumPad0`–`9`.
