---
name: loupedeck-claude-code
description: Konfiguruje Loupedeck CT jako pulpit sterujący do Claude Code (skróty, przeskakiwanie między terminalami, komendy slash, scroll kołem). Uruchom po podpięciu Loupedecka do nowego komputera (Windows lub macOS) lub gdy chcesz zmienić mapę przycisków.
---

# Loupedeck CT → Claude Code

Cel: po uruchomieniu tego skilla na danym komputerze Loupedeck CT ma gotowy profil
"Claude Code" podpięty pod terminal, a terminal ma skonfigurowane skróty, których
profil używa. Skill jest idempotentny — można go uruchamiać wielokrotnie.

## 0. Rozpoznanie środowiska (zawsze najpierw)

1. OS: `uname -s` (Darwin = macOS) albo `$env:OS` (Windows_NT).
2. Czy Loupedeck software jest zainstalowany i działa (od wersji 6 to "Logi Plugin Service"):
   - Windows: `Get-Process LogiPluginService, Loupedeck*`; profile w `%LOCALAPPDATA%\Logi\LogiPluginService\Applications\Loupedeck20\`
   - macOS: `pgrep -l -i 'LogiPluginService|Loupedeck'`; profile prawdopodobnie w
     `~/Library/Application Support/Logi/LogiPluginService/Applications/Loupedeck20/` (sprawdź i popraw tę linijkę)
   - `Loupedeck20` = Loupedeck CT. Szczegóły formatu: `docs/format-notes.md` w folderze skilla.
   - Skill żyje w prywatnym repo `github.com/kazziu/loupedeck-claude-code`. Na nowej maszynie:
     `git clone https://github.com/kazziu/loupedeck-claude-code ~/.claude/skills/loupedeck-claude-code`.
     Zmiany wprowadzone tutaj commituj i pushuj, żeby druga maszyna je dostała.
   Jeśli brak softu — zatrzymaj się i powiedz użytkownikowi, że musi zainstalować
   Loupedeck Software (loupedeck.com/downloads); nic nie da się zrobić bez niego.
3. Czy urządzenie jest podpięte: Windows `Get-PnpDevice -FriendlyName "*Loupedeck*"`,
   macOS `system_profiler SPUSBDataType | grep -i loupedeck`.
4. Który terminal jest w użyciu (wykryj, nie zgaduj):
   - Windows: Windows Terminal (`wt.exe`, settings.json w `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_*\LocalState\`), ewentualnie WSL w środku.
   - macOS: iTerm2, Ghostty, Warp, Terminal.app — sprawdź `/Applications`.
   - Czy jest `tmux` (preferowane: jedna sesja tmux, w niej okna 1–8 = osobne sesje Claude Code).
   Jeśli jest kilka kandydatów — zapytaj użytkownika jednym pytaniem, który ma być celem profilu.

## 1. Skonfiguruj terminal tak, żeby skróty były deterministyczne

Loupedeck wysyła tylko klawisze/tekst, więc terminal musi mieć stabilne skróty.

**tmux (zalecane na obu systemach)** — dopisz do `~/.tmux.conf` (nie nadpisuj istniejącego pliku, dodaj blok z komentarzem `# loupedeck`):
```
# loupedeck
bind -n M-1 select-window -t 1
bind -n M-2 select-window -t 2
bind -n M-3 select-window -t 3
bind -n M-4 select-window -t 4
bind -n M-5 select-window -t 5
bind -n M-6 select-window -t 6
bind -n M-7 select-window -t 7
bind -n M-8 select-window -t 8
bind -n M-n next-window
bind -n M-p previous-window
set -g mouse on
```
Stwórz też skrypt `cc-sessions` (bash), który startuje sesję tmux `cc` z oknami 1–8,
każde w katalogu z listy `~/.config/loupedeck-cc/projects.txt` (jeśli pliku nie ma —
utwórz go z komentarzem i poproś użytkownika o ścieżki projektów).

**Windows Terminal (gdy brak tmux)**: `ctrl+alt+1..8` → `switchToTab` index 0..7 to domyślne skróty WT,
nie dodawaj ich (indeks jest od zera). Dopisz tylko `ctrl+alt+right/left` = nextTab/prevTab z
`"tabSwitcherMode": "disabled"`. WT 1.24+ trzyma komendy w `actions` (z `id`), a klawisze osobno w `keybindings`.
Rób backup pliku przed edycją.

**iTerm2 / Ghostty (gdy brak tmux)** — ⌘1–⌘8 działa domyślnie, nic nie zmieniaj.

## 2. Mapa przycisków (źródło prawdy)

Modyfikatory: Windows = Ctrl/Alt, macOS = ⌘/⌥. Niżej "MOD1" to Alt (Win) / ⌥ (Mac),
"MOD2" to Ctrl (Win) / ⌘ (Mac).

| Element | Akcja Loupedeck | Co wysyła |
|---|---|---|
| Przyciski okrągłe 1–8 | Keyboard Shortcut | tmux: `MOD1+N`; Windows Terminal: `Ctrl+Alt+N`; iTerm2/Ghostty: `⌘N` |
| Kafelek 1 "Compact" | Text + Enter | `/compact` |
| Kafelek 2 "Clear" | Text + Enter | `/clear` |
| Kafelek 3 "Model" | Text + Enter | `/model` |
| Kafelek 4 "Resume" | Text + Enter | `/resume` |
| Kafelek 5 "Plan" | Keyboard Shortcut | `Shift+Tab` (przełącza tryb: normal / auto-accept / plan) |
| Kafelek 6 "Stop" | Keyboard Shortcut | `Esc` |
| Kafelek 7 "Kill" | Keyboard Shortcut | `Ctrl+C` |
| Kafelek 8 "git status" | Text + Enter | `git status` |
| Kafelek 9 "Remote" | Text + Enter | `/remote-control` (`git diff` przeniesiony na stronę 2, kafelek 11) |
| Kafelek 10 "Nowa sesja" | Text + Enter | `claude` |
| Kafelek 11 "Kontynuuj" | Text + Enter | `claude -c` |
| Kafelek 12 "Strona 2" | Switch Page | przejście na stronę 2 (własne prompty) |
| Duże koło | szablon `ClaudeMascot___WheelToolClawd` (pełny ekran 240×240) | obrót = scroll terminala (za szybko = zawroty głowy); dotyk = karmienie / budzenie / głaskanie; podwójny dotyk = taniec; przytrzymanie = `Enter` |
| (bez wtyczki) | Mouse Scroll + Enter | fallback: zegar, obrót = scroll, dotyk = `Enter` |
| Pokrętło L1 | Keyboard Shortcut ± | `MOD1+n` / `MOD1+p` (tmux) lub next/prev tab |
| Pokrętło L2 | Keyboard Shortcut ± | `MOD2+=` / `MOD2+-` (rozmiar czcionki) |
| Pokrętło L3 | System: Volume | głośność |
| Pokrętło P1–P3 | wolne | zostaw puste |
| Undo | Keyboard Shortcut | `Ctrl+_` (undo w linii Claude Code) |
| Save | Text + Enter | `git add -A && git commit -m "wip"` |
| ⌫ / 🗑 / ␣ / ⏎ | Keyboard Shortcut | Backspace / `Ctrl+U` (skasuj linię) / Space / Enter |
| A/B/C/D (strzałki) | Keyboard Shortcut | ↑ ↓ ← → |

Strona 2 kafelków: do 11 ulubionych promptów z `~/.config/loupedeck-cc/prompts.txt`
(jedna linia = jeden kafelek, format `Etykieta | tekst promptu | ikona`). Jeśli pliku nie ma, utwórz go
z 3 przykładami (`review`, `tests`, `explain`).

**Grafika (tylko kodem, bez generatorów obrazu):** `art/pixelart.py` rysuje piksel po pikselu maskotkę
Claude Code. Ikony kafelków i pokręteł (siatka 20×20) trafiają do profilu jako `ActionIcons/<actionId>.ict`
(PNG w base64 + podpis). Klatki koła (siatka 40×40 ×6 = 240 px, maskotka zajmuje 80% szerokości, 11 stanów: idle, walk, sleep, happy, eat,
dizzy, hungry, dance, work, pet) są wbudowane w DLL wtyczki. Nowa ikona = funkcja w `tile()` + nazwa
w `TILE_NAMES`. Podgląd: wyrenderuj `tile(n).image(6)` / `wheel_frame(s, f).image(5)` do PNG i obejrzyj.

**Wtyczka ClaudeMascot (`plugin/`, C#):** tamagotchi na kole. Pełny ekran koła daje tylko własna klasa
`WheelTool` (`plugin/WheelToolClawd.cs`), a w profilu trzeba ją wskazać jako `templateName: "ClaudeMascot___WheelToolClawd"`.
Bez prefiksu `<wtyczka>___` usługa (`PluginManager.CreateWheelTool`) szuka klasy tylko w PluginApi, w samej usłudze
i we wtyczce **natywnej** profilu (np. DefaultWin), więc koło zostaje martwe.
Szablon `WheelToolGeneric1x1` pokazuje obraz akcji tylko jako małą ikonę z podpisem. Głód rośnie przez ~45 min, po 3 min bez
dotyku maskotka zasypia, czasem spaceruje albo tańczy. Gdy plik `~/.config/loupedeck-cc/claude-state`
zawiera `working` (np. zapisywany przez hooki Claude Code), maskotka pisze na laptopie.
Host Logi Plugin Service 6.4 działa na **.NET 10**, więc wtyczka wymaga .NET 10 SDK. Loader wymaga
klasy `ClientApplication` także we wtyczce uniwersalnej i wczytuje DLL z pamięci (`Assembly.Location`
jest puste), dlatego zasoby są wbudowane jako EmbeddedResource.

W makrach z kilkoma klawiszami zawsze wstaw Delay 60 ms między klawiszami.

Komendy git (kafelki 8–9 i Save) idą z prefiksem `!`, czyli `!git status`. W oknie Claude Code `!` to tryb bash,
więc komenda wykona się od razu, a nie trafi do modelu jako wiadomość. Poza tym PowerShell 5.1 nie zna `&&`.
Kwadratowe na CT: 1 = Undo, 3 = ⏎ (Fn: Spacja), 4 = Save, 6/7/9/10 = strzałki, 11 = ⌫ (Fn: Ctrl+U).
Pokrętło L2 wciśnięte = reset czcionki (`MOD2+0`).
Źródłem prawdy jest teraz `gen_profile.py` w folderze skilla: zmiany mapy wprowadzaj tam i w tej tabelce.

## 3. Wygeneruj i zainstaluj profil

Format jest już rozpracowany (patrz `format-notes.md`), a generator leży obok tego pliku:

```
C=~/.config/loupedeck-cc
python build_plugin.py --out $C/build-plugin                     # wtyczka + klatki (wymaga dotnet 10)
python gen_profile.py --os win --out $C/build-win --prompts $C/prompts.txt --wheel-plugin
python gen_profile.py --os win --out $C/build-win --prompts $C/prompts.txt --wheel-plugin --target default
powershell -File install_win.ps1 -Build $C/build-win -Plugin $C/build-plugin/ClaudeMascot -MakeDefault
```
Generator robi `build-<os>/app/` (osobna aplikacja: profil przełącza się sam, gdy terminal jest na wierzchu),
`build-<os>/default/<GUID>/` (ten sam profil dla domyślnej aplikacji systemu `@_defaultwin`, tryb `System`)
oraz `claude-code-<os>.lp5`. Identyfikatory są stałe (uuid5), więc ponowne uruchomienie nadpisuje ten sam profil.
`install_win.ps1` robi backup, zatrzymuje usługę, podmienia pliki, z `-MakeDefault` ustawia
`defaultProfileName` w `@_defaultwin/ApplicationInfo.json` (stary profil zostaje) i uruchamia usługę.
Użytkownik chce, żeby profil Claude Code był **domyślny** na każdej maszynie.

**macOS (repo sklonowane do `~/.claude/skills/loupedeck-claude-code`):** nie ma jeszcze `install_mac.sh`.
Napisz go na wzór `install_win.ps1` po sprawdzeniu ścieżek (sekcja 0), domyślna aplikacja to
prawdopodobnie `@_defaultmac`. We wtyczce scroll używa `mouse_event` z user32, który działa tylko
na Windows; na Macu podmień go na CGEvent (`CGEventCreateScrollWheelEvent`) i zbuduj do folderu `mac`
(`pluginFolderMac` w `plugin/LoupedeckPackage.yaml`). `PluginApiDir` dla macOS w csproj to zgadywana
ścieżka, więc ją zweryfikuj.
Na Macu przed pierwszym użyciem sprawdź w `gen_profile.py` gałąź `mac`: `layoutId` (weź z dowolnego
`keyboardKey` w istniejącym profilu na Macu), `processOrBundleName` terminala i skróty next/prev tab.

Tylko gdy generator nie działa (np. nowa wersja softu zmieniła format):

1. Sprawdź, czy w `~/.config/loupedeck-cc/` leży `sample.lp5`. Jeśli nie — poproś użytkownika,
   żeby w Loupedeck Software stworzył pusty profil "Claude Code" (Custom Profile → aplikacja = wykryty
   terminal), przypisał JEDEN dowolny kafelek na akcję Text i wyeksportował go jako `sample.lp5`
   do tego katalogu. Zatrzymaj się do czasu, aż plik się pojawi.
2. Rozpakuj `sample.lp5` (to archiwum zip) do katalogu roboczego, przeczytaj wszystkie JSON-y,
   zrozum strukturę: identyfikatory elementów (kafelki, pokrętła, koło, przyciski okrągłe),
   jak zapisana jest akcja Text, Keyboard Shortcut, Switch Page, Mouse Scroll. Zapisz wnioski
   w `~/.config/loupedeck-cc/format-notes.md`, żeby następne uruchomienie nie musiało badać od nowa.
3. Wygeneruj skryptem (Python) nowy profil wg mapy z sekcji 2, z poprawnymi modyfikatorami dla
   tego OS, spakuj do `claude-code-<os>.lp5` i zapisz w `~/.config/loupedeck-cc/`.
4. Zaimportuj: najpierw spróbuj skopiować wynikowy katalog profilu w to samo miejsce, w którym
   soft trzyma profile (ścieżki z sekcji 0), i zrestartuj Loupedeck Software
   (Windows: `Stop-Process Loupedeck*; Start-Process "C:\Program Files\Loupedeck\..."`,
   macOS: `pkill Loupedeck; open -a Loupedeck`). Jeśli profil nie pojawia się w liście —
   powiedz użytkownikowi, żeby zrobił Import profile z pliku `.lp5` ręcznie (jedno kliknięcie).
5. Ustaw w profilu "Adapt to App" na wykryty terminal, żeby przełączał się sam.

Fallback, jeśli format okaże się nieczytelny: zbuduj plugin przez oficjalne Loupedeck Plugin SDK
(C#, .NET) — przyciski i pokrętła definiowane w kodzie, działa na Windows i macOS, da się później
dodać dynamiczne etykiety (np. nazwy sesji Claude Code na kafelkach). Zacznij od szablonu
`dotnet new` z repozytorium SDK Loupedeck na GitHubie, zainstaluj przez Add-on Manager.

## 4. Weryfikacja

1. Poproś użytkownika, żeby nacisnął przycisk okrągły 2 i kafelek "Compact" w otwartym terminalu
   z Claude Code. Sprawdź w logu tmux / treści terminala, czy przełączyło okno i wpisało `/compact`.
2. Jeśli Text wpisuje się ze zjedzonymi znakami — zwiększ Delay w akcjach Text lub włącz
   w Loupedeck "slow typing" (ustawienie akcji Text).
3. Zapisz w `~/.config/loupedeck-cc/status.md`: data, OS, terminal, wersja Loupedeck Software,
   co działa, co nie.

## 5. (Opcjonalnie) automatyczne uruchomienie po wpięciu USB

Tylko jeśli użytkownik tego chce — spytaj. Mechanizm: watcher wykrywa Loupedecka i odpala
`claude -p "/loupedeck-claude-code"` TYLKO gdy brakuje profilu na tej maszynie.
- Windows: Task Scheduler, trigger "On an event" (Microsoft-Windows-DriverFrameworks-UserMode, ID 2003)
  lub skrypt PowerShell z `Register-WmiEvent Win32_DeviceChangeEvent`.
- macOS: LaunchAgent z `WatchPaths` nie zadziała dla USB — użyj Hammerspoon `hs.usb.watcher`
  albo prostego LaunchAgent `StartInterval 30` sprawdzającego `system_profiler`.
Vendor ID Loupedeck znajdź z listy USB (sekcja 0, pkt 3) — nie zakładaj z góry.
