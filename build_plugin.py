"""Buduje paczke wtyczki ClaudeMascot (tamagotchi na kole CT).

Uzycie: python build_plugin.py --out ~/.config/loupedeck-cc/build-plugin
Wynik: <out>/ClaudeMascot/{metadata/, win/ClaudeMascotPlugin.dll, frames/*.png}
Wymaga .NET SDK w wersji zgodnej z hostem (Logi Plugin Service 6.4 = .NET 10).
"""
import argparse, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "art"))
import pixelart  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pkg = os.path.join(a.out, "ClaudeMascot")
    shutil.rmtree(pkg, ignore_errors=True)
    os.makedirs(os.path.join(pkg, "metadata"))

    frames = os.path.join(HERE, "plugin", "frames")  # wbudowywane w DLL jako EmbeddedResource
    shutil.rmtree(frames, ignore_errors=True)
    pixelart.export_wheel(frames)

    binout = os.path.join(a.out, "bin")
    subprocess.run(["dotnet", "build", os.path.join(HERE, "plugin", "ClaudeMascotPlugin.csproj"), "-c", "Release",
                    "-o", binout, "-v", "q", "-nologo"], check=True,
                   env={**os.environ, "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"})
    os.makedirs(os.path.join(pkg, "win"))
    shutil.copy(os.path.join(binout, "ClaudeMascotPlugin.dll"), os.path.join(pkg, "win"))

    shutil.copy(os.path.join(HERE, "plugin", "LoupedeckPackage.yaml"), os.path.join(pkg, "metadata"))
    icon = pixelart.wheel_frame("happy", 3).image(5, bg=(0, 0, 0, 255)).resize((256, 256), pixelart.Image.NEAREST)
    icon.save(os.path.join(pkg, "metadata", "Icon256x256.png"))
    print(pkg)


if __name__ == "__main__":
    main()
