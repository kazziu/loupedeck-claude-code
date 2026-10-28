<p align="center">
  <img src="docs/img/hero.png" alt="Loupedeck CT z profilem Claude Code i tamagotchi Clawd na kole" width="100%">
</p>

<h1 align="center">Loupedeck CT × Claude Code</h1>

<p align="center">
  <b>Loupedeck CT jako pulpit sterujący do Claude Code</b>: ręcznie zakodowane kafelki pixel art,<br>
  a na dużym kole pixelowe tamagotchi, które reaguje na to, co robi Claude.
</p>

<p align="center">
  <a href="README.md">English</a> · <a href="README.de.md">Deutsch</a> · <b>Polski</b>
</p>

---

## Co dostajesz

| | |
|---|---|
| **12 + 12 kafelków dotykowych** | `/compact`, `/clear`, `/model`, `/resume`, `/remote-control`, tryb planu, Esc, Ctrl+C, `git status`, nowa sesja, `claude -c` i druga strona z Twoimi promptami. |
| **8 przycisków okrągłych** | Skok prosto do sesji Claude Code 1–8. Działa ze ścianą osobnych okien terminala (numerowanych tak, jak się czyta ekran: od górnego rzędu, od lewej do prawej) i z zakładkami w jednym oknie. Fn + przycisk zawsze przełącza zakładki. |
| **Pokrętła** | Poprzednia/następna zakładka, rozmiar czcionki terminala, głośność. |
| **Duże koło** | Clawd, tamagotchi mieszkające na okrągłym ekranie. Obrót koła nadal przewija terminal. |
| **Hooki Claude Code** | Clawd pisze na laptopie, gdy Claude pracuje. Gdy Claude czeka na Ciebie, macha, pokazuje `!` i **koło wibruje**. Świętuje koniec zadania i poci się, gdy narzędzie zawiedzie. |
| **3 języki** | Podpisy po angielsku, niemiecku albo po polsku. Komendy Claude Code zostają pod prawdziwymi nazwami. |
| **Wszystko jest kodem** | Profil, każda ikona i każda klatka animacji powstają ze skryptów. Wszystko da się przebudować, zmienić i wersjonować. |

<table>
  <tr>
    <td align="center" width="62%"><img src="docs/img/loupedeck-app.png" alt="Prawdziwy zrzut profilu w aplikacji Loupedeck"><br>
      <sub><b>Na żywo</b>. W jednej sesji właśnie wywaliło się narzędzie, więc Clawd ma oczy X i krople potu.<br>Dwie kropki pod nim to dwie sesje Claude Code, które dalej pracują.</sub></td>
    <td align="center"><img src="docs/img/wheel.gif" alt="Animacje Clawda" width="240"><br>
      <sub>Wszystkie animacje koła, rysowane piksel po pikselu w <code>art/pixelart.py</code>.</sub></td>
  </tr>
</table>

## Clawd, tamagotchi na kole

<p align="center"><img src="docs/img/states.png" alt="Wszystkie stany maskotki" width="100%"></p>

| Ty | Clawd |
|---|---|
| dotykasz koła | daje się pogłaskać (serduszka). Jeśli jest głodny, zjada ciastko. |
| dotykasz dwa razy | tańczy |
| przytrzymujesz | koło wysyła **Enter** (dawna funkcja koła) |
| kręcisz kołem | koło przewija terminal; za szybko i Clawdowi kręci się w głowie |
| zostawiasz go na 3 min | zasypia |
| zapominasz o nim na ok. 45 min | robi się głodny (dymek z ciastkiem) |

| Claude Code (przez hooki) | Clawd |
|---|---|
| wysyłasz prompt / działa narzędzie | pisze na laptopie |
| pytanie o zgodę, pytanie do Ciebie, bezczynność | macha, pokazuje `!`, **koło wibruje** |
| narzędzie się wywala | oczy X, krople potu, trzęsie się |
| `/compact` | zostaje zgnieciony |
| koniec tury (`Stop`) | skacze, konfetti |
| start sesji | mówi HI |

Kropki na dole koła pokazują, ile sesji pracuje (pomarańczowe) albo czeka na Ciebie (migające żółte), maksymalnie 8.

## Wymagania

- **Loupedeck CT** i **Logi Plugin Service 6.x** (aktualne oprogramowanie Loupedecka). Testowane na 6.4.1 i Windows 11.
- **Claude Code** w Windows Terminal (natywnie albo w WSL). Na macOS docelowo iTerm2 / Ghostty, ale wersja na Maca nie jest jeszcze przetestowana (patrz [macOS](#macos)).
- **Python 3.9+** z Pillow (`pip install pillow`) do generatorów.
- **.NET 10 SDK** do zbudowania wtyczki koła. Logi Plugin Service 6.4 działa na .NET 10, więc .NET 8 nie wystarczy.

## Instalacja

Repo jest [skillem Claude Code](https://docs.claude.com/en/docs/claude-code/skills). Najprościej, gdy zrobi to Claude:

```bash
git clone https://github.com/kazziu/loupedeck-claude-code ~/.claude/skills/loupedeck-claude-code
```

a potem w Claude Code:

```
/loupedeck-claude-code
```

Skill sprawdza system, terminal i instalację Loupedecka oraz pyta o język. Potem buduje wtyczkę, generuje profil, instaluje wszystko (z kopiami zapasowymi) i prowadzi Cię przez dwuminutowy test na urządzeniu.

<details>
<summary><b>Instalacja ręczna (Windows)</b></summary>

```powershell
$SK = "$HOME\.claude\skills\loupedeck-claude-code"; $C = "$HOME\.config\loupedeck-cc"
mkdir $C -Force; Copy-Item "$SK\docs\prompts.pl.txt" "$C\prompts.txt"

python "$SK\build_plugin.py" --out "$C\build-plugin"                       # wymaga dotnet 10
python "$SK\gen_profile.py" --os win --out "$C\build-win" --prompts "$C\prompts.txt" --lang pl --wheel-plugin
python "$SK\gen_profile.py" --os win --out "$C\build-win" --prompts "$C\prompts.txt" --lang pl --wheel-plugin --target default
powershell -File "$SK\install_win.ps1" -Build "$C\build-win" -Plugin "$C\build-plugin\ClaudeMascot" -MakeDefault

python "$SK\hooks\install_hooks.py"                                        # opcjonalnie: hooki Claude Code
```

Windows Terminal ma domyślnie `Ctrl+Alt+1…8` na zakładki. Pod pokrętło „Zakładki” dopisz `nextTab` / `prevTab` na `ctrl+alt+right` / `ctrl+alt+left` z `"tabSwitcherMode": "disabled"`.
</details>

<details>
<summary><b>Co zmienia się na komputerze</b></summary>

| Gdzie | Co | Jak cofnąć |
|---|---|---|
| `%LOCALAPPDATA%\Logi\LogiPluginService\Applications\Loupedeck20\windowsterminal` | profil, który przełącza się z Windows Terminal | usuń folder |
| `…\Loupedeck20\@_defaultwin\Profiles\<GUID>` + `ApplicationInfo.json` | ten sam profil jako domyślny na CT (z `-MakeDefault`); stary domyślny zostaje | wybierz stary profil w aplikacji Loupedeck |
| `…\LogiPluginService\Plugins\ClaudeMascot` | wtyczka koła | usuń folder |
| `~/.claude/settings.json` → `hooks` | 15 asynchronicznych hooków zapisujących `~/.config/loupedeck-cc/sessions/*.json` | `python hooks/install_hooks.py --remove` |
| `~/.config/loupedeck-cc/backup-*` | kopie zapasowe przed każdą instalacją | |
</details>

## Dostosowanie

- **Twoje prompty (strona 2):** edytuj `~/.config/loupedeck-cc/prompts.txt`. Każda linia ma postać `Etykieta | tekst promptu | ikona`. Potem uruchom skill jeszcze raz.
- **Język:** `--lang en|de|pl` albo `{"lang": "pl"}` w `~/.config/loupedeck-cc/config.json`. Tłumaczenia są w `LABELS` w `gen_profile.py`, więc nowy język to jeden słownik.
- **Mapa przycisków:** źródłem prawdy jest `gen_profile.py`. Każdy kafelek to jedna linia, np. `b.text_enter("Compact", "/compact", "compact")`.
- **Ikony i animacje:** `art/pixelart.py`. Każda ikona to mała funkcja na siatce 20×20, a każdy stan koła to funkcja na siatce 40×40. Polecenie `python art/render_docs.py` renderuje podgląd całości do PNG/GIF.

## Jak to działa

```
gen_profile.py ──► ProfileInfo.json + ActionIcons/*.ict ──► Logi Plugin Service ──► kafelki, przyciski, pokrętła
art/pixelart.py ─┬► ikony kafelków (PNG w base64 wewnątrz .ict)
                 └► klatki koła ──► plugin/ (C#, .NET 10) ──► WheelToolClawd rysuje 240×240 na kole
hooki Claude Code ──► hooks/mascot_hook.py ──► ~/.config/loupedeck-cc/sessions/*.json ──► wtyczka czyta co ~1 s
```

Format profili Loupedecka nie jest udokumentowany. Wszystko tutaj powstało z analizy profili
dołączonych do oprogramowania, paczki interfejsu konfiguracyjnego i kodu IL samej usługi.
Notatki są w **[docs/loupedeck-format.md](docs/loupedeck-format.md)** (po angielsku). Jeśli robisz
cokolwiek dla Loupedecka / Logi Plugin Service, zacznij od nich; oszczędzisz dzień pracy.

Najważniejsze:

- Profile to zwykły JSON (`ProfileInfo.json`). `Loupedeck20` = CT, `30` = Live, `50` = Live S.
- Kroki makr używają `$@Generic___@KeyboardKey` z `"<Mod+Klawisz>___<keyboardLayoutId>___<etykieta>___"` oraz `$@Generic___@SendText`. Nazwy klawiszy (`Back`, `Return`, `Minus`, `Equals`, `Key0`…) pochodzą z tabeli w interfejsie konfiguracyjnym.
- Ikony kafelków to pliki `.ict` (JSON: PNG w base64 + podpis, współrzędne w procentach) nazwane identyfikatorem akcji.
- **Koło na pełny ekran:** dziedziczysz po `WheelTool` we wtyczce i podajesz w profilu `templateName: "<NazwaWtyczki>___<Klasa>"`. Bez prefiksu usługa szuka tylko we wtyczce *natywnej* profilu i koło zostaje martwe.
- Usługa wczytuje DLL wtyczek z pamięci, więc `Assembly.Location` jest puste. Zasoby trzeba wbudować w DLL.
- Nawet „uniwersalna” wtyczka potrzebuje klasy dziedziczącej po `ClientApplication`, inaczej loader jej nie przyjmie.

## macOS

Generator ma gałąź `mac` (`⌘1…8` dla zakładek iTerm2 / Ghostty, `@_defaultmac`), ale nie była jeszcze
testowana na Macu. Do zrobienia: `install_mac.sh` na wzór `install_win.ps1`, przewijanie przez CGEvent
we wtyczce (dziś używa `user32`) oraz sprawdzenie ścieżek profili i SDK. Skill mówi Claude'owi
dokładnie, co sprawdzić. PR mile widziane.

## Problemy

| Objaw | Rozwiązanie |
|---|---|
| Koło czarne / martwe | `templateName` koła musi być `ClaudeMascot___WheelToolClawd`. Sprawdź `%LOCALAPPDATA%\Logi\LogiPluginService\Logs\plugin_logs\ClaudeMascot.log`. |
| `Cannot load plugin … already loaded` w logu | To normalne: usługa skanuje wtyczki dwa razy. |
| Wtyczka na liście wyłączonych | Zrestartuj usługę. Lista wyłączonych żyje tylko w pamięci. |
| Wpisywany tekst gubi znaki | Zwiększ krok `("sleep", 80)` w `text_enter` w `gen_profile.py`. |
| Maskotka nie reaguje na Claude'a | Uruchom `python hooks/install_hooks.py`, zacznij nową sesję Claude Code i sprawdź, czy w `~/.config/loupedeck-cc/sessions/` pojawiają się pliki. |

## Autorzy i zastrzeżenia

Nieoficjalny projekt fanowski, niezwiązany z Anthropic ani Logitech i przez nie niepopierany.
*Claude* i *Claude Code* to znaki towarowe Anthropic. *Loupedeck* i *Logi* to znaki towarowe Logitech.
Maskotka to fan art narysowany od zera w Pythonie, piksel po pikselu.

Zrobione w jednej długiej, przyjemnej sesji przez [@kazziu](https://github.com/kazziu) razem z Claude Code.

[Licencja MIT](LICENSE)
