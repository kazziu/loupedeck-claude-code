#!/bin/bash
# Installs the generated profile (and optionally the ClaudeMascot plugin) into Logi Plugin Service on macOS.
# Usage: ./install_mac.sh -b <build-mac dir> [-p <ClaudeMascot dir>] [-d]
#   -d: copies <build>/default/<GUID> to @_defaultmac and makes it the CT default profile
#       (the previous default profile is kept; pick it again in the Loupedeck app to go back).
set -euo pipefail
BUILD="" PLUGIN="" MAKE_DEFAULT=0
while getopts "b:p:d" o; do
    case $o in b) BUILD=$OPTARG ;; p) PLUGIN=$OPTARG ;; d) MAKE_DEFAULT=1 ;; *) exit 2 ;; esac
done
[ -n "$BUILD" ] || { echo "usage: $0 -b <build-mac dir> [-p <ClaudeMascot dir>] [-d]" >&2; exit 2; }

LPS="$HOME/Library/Application Support/Logi/LogiPluginService"
APP=/Applications/Utilities/LogiPluginService.app
NAME=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8-sig"))["name"])' "$BUILD/app/ApplicationInfo.json")
DST="$LPS/Applications/Loupedeck20/$NAME"
DEFAPP="$LPS/Applications/Loupedeck20/@_defaultmac"
BK="$HOME/.config/loupedeck-cc/backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BK"
[ -d "$DST" ] && cp -R "$DST" "$BK/$NAME"
[ -n "$PLUGIN" ] && [ -d "$LPS/Plugins/ClaudeMascot" ] && cp -R "$LPS/Plugins/ClaudeMascot" "$BK/ClaudeMascot"
[ $MAKE_DEFAULT = 1 ] && cp -R "$DEFAPP" "$BK/defaultmac"

# The UI and the service both write profiles on exit, so stop them before swapping files.
osascript -e 'quit app "Loupedeck"' 2>/dev/null || true
pkill -x LogiPluginService 2>/dev/null || true
for _ in $(seq 20); do pgrep -x LogiPluginService >/dev/null || break; sleep 0.5; done
pkill -x LogiPluginServiceExt LogiPluginServiceNative 2>/dev/null || true
sleep 1

rm -rf "$DST"
cp -R "$BUILD/app" "$DST"
if [ -n "$PLUGIN" ]; then
    mkdir -p "$LPS/Plugins"
    rm -rf "$LPS/Plugins/ClaudeMascot"
    cp -R "$PLUGIN" "$LPS/Plugins/ClaudeMascot"
fi
if [ $MAKE_DEFAULT = 1 ]; then
    SRC=$(find "$BUILD/default" -mindepth 1 -maxdepth 1 -type d | head -1)
    GUID=$(basename "$SRC")
    rm -rf "$DEFAPP/Profiles/$GUID"
    cp -R "$SRC" "$DEFAPP/Profiles/$GUID"
    python3 - "$DEFAPP/ApplicationInfo.json" "$GUID" <<'EOF'
import re, sys
path, guid = sys.argv[1], sys.argv[2]
text = open(path, encoding="utf-8-sig").read()
open(path, "w", encoding="utf-8").write(re.sub(r'"defaultProfileName":\s*"[^"]*"', f'"defaultProfileName": "{guid}"', text))
EOF
fi
# Start the service through its launch agent: started from a shell (open/exec) it showed the profile but
# ignored every button and the wheel. Then bring the Loupedeck app back, as it was before.
AGENT="$HOME/Library/LaunchAgents/com.logi.pluginservice.launch.plist"
if [ -f "$AGENT" ]; then
    launchctl unload "$AGENT" 2>/dev/null || true
    launchctl load "$AGENT"
else
    open "$APP" --args -noui
fi
open -a Loupedeck
echo "backup: $BK"
echo "installed: $DST$([ -n "$PLUGIN" ] && echo " + plugin")$([ $MAKE_DEFAULT = 1 ] && echo " + default profile")"
