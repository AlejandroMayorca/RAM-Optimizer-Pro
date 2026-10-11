<div align="center">

<img src="assets/icon.png" width="120" alt="RAM Optimizer Pro">

# RAM Optimizer Pro

**Automatically frees up RAM and keeps Windows fast, without you having to think about it.**

[![Latest release](https://img.shields.io/github/v/release/AlejandroMayorca/RAM-Optimizer-Pro?label=version&color=4FE0C2&style=for-the-badge)](https://github.com/AlejandroMayorca/RAM-Optimizer-Pro/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/AlejandroMayorca/RAM-Optimizer-Pro/total?label=downloads&color=0E9F8A&style=for-the-badge)](https://github.com/AlejandroMayorca/RAM-Optimizer-Pro/releases)
![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0E131D?style=for-the-badge&logo=windows)

### [⬇️ Download for Windows](https://github.com/AlejandroMayorca/RAM-Optimizer-Pro/releases/latest)

Free · No ads · Works offline

[Español](README.md) · **English**

<img src="docs/screenshots/panel.png" width="860" alt="RAM Optimizer Pro dashboard">

</div>

---

## What it does

Over time, Windows and your open apps hold on to memory they aren't using: background browser tabs, games you already closed, stale file cache. **RAM Optimizer Pro** watches your memory around the clock and, when usage spikes, safely frees it so your apps and games get room to breathe again.

It installs in seconds, starts with Windows and works quietly from the system tray.

> The interface is currently in Spanish. An English translation is on the roadmap.

## Features

- **Real-time dashboard** — RAM usage, available memory, system cache and a 5-minute activity chart.
- **Smart auto-clean** — runs only when usage stays above your threshold, and backs off automatically when cleaning isn't paying off.
- **Three cleaning levels**
  - **Quick:** trims the memory of background apps.
  - **Balanced** *(recommended)*: also flushes modified memory and low-priority cache.
  - **Deep:** releases all system and file cache.
- **Scheduled cleaning** — every 15 min, 30 min, 1 h, 2 h or 4 h.
- **Protects what you're using** — never touches the active window (your game, editor or video call) or critical Windows processes.
- **Process manager** — see what uses the most memory, group by app, free or exclude with one click.
- **Starts with Windows, no prompts** — launches minimized at sign-in without UAC pop-ups.
- **System tray** — live RAM percentage next to the clock, quick menu and notifications.
- **History** — how much memory was recovered, when and how.
- **Dark, light or automatic theme.**

<div align="center">
<img src="docs/screenshots/procesos.png" width="420" alt="Process manager">
<img src="docs/screenshots/ajustes.png" width="420" alt="Settings">
</div>

## Installation

1. Download **`RAMOptimizerPro-Setup-3.0.0.exe`** from [Releases](https://github.com/AlejandroMayorca/RAM-Optimizer-Pro/releases/latest).
2. Run it and allow administrator access.
3. Click **Comenzar → Siguiente → Instalar**. Done!

If you already have an older version, the installer upgrades it and keeps your settings.

> **Seeing "Windows protected your PC"?**
> This is normal for new software from independent developers without a paid code-signing certificate. Click **More info → Run anyway**. You can verify the file against the SHA-256 checksum published with each release, or scan it on [VirusTotal](https://www.virustotal.com).

### Requirements

- Windows 10 or 11, 64-bit
- 100 MB of free disk space
- Administrator rights to install

### Uninstall

Go to **Settings → Apps → RAM Optimizer Pro → Uninstall**, or use the Start menu shortcut. The app, shortcuts and startup task are removed.

## FAQ

**Is it safe?**
Yes. It only uses official Windows APIs (`EmptyWorkingSet`, `NtSetSystemInformation`, `SetSystemFileCacheSize`), the same ones used by Microsoft tools such as RAMMap. It never closes programs or touches critical system processes.

**Will my programs close?**
No. Nothing is closed. Only memory that isn't being used at that moment is released.

**Does it collect data?**
No. It never connects to the internet. Settings and history stay on your PC in `%APPDATA%\RAMOptimizerPro`.

**Is it good for gaming?**
Yes, especially on PCs with 8 GB or 16 GB of RAM. *Protect the active app* keeps your running game untouched.

**Why does it need administrator rights?**
Releasing system cache is only possible with elevated privileges. You approve it once during installation; after that the app opens without prompts.

## Feedback and bugs

Found a problem or have an idea? [Open a report here](https://github.com/AlejandroMayorca/RAM-Optimizer-Pro/issues/new/choose). If you like the app, give the repo a ⭐ — it helps more people find it.

---

<div align="center">

Made by **zPcho** · © 2024-2026

</div>
