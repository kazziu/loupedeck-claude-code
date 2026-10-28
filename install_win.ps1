# Installs the generated profile (and optionally the ClaudeMascot plugin) into Logi Plugin Service on Windows.
# Usage: powershell -File install_win.ps1 -Build <build-win dir> [-Plugin <ClaudeMascot dir>] [-MakeDefault]
#   -MakeDefault: copies <Build>\default\<GUID> to @_defaultwin and makes it the CT default profile
#                 (the previous default profile is kept; pick it again in the Loupedeck app to go back).
param([Parameter(Mandatory)] [string]$Build, [string]$Plugin, [switch]$MakeDefault)
$ErrorActionPreference = "Stop"
$lps = "$env:LOCALAPPDATA\Logi\LogiPluginService"
$exe = "C:\Program Files\Logi\LogiPluginService\LogiPluginService.exe"
$dst = "$lps\Applications\Loupedeck20\windowsterminal"
$defApp = "$lps\Applications\Loupedeck20\@_defaultwin"
$bk = "$env:USERPROFILE\.config\loupedeck-cc\backup-$(Get-Date -Format yyyyMMdd-HHmmss)"
New-Item -ItemType Directory -Force $bk | Out-Null
if (Test-Path $dst) { Copy-Item $dst "$bk\windowsterminal" -Recurse }
if ($Plugin -and (Test-Path "$lps\Plugins\ClaudeMascot")) { Copy-Item "$lps\Plugins\ClaudeMascot" "$bk\ClaudeMascot" -Recurse }
if ($MakeDefault) { Copy-Item "$defApp\ApplicationInfo.json" "$bk\defaultwin-ApplicationInfo.json" }

Get-Process Loupedeck, LogiPluginService, LogiPluginServiceExt -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 3

if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
Copy-Item "$Build\app" $dst -Recurse
if ($Plugin) {
    $pd = "$lps\Plugins\ClaudeMascot"
    if (Test-Path $pd) { Remove-Item $pd -Recurse -Force }
    Copy-Item $Plugin $pd -Recurse
}
if ($MakeDefault) {
    $src = Get-ChildItem "$Build\default" -Directory | Select-Object -First 1
    $pdst = "$defApp\Profiles\$($src.Name)"
    if (Test-Path $pdst) { Remove-Item $pdst -Recurse -Force }
    Copy-Item $src.FullName $pdst -Recurse
    $infoPath = "$defApp\ApplicationInfo.json"
    $info = Get-Content $infoPath -Raw
    $info = $info -replace '"defaultProfileName":\s*"[^"]*"', ('"defaultProfileName": "' + $src.Name + '"')
    [IO.File]::WriteAllText($infoPath, $info, (New-Object Text.UTF8Encoding $false))
}
Start-Process $exe
"backup: $bk"
"installed: $dst" + $(if ($Plugin) { " + plugin" } else { "" }) + $(if ($MakeDefault) { " + default profile" } else { "" })
