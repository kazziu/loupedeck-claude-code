"""Generuje profil Loupedeck CT "Claude Code" dla Logi Plugin Service 6.x.

Uzycie:
  python gen_profile.py --os win --out <katalog_wyjsciowy> [--prompts prompts.txt] [--wheel-plugin]

Tworzy w <out>:
  app/ApplicationInfo.json + app/Profiles/<GUID>/ProfileInfo.json + ActionIcons/*.ict
                                                                   (do skopiowania do Applications/Loupedeck20/)
  claude-code-<os>.lp5                                             (do recznego importu)
Wszystkie identyfikatory sa deterministyczne (uuid5), wiec ponowne uruchomienie nadpisuje ten sam profil.
--wheel-plugin: na kole maskotka-tamagotchi z wtyczki ClaudeMascot (musi byc zainstalowana).
--target default: zamiast osobnej aplikacji terminala profil dla domyslnej aplikacji systemu
  (@_defaultwin / @_defaultmac), wynik w <out>/default/<GUID>/; instalator ustawia go jako domyslny.
"""
import argparse, base64, json, os, sys, uuid, zipfile, datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "art"))
import pixelart  # noqa: E402

DEVICE = "Loupedeck20"  # Loupedeck CT
NS = uuid.UUID("6f1c2d4e-9a7b-4c1d-8e2f-3a4b5c6d7e8f")
MODE = "main"

def gid(*parts):
    return uuid.uuid5(NS, "|".join(parts)).hex.upper()

# Nazwy klawiszy z tabeli UI Loupedecka (configui2/app.asar): Back, Return, Escape, Tab, Space,
# Minus, Equals, Key0-9, KeyA-Z, ArrowUp/Down/Left/Right. Modyfikatory: ControlOrCommand (Ctrl / Cmd),
# Control (prawdziwy Ctrl takze na Macu), AltOrOption, Shift, Windows.
DISPLAY = {"ControlOrCommand": "Ctrl", "Control": "Ctrl", "AltOrOption": "Alt", "Shift": "Shift",
           "Back": "Backspace", "Equals": "=", "Minus": "-"}

class Builder:
    def __init__(self, os_name, layout_id):
        self.os, self.layout = os_name, layout_id
        self.macros, self.adjustments = [], []
        self.icons = {}  # actionId -> (nazwa ikony z pixelart.TILE_NAMES, podpis)

    def key(self, combo):
        parts = combo.split("+")
        disp = "+".join(DISPLAY.get(p, p[3:] if p.startswith("Key") and len(p) == 4 else p) for p in parts)
        return f"{combo}___{self.layout}___{disp}___"

    def _cmd(self, owner, i, template, params):
        return {"$type": "Loupedeck.Service.MacroActionEditorCommand, LoupedeckService",
                "name": gid(owner, str(i)), "templateName": template,
                "actionParameters": {"$type": "System.Collections.Generic.Dictionary`2[[System.String, System.Private.CoreLib],[System.String, System.Private.CoreLib]], System.Private.CoreLib", **params}}

    def _steps(self, owner, steps):
        """steps: ('key', 'Ctrl+...') | ('text', '...') | ('sleep', ms) -> (editorCommands, actions)"""
        cmds, actions = [], []
        for i, (kind, val) in enumerate(steps):
            if kind == "sleep":
                actions.append(f"$@Generic___@Sleep___{val}")
                continue
            if kind == "key":
                c = self._cmd(owner, i, "$@Generic___@KeyboardKey", {"keyboardKey": self.key(val)})
            else:
                c = self._cmd(owner, i, "$@Generic___@SendText", {"text": val, "useClipboard": "false"})
            cmds.append(c); actions.append(c["name"])
        return cmds, actions

    def icon(self, action_id, icon, label):
        if icon:
            self.icons[action_id] = (icon, label)
        return action_id

    def macro(self, label, *steps, group="Claude Code", icon=None):
        name = gid("macro", label, json.dumps(steps))
        cmds, actions = self._steps(name, steps)
        self.macros.append({"$type": "Loupedeck.Service.ApplicationProfileMacroCommand, LoupedeckService",
            "isCommand": True, "name": name, "displayName": label, "description": "", "groupName": group,
            "superGroupName": "@macro", "supportedOs": "All", "supportedModes": [MODE], "showAsSingleAction": False,
            "actionEditorCommands": cmds, "isMultiState": False, "actions": actions})
        return self.icon(f"$@Generic___@Macro___{name}", icon, label)

    def text_enter(self, label, text, icon=None):
        return self.macro(label, ("text", text), ("sleep", 80), ("key", "Return"), icon=icon)

    def dial(self, label, left, right, group="Claude Code", icon=None):
        name = gid("adj", label, left, right)
        cmds, la = self._steps(name + "L", [("key", left)])
        cmds2, ra = self._steps(name + "R", [("key", right)])
        self.adjustments.append({"$type": "Loupedeck.Service.ApplicationProfileMacroAdjustment, LoupedeckService",
            "isCommand": False, "name": name, "displayName": label, "description": "", "groupName": group,
            "superGroupName": None, "supportedOs": "All", "supportedModes": [MODE], "showAsSingleAction": False,
            "actionEditorCommands": cmds + cmds2, "actionsBefore": [], "actionsLeft": la, "actionsRight": ra,
            "actionsReset": [], "clickRateLimit": 9})
        return self.icon(f"$@Generic___@MacroAdjustment___{name}", icon, label)


def ict(icon, caption):
    """Szablon ikony Loupedecka (.ict): pixel art + podpis. Wspolrzedne area sa w procentach kafelka."""
    return {"backgroundColor": 4278190080, "items": [
        {"image": base64.b64encode(pixelart.tile_png(icon)).decode(), "imageFileName": f"{icon}.png",
         "imageColor": 4294967295, "imageRotation": "None", "isVisible": True, "itemType": "Image",
         "area": {"x": 12, "y": 0, "width": 76, "height": 76}},
        {"text": caption.replace("\n", " "), "originalText": None, "textColor": 4294967295,
         "fontSize": 4, "fontName": "Arial", "isVisible": True, "itemType": "Text",
         "area": {"x": 0, "y": 76, "width": 100, "height": 24}}]}


def button(press=None, fn=None):
    return {"$type": "Loupedeck.Service.ProfileLayoutButton, LoupedeckService", "pressAction": press, "fnPressAction": fn}

def encoder(press=None, rotate=None):
    return {"$type": "Loupedeck.Service.ProfileLayoutEncoder, LoupedeckService", "pressAction": press,
            "fnPressAction": None, "rotateAction": rotate, "fnRotateAction": None}

def page(kind, name, display, controls):
    t = "ProfileLayoutEncoderPage" if kind == "enc" else "ProfileLayoutButtonPage"
    return {"$type": f"Loupedeck.Service.{t}, LoupedeckService", "name": name, "displayName": display,
            "description": None, "controls": controls, "dynamicPageName": None, "dynamicPagePluginName": None,
            "dynamicPageNumber": 0}


def load_prompts(path):
    """prompts.txt: `Etykieta | tekst promptu | ikona` (ikona opcjonalna, nazwa z pixelart.TILE_NAMES)."""
    out = []
    if path and os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            parts = [s.strip() for s in line.split("|")]
            icon = parts[2] if len(parts) > 2 and parts[2] in pixelart.TILE_NAMES else "explain"
            out.append((parts[0].replace("\\n", "\n"), parts[1], icon))
    return out[:10]  # 11. kafelek = git diff, 12. = powrot na strone 1


def build(os_name, prompts, wheel_plugin=False, target="app"):
    global MODE
    win = os_name == "win"
    default = target == "default"
    MODE = "System" if default else "main"  # tryb domyslnej aplikacji DefaultWin to "System"
    b = Builder(os_name, "68486165" if win else "0")
    CTRL = "Control"            # prawdziwy Ctrl (Ctrl+C, Ctrl+U, Ctrl+_) na obu systemach
    MOD2 = "ControlOrCommand"   # Ctrl na Windows, Cmd na Macu

    # Przyciski okragle 1-8 -> zakladki terminala
    if win:   # Windows Terminal: domyslne Ctrl+Alt+1..8 = switchToTab index 0..7
        tab = lambda n: f"ControlOrCommand+AltOrOption+Key{n}"
        nxt, prv = "ControlOrCommand+AltOrOption+ArrowRight", "ControlOrCommand+AltOrOption+ArrowLeft"
    else:     # iTerm2 / Ghostty: Cmd+1..8
        tab = lambda n: f"ControlOrCommand+Key{n}"
        nxt, prv = "ControlOrCommand+Shift+Oem6", "ControlOrCommand+Shift+Oem4"
    round_ctrls = [button(b.macro(f"Sesja {n}", ("key", tab(n)), group="Sesje")) for n in range(1, 9)]

    enter = b.macro("Enter", ("key", "Return"))
    p1 = [
        b.text_enter("Compact", "/compact", "compact"),
        b.text_enter("Clear", "/clear", "clear"),
        b.text_enter("Model", "/model", "model"),
        b.text_enter("Resume", "/resume", "resume"),
        b.macro("Plan", ("key", "Shift+Tab"), icon="plan"),
        b.macro("Stop", ("key", "Escape"), icon="stop"),
        b.macro("Kill", ("key", f"{CTRL}+KeyC"), icon="kill"),
        b.text_enter("git\nstatus", "!git status", "git_status"),
        b.text_enter("Remote", "/remote-control", "remote"),
        b.text_enter("Nowa\nsesja", "claude", "new"),
        b.text_enter("Kontynuuj", "claude -c", "continue"),
        b.icon("$@Generic___@NextTouchPage", "next", "Dalej"),
    ]
    p2 = [b.text_enter(label, text, icon) for label, text, icon in prompts]
    p2 += [None] * (10 - len(p2))
    p2 += [b.text_enter("git\ndiff", "!git diff --stat", "git_diff"),
           b.icon("$@Generic___@PreviousTouchPage", "prev", "Wstecz")]

    # Kwadratowe (indeksy jak w fabrycznych profilach CT): 1 Undo, 3 Enter, 4 Save, 6/7/9/10 strzalki, 11 wolny
    sq = [button() for _ in range(12)]
    sq[1] = button(b.macro("Undo", ("key", f"{CTRL}+Shift+Minus")))
    sq[3] = button(enter, b.macro("Spacja", ("key", "Space")))
    sq[4] = button(b.text_enter("Save\nwip", '!git add -A && git commit -m "wip"'))
    sq[6] = button(b.macro("Gora", ("key", "ArrowUp")))
    sq[7] = button(b.macro("Lewo", ("key", "ArrowLeft")))
    sq[9] = button(b.macro("Dol", ("key", "ArrowDown")))
    sq[10] = button(b.macro("Prawo", ("key", "ArrowRight")))
    sq[11] = button(b.macro("Backspace", ("key", "Back")), b.macro("Skasuj\nlinie", ("key", f"{CTRL}+KeyU")))

    enc = [
        encoder(None, b.dial("Zakladki", prv, nxt, icon="tabs")),
        encoder(b.macro("Font reset", ("key", f"{MOD2}+Key0")),
                b.dial("Font", f"{MOD2}+Minus", f"{MOD2}+Equals", icon="font")),
        encoder("$DefaultWin___ResetVolume", "$DefaultWin___Volume") if win else encoder(),
        encoder(), encoder(), encoder(),
    ]

    if wheel_plugin:  # WheelToolClawd z wtyczki ClaudeMascot: pelny ekran, sam obsluguje dotyk i obrot
        # Bez prefiksu usluga szuka szablonu tylko w PluginApi, w sobie i we wtyczce NATYWNEJ profilu
        # (PluginManager.CreateWheelTool); "<wtyczka>___<klasa>" kieruje ja do naszej wtyczki.
        wheel = {"templateName": "ClaudeMascot___WheelToolClawd", "actions": "", "adjustment": ""}
    else:
        wheel = {"templateName": "WheelToolAnalogClock", "actions": enter, "adjustment": "$@Generic___@MouseWheel"}

    tp1, tp2, ep, wp, ws = (gid(x) for x in ("touch1", "touch2", "enc1", "wheel1", "ws1"))
    rp, sp = gid("round"), gid("square")
    mode = {"$type": "Loupedeck.Service.ProfileLayoutMode20, LoupedeckService", "deviceType": DEVICE,
        "modeName": MODE, "parentModeName": None, "actions": None, "dynamicButtonPages": None, "dynamicEncoderPages": None,
        "touchPages": [page("btn", tp1, "Claude Code", [button(a) for a in p1]),
                       page("btn", tp2, "Prompty", [button(a) for a in p2])],
        "encoderPages": [page("enc", ep, "Claude Code", enc)],
        "wheelPages": [{"$type": "Loupedeck.Service.ProfileLayoutWheelPage, LoupedeckService", "name": wp,
            "displayName": "Clawd" if wheel_plugin else "Scroll", "description": None,
            "templateName": wheel["templateName"],
            "parameters": {"$type": "Loupedeck.StringDictionaryNoCase, PluginApi",
                           "actions": wheel["actions"], "adjustment": wheel["adjustment"]}}],
        "workspaces": [{"$type": "Loupedeck.Service.ProfileLayoutWorkspace20, LoupedeckService", "name": ws,
            "displayName": "Claude Code", "description": None, "touchPageNames": [tp1, tp2],
            "encoderPageNames": [ep], "wheelPageNames": [wp], "activationActions": []}],
        "homeWorkspaceName": ws}

    if default:
        app = "@_defaultwin" if win else "@_defaultmac"
        prof_name = gid("profile", os_name, "default")
        plugins = ["ClaudeMascot"] if wheel_plugin else []
    else:
        app = "windowsterminal" if win else "iterm2"
        prof_name = gid("profile", os_name)
        plugins = (["DefaultWin"] if win else []) + (["ClaudeMascot"] if wheel_plugin else [])
    profile = {"$type": "Loupedeck.Service.ApplicationProfile, LoupedeckService", "name": prof_name,
        "profileFlags": "None", "displayName": "Claude Code", "description": "Generated by loupedeck-claude-code skill",
        "deviceType": DEVICE, "applicationName": app,
        "nativePluginName": ("DefaultWin" if win else "DefaultMac") if default else None, "hasNativePlugin": default,
        "additionalNativePluginNames": plugins,
        "lastModifiedTimeUtc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.0000000Z"),
        "profileSettings": {"$type": "Loupedeck.DictionaryNoCase`1[[System.String, System.Private.CoreLib]], PluginApi"},
        "actionImages90": None, "actionImages60": None, "wheelImages": None, "actionColors": None,
        "layout": {"$type": "Loupedeck.Service.ProfileLayout20, LoupedeckService", "deviceType": DEVICE,
            "profileFlags": "None", "layoutModes": [mode],
            "roundPage": page("btn", rp, "", round_ctrls), "squarePage": page("btn", sp, "", sq)},
        "macroCommands": b.macros, "macroAdjustments": b.adjustments, "profileCommands": [],
        "profileAdjustments": [], "conversionHistory": "", "packageName": None, "packageVersion": None,
        "profileActions": []}
    appinfo = {"$type": "Loupedeck.Service.SupportedApplicationInfo, LoupedeckService", "name": app,
        "displayName": "Windows Terminal" if win else "iTerm2", "description": None, "deviceType": DEVICE,
        "nativePluginName": None, "hasNativePlugin": False, "processOrBundleName": app if win else "com.googlecode.iterm2",
        "modes": [{"$type": "Loupedeck.Service.ApplicationMode, LoupedeckService", "name": MODE,
                   "parentModeName": None, "displayName": "Main"}],
        "defaultProfileName": prof_name, "isEnabled": True}
    icons = {aid: ict(icon, label) for aid, (icon, label) in b.icons.items()}
    return app, prof_name, appinfo, profile, icons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--os", choices=["win", "mac"], required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompts")
    ap.add_argument("--wheel-plugin", action="store_true")
    ap.add_argument("--target", choices=["app", "default"], default="app")
    a = ap.parse_args()
    app, prof, appinfo, profile, icons = build(a.os, load_prompts(a.prompts), a.wheel_plugin, a.target)
    if a.target == "default":
        pdir = os.path.join(a.out, "default", prof)
        os.makedirs(os.path.join(pdir, "ActionIcons"), exist_ok=True)
        dump = lambda o: json.dumps(o, indent=2, ensure_ascii=False)
        open(os.path.join(pdir, "ProfileInfo.json"), "w", encoding="utf-8").write(dump(profile))
        for aid, data in icons.items():
            open(os.path.join(pdir, "ActionIcons", aid + ".ict"), "w", encoding="utf-8").write(dump(data))
        print(json.dumps({"app": app, "profile": prof, "profiledir": pdir, "icons": len(icons)}))
        return
    appdir = os.path.join(a.out, "app")
    pdir = os.path.join(appdir, "Profiles", prof)
    os.makedirs(os.path.join(pdir, "ActionIcons"), exist_ok=True)
    dump = lambda o: json.dumps(o, indent=2, ensure_ascii=False)
    open(os.path.join(appdir, "ApplicationInfo.json"), "w", encoding="utf-8").write(dump(appinfo))
    open(os.path.join(pdir, "ProfileInfo.json"), "w", encoding="utf-8").write(dump(profile))
    for aid, data in icons.items():
        open(os.path.join(pdir, "ActionIcons", aid + ".ict"), "w", encoding="utf-8").write(dump(data))
    lp5 = os.path.join(a.out, f"claude-code-{a.os}.lp5")
    with zipfile.ZipFile(lp5, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("ApplicationInfo.json", dump(appinfo))
        z.writestr("ProfileInfo.json", dump(profile))
        for aid, data in icons.items():
            z.writestr(f"ActionIcons/{aid}.ict", dump(data))
        z.writestr("metadata/LoupedeckPackage.yaml",
                   f"type: Profile5\nname: {prof}\ndisplayName: Claude Code\nversion: 1.0.0.0\n")
    print(json.dumps({"app": app, "profile": prof, "appdir": appdir, "lp5": lp5, "icons": len(icons),
                      "macros": len(profile["macroCommands"]), "dials": len(profile["macroAdjustments"])}))


if __name__ == "__main__":
    main()
