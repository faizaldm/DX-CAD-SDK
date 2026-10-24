# Installing DX-CAD

DX-CAD&trade; comes four ways: from PyPI for anyone with Python 3.12, and as a
build for each desktop that needs no Python. Each GitHub release carries the
builds. Whichever you take, `dxcad doctor` (or `dxcad.exe doctor` on
Windows) tells you it worked, ending with a line starting `SMOKE OK`.

## With Python

```
pip install dxcad
dxcad doctor
dxcad gui
```

The OpenCASCADE kernel and Qt come with it as pinned dependencies. On Linux
the wheel is a manylinux wheel, which installs on any distribution new enough
for the kernel's own wheel.

## Windows

The release carries `DX-CAD-<version>-windows-x64-setup.exe`, an installer
that adds DX-CAD to the Start menu and opens its part, assembly and drawing
files, and
`DX-CAD-<version>-windows-x64.zip`, a portable build. Unzip that anywhere
and run `DX-CAD.exe` in the `DX-CAD` folder it makes; its `README.txt` says
the same. `dxcad.exe` beside it is the command line, for terminals, scripts
and AI agents: double-clicked, it says so and offers to open DX-CAD.

The portable build registers nothing with Windows, so Explorer shows DX-CAD's
parts, assemblies and drawings with no picture and no icon of their own. The
installer registers them: each type's icon, and a thumbnail of each saved
file, in Explorer's large icons and its preview pane. If Explorer had shown
those files before the install, sign out of Windows and in again once, so it
reads the new types instead of what it kept.

## macOS

The release carries `DX-CAD-<version>-macos.dmg`, for Apple silicon. Open
it and drag DX-CAD into Applications. The build is not signed by Apple yet,
so the first time macOS says it cannot check it for malicious software.
Right-click (or Control-click) DX-CAD in Applications, choose Open, and
then Open in the dialog; macOS remembers the choice. Or, in a terminal,
take the download's quarantine mark off it once:

```text
xattr -dr com.apple.quarantine /Applications/DX-CAD.app
```

## Linux

The release carries `DX-CAD-x86_64.AppImage`, one file that runs on most
64-bit distributions. A download is not executable, so mark it so once,
then run it:

```text
chmod +x DX-CAD-x86_64.AppImage
./DX-CAD-x86_64.AppImage
```

`dxcad associate`, from a pip install, adds the desktop entry and the
part, assembly and drawing file types for your user.

What changed between one version and the next is in the
changelog, whose
section for a new version DX-CAD shows at its first start after an update.
