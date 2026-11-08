# SuperLauncherMC

🎮 A lightweight, telemetry-free Minecraft launcher for Arch Linux (and beyond).

**No ads. No tracking. No Electron. Just PyQt6 and ~150 MB of RAM.**

> "We don’t make software. We make statements."

![SuperLauncherMC screenshot](assets/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0_20261108_211006.png)

## Install (Arch Linux)

You can grab the package straight from the Arch User Repository (AUR):

```bash
yay -S superlauncher
# or
paru -S superlauncher
```

### Other Distributions
Clone the repo and run it directly via Python (Requires Python 3.10+ and PyQt6):
```bash
git clone https://github.com
cd SuperLauncherMC-for-linux
pip install -r requirements.txt
python -m superlauncher
```

## Why?
Most Minecraft launchers today are absolute trash:
* **Bloated Electron apps** (Lunar, Feather) that hog your system resources.
* **Packed with malware and telemetry** (TLauncher) that track your background data.
* **Overcomplicated setups** that force you into manual Java path configurations.

SuperLauncherMC is different. It's built independently from the ground up to be blazing fast, entirely local, and resource-friendly. It starts in ~0.5s, uses roughly 150 MB of RAM, and strips out corporate tracking. It also builds full-stack dev tools right into your client, allowing you to manage local environments directly from the interface.

## Features
✅ **Zero Telemetry, Zero Ads** — Completely isolated workspace. No trackers, no analytics, no corporate call-backs.

✅ **Native Local Server Orchestration** — Deploy, configure, and manage local Minecraft servers (Paper, Spigot, Forge, Fabric) straight from the GUI. Features automated EULA acceptance, console piping, backups, and MOTD configuration.

✅ **Modrinth & CurseForge Integration** — Direct API integration for clean, one-click mod and modpack installation.

✅ **Full Environment Support** — Out-of-the-box launcher support for Vanilla, Fabric, Forge, Quilt, and OptiFine.

✅ **Account Management** — Secure Microsoft OAuth implementation alongside fully functional offline accounts.

✅ **Client & Asset Automation** — Native auto-updates pipeline for both the launcher core and Minecraft runtimes.

## What's still rough
* **Arch-First Packaging:** The launcher is primarily optimized and engineered on Arch Linux. It works on other distros via Python interpreter scripts, but the seamless packaging is Arch-focused.
* **Brutal UI:** The interface is built to be purely functional and lightweight, not fancy. Startup metrics and memory restrictions were prioritized over smooth UI animations.
* **Distribution Formats:** Flatpak and AppImage wrappers are not implemented yet. They are planned for future deployment cycles.
* **Localization:** The runtime language switch framework (RU ↔ EN) currently has a known bug. A hotfix is actively in progress.

## Tech Stack
* Python 3.10+ / PyQt6
* `minecraft-launcher-lib` for instance environments execution
* Upstream AUR Package: `superlauncher`

## Contributing
Issues and pull requests are highly welcome. If you encounter a runtime crash or process hanging, please open an issue containing:
1. Your Linux distribution and system Python interpreter version.
2. The current launcher build version.
3. Accurate terminal logs or steps to reproduce the bug.

## License
Distributed under the **GPL-3.0 License**. 

Developed by **Ludvig2457** · GitHub Organization: [SuperLauncherMC](https://github.com)
