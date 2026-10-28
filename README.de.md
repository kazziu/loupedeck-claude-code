<p align="center">
  <img src="docs/img/hero.png" alt="Loupedeck CT mit dem Claude-Code-Profil und dem Clawd-Tamagotchi auf dem Rad" width="100%">
</p>

<h1 align="center">Loupedeck CT × Claude Code</h1>

<p align="center">
  <b>Macht aus einem Loupedeck CT ein Bedienpult für Claude Code</b>: handcodierte Pixel-Art-Kacheln<br>
  und auf dem großen Rad ein Pixel-Tamagotchi, das auf das reagiert, was Claude gerade tut.
</p>

<p align="center">
  <a href="README.md">English</a> · <b>Deutsch</b> · <a href="README.pl.md">Polski</a>
</p>

---

## Was du bekommst

| | |
|---|---|
| **12 + 12 Touch-Kacheln** | `/compact`, `/clear`, `/model`, `/resume`, `/remote-control`, Plan-Modus, Esc, Strg+C, `git status`, neue Sitzung, `claude -c` und eine zweite Seite mit deinen eigenen Prompts. |
| **8 runde Tasten** | Direkt zu Claude-Code-Sitzung 1–8 springen. Funktioniert mit einer Wand aus einzelnen Terminalfenstern (nummeriert in Leserichtung: oberste Reihe zuerst, von links nach rechts) und mit Tabs in einem Fenster. Fn + Taste wechselt immer den Tab. |
| **Drehregler** | Vorheriger/nächster Tab, Schriftgröße im Terminal, Systemlautstärke. |
| **Großes Rad** | Clawd, ein Tamagotchi, das auf dem runden Display wohnt. Drehen scrollt weiterhin das Terminal. |
| **Claude-Code-Hooks** | Clawd tippt auf einem Laptop, während Claude arbeitet. Wenn Claude dich braucht, winkt er, zeigt ein `!` und **das Rad vibriert**. Er feiert, wenn eine Aufgabe fertig ist, und schwitzt, wenn ein Tool fehlschlägt. |
| **3 Sprachen** | Beschriftungen auf Englisch, Deutsch oder Polnisch. Claude-Code-Befehle behalten ihre echten Namen. |
| **Alles ist Code** | Das Profil, jedes Icon und jeder Animationsframe werden von Skripten erzeugt. Alles lässt sich neu bauen, anpassen und versionieren. |

<table>
  <tr>
    <td align="center" width="62%"><img src="docs/img/loupedeck-app.png" alt="Echter Screenshot des Profils in der Loupedeck-App"><br>
      <sub><b>Live</b> (polnische Beschriftung). In einer Sitzung ist gerade ein Tool fehlgeschlagen, deshalb hat Clawd X-Augen und Schweißtropfen.<br>Die zwei Punkte darunter sind zwei Claude-Code-Sitzungen, die weiterarbeiten.</sub></td>
    <td align="center"><img src="docs/img/wheel.gif" alt="Clawd-Animationen" width="240"><br>
      <sub>Alle Rad-Animationen, Pixel für Pixel in <code>art/pixelart.py</code> erzeugt.</sub></td>
  </tr>
</table>

## Clawd, das Rad-Tamagotchi

<p align="center"><img src="docs/img/states.png" alt="Alle Zustände des Maskottchens" width="100%"></p>

| Du | Clawd |
|---|---|
| tippst auf das Rad | lässt sich streicheln (Herzen). Wenn er hungrig ist, isst er einen Keks. |
| tippst doppelt | tanzt |
| drückst lange | das Rad sendet **Enter** (seine alte Aufgabe) |
| drehst das Rad | das Rad scrollt das Terminal; zu schnell, und Clawd wird schwindelig |
| lässt ihn 3 Min. allein | schläft ein |
| vergisst ihn ca. 45 Min. | wird hungrig (Gedankenblase mit Keks) |

| Claude Code (über Hooks) | Clawd |
|---|---|
| du sendest einen Prompt / ein Tool läuft | tippt auf seinem Laptop |
| Berechtigungsabfrage, Rückfrage oder Leerlauf | winkt, zeigt `!`, **das Rad vibriert** |
| ein Tool schlägt fehl | X-Augen, Schweißtropfen, zittert |
| `/compact` | wird zusammengedrückt |
| der Turn endet (`Stop`) | springt, Konfetti |
| eine Sitzung startet | sagt HI |

Punkte unten auf dem Rad zeigen, wie viele Sitzungen arbeiten (orange) oder auf dich warten (gelb blinkend), bis zu 8.

## Voraussetzungen

- **Loupedeck CT** und **Logi Plugin Service 6.x** (die aktuelle Loupedeck-Software). Getestet mit 6.4.1 unter Windows 11.
- **Claude Code** im Windows Terminal (nativ oder WSL). Unter macOS sind iTerm2 / Ghostty vorgesehen, der Mac-Weg ist aber noch nicht getestet (siehe [macOS](#macos)).
- **Python 3.9+** mit Pillow (`pip install pillow`) für die Generatoren.
- **.NET 10 SDK** zum Bauen des Rad-Plugins. Logi Plugin Service 6.4 läuft auf .NET 10, .NET 8 reicht also nicht.

## Installation

Das Repo ist ein [Claude-Code-Skill](https://docs.claude.com/en/docs/claude-code/skills). Am einfachsten macht es Claude selbst:

```bash
git clone https://github.com/kazziu/loupedeck-claude-code ~/.claude/skills/loupedeck-claude-code
```

dann in Claude Code:

```
/loupedeck-claude-code
```

Der Skill prüft Betriebssystem, Terminal und Loupedeck-Installation und fragt nach der Sprache. Danach baut er das Plugin, erzeugt das Profil, installiert alles (mit Backups) und führt dich durch einen 2-Minuten-Test am Gerät.

<details>
<summary><b>Manuelle Installation (Windows)</b></summary>

```powershell
$SK = "$HOME\.claude\skills\loupedeck-claude-code"; $C = "$HOME\.config\loupedeck-cc"
mkdir $C -Force; Copy-Item "$SK\docs\prompts.de.txt" "$C\prompts.txt"

python "$SK\build_plugin.py" --out "$C\build-plugin"                       # braucht dotnet 10
python "$SK\gen_profile.py" --os win --out "$C\build-win" --prompts "$C\prompts.txt" --lang de --wheel-plugin
python "$SK\gen_profile.py" --os win --out "$C\build-win" --prompts "$C\prompts.txt" --lang de --wheel-plugin --target default
powershell -File "$SK\install_win.ps1" -Build "$C\build-win" -Plugin "$C\build-plugin\ClaudeMascot" -MakeDefault

python "$SK\hooks\install_hooks.py"                                        # optional: Claude-Code-Hooks
```

Windows Terminal belegt `Strg+Alt+1…8` bereits mit den Tabs. Für den „Tabs“-Regler füge `nextTab` / `prevTab` auf `ctrl+alt+right` / `ctrl+alt+left` mit `"tabSwitcherMode": "disabled"` hinzu.
</details>

<details>
<summary><b>Was auf deinem Rechner geändert wird</b></summary>

| Wo | Was | Rückgängig |
|---|---|---|
| `%LOCALAPPDATA%\Logi\LogiPluginService\Applications\Loupedeck20\windowsterminal` | Profil, das Windows Terminal folgt | Ordner löschen |
| `…\Loupedeck20\@_defaultwin\Profiles\<GUID>` + `ApplicationInfo.json` | dasselbe Profil als CT-Standard (mit `-MakeDefault`); dein altes Standardprofil bleibt erhalten | altes Profil in der Loupedeck-App wählen |
| `…\LogiPluginService\Plugins\ClaudeMascot` | das Rad-Plugin | Ordner löschen |
| `~/.claude/settings.json` → `hooks` | 15 asynchrone Hooks, die `~/.config/loupedeck-cc/sessions/*.json` schreiben | `python hooks/install_hooks.py --remove` |
| `~/.config/loupedeck-cc/backup-*` | Backups vor jeder Installation | |
</details>

## Anpassen

- **Eigene Prompts (Seite 2):** `~/.config/loupedeck-cc/prompts.txt` bearbeiten. Jede Zeile hat die Form `Beschriftung | Prompt-Text | Icon`. Danach den Skill erneut ausführen.
- **Sprache:** `--lang en|de|pl` oder `{"lang": "de"}` in `~/.config/loupedeck-cc/config.json`. Die Übersetzungen stehen in `LABELS` in `gen_profile.py`, eine neue Sprache ist also ein weiteres Wörterbuch.
- **Tastenbelegung:** Maßgeblich ist `gen_profile.py`. Jede Kachel ist eine Zeile, z. B. `b.text_enter("Compact", "/compact", "compact")`.
- **Icons und Animationen:** `art/pixelart.py`. Jedes Icon ist eine kleine Funktion auf einem 20×20-Raster, jeder Rad-Zustand eine Funktion auf 40×40. `python art/render_docs.py` rendert eine Vorschau als PNG/GIF.

## Wie es funktioniert

```
gen_profile.py ──► ProfileInfo.json + ActionIcons/*.ict ──► Logi Plugin Service ──► Kacheln, Tasten, Regler
art/pixelart.py ─┬► Kachel-Icons (Base64-PNG in .ict)
                 └► Rad-Frames ──► plugin/ (C#, .NET 10) ──► WheelToolClawd zeichnet 240×240 aufs Rad
Claude-Code-Hooks ──► hooks/mascot_hook.py ──► ~/.config/loupedeck-cc/sessions/*.json ──► Plugin liest ca. jede Sekunde
```

Das Loupedeck-Profilformat ist nicht dokumentiert. Alles hier wurde aus den mitgelieferten Profilen,
dem Bundle der Konfigurationsoberfläche und dem IL-Code des Dienstes erschlossen.
Die Notizen stehen in **[docs/loupedeck-format.md](docs/loupedeck-format.md)** (auf Englisch). Wenn du
irgendetwas für Loupedeck / Logi Plugin Service baust, fang dort an; es spart dir einen Tag.

Das Wichtigste:

- Profile sind einfaches JSON (`ProfileInfo.json`). `Loupedeck20` = CT, `30` = Live, `50` = Live S.
- Makro-Schritte nutzen `$@Generic___@KeyboardKey` mit `"<Mods+Taste>___<keyboardLayoutId>___<Label>___"` und `$@Generic___@SendText`. Die Tastennamen (`Back`, `Return`, `Minus`, `Equals`, `Key0`…) stammen aus einer Tabelle in der Konfigurationsoberfläche.
- Kachel-Icons sind `.ict`-Dateien (JSON: Base64-PNG + Beschriftung, Koordinaten in Prozent), benannt nach der Action-ID.
- **Vollbild auf dem Rad:** in einem Plugin von `WheelTool` erben und im Profil `templateName: "<PluginName>___<Klasse>"` angeben. Ohne Präfix sucht der Dienst nur im *nativen* Plugin des Profils, und das Rad bleibt tot.
- Der Dienst lädt Plugin-DLLs aus dem Speicher, `Assembly.Location` ist also leer. Assets müssen in die DLL eingebettet werden.
- Auch „universelle“ Plugins brauchen eine von `ClientApplication` abgeleitete Klasse, sonst lehnt der Loader sie ab.

## macOS

Der Generator hat einen `mac`-Zweig (`⌘1…8` für iTerm2- / Ghostty-Tabs, `@_defaultmac`), der aber noch
nicht auf einem Mac getestet wurde. Offen sind: ein `install_mac.sh` nach dem Vorbild von `install_win.ps1`,
Scrollen per CGEvent im Plugin (heute über `user32`) und das Prüfen der Profil- und SDK-Pfade. Der Skill
sagt Claude genau, was zu prüfen ist. PRs willkommen.

## Fehlerbehebung

| Symptom | Lösung |
|---|---|
| Rad schwarz / tot | Der `templateName` des Rads muss `ClaudeMascot___WheelToolClawd` sein. Siehe `%LOCALAPPDATA%\Logi\LogiPluginService\Logs\plugin_logs\ClaudeMascot.log`. |
| `Cannot load plugin … already loaded` im Log | Normal: Der Dienst scannt Plugins zweimal. |
| Plugin als deaktiviert gelistet | Dienst neu starten. Die Deaktivierungsliste lebt nur im Speicher. |
| Getippter Text verliert Zeichen | Den Schritt `("sleep", 80)` in `text_enter` in `gen_profile.py` erhöhen. |
| Maskottchen reagiert nie auf Claude | `python hooks/install_hooks.py` ausführen, eine neue Claude-Code-Sitzung starten und prüfen, ob in `~/.config/loupedeck-cc/sessions/` Dateien entstehen. |

## Credits und Hinweis

Inoffizielles Fanprojekt, nicht mit Anthropic oder Logitech verbunden und nicht von ihnen unterstützt.
*Claude* und *Claude Code* sind Marken von Anthropic. *Loupedeck* und *Logi* sind Marken von Logitech.
Das Maskottchen ist Fan-Art, von Grund auf in Python gezeichnet, Pixel für Pixel.

Entstanden in einer langen, spaßigen Session von [@kazziu](https://github.com/kazziu) zusammen mit Claude Code.

[MIT-Lizenz](LICENSE)
