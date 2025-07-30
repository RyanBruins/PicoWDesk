# 📦 PicoWDesk  
**A tiny, hackable web-desktop for the Raspberry Pi Pico W**

https://github.com/RyanBruins/PicoWDesk  
Licence: MIT

PicoWDesk turns your Pico W into a pocket-sized computer that you control from any browser.  
Everything (desktop, windows, dock, file-manager, games and utilities) is stored **in two files** on the Pico:  
- `main.py` – the MicroPython HTTP server  
- `index.html` – the single-page desktop UI  

Pick one of five ready-made packages, flash MicroPython, copy the files, and you’re done.

---

## 🗂️ Project Layout

```
PicoWDesk/
├── main.py                # MicroPython server & API
├── index.html             # Desktop / Mobile UI
├── config.json            # Wi-Fi, port, restricted files, etc.
├── favicon.ico            # Browser tab icon
├── package-*.sh           # 5 deployment scripts → see below
├── LICENCE.md             # MIT licence
├── docs/
│   ├── DESKTOP.md         # Desktop & Mobile modes, folders, icons
│   ├── NETWORK.md         # Network Configuration Guide for Pico W
│   ├── API.md             # Full HTTP API reference
│   └── INSTALL.md         # Step-by-step flashing & install guide
└── apps/
    ├── system/            # Core management apps (FileManager, Editor, Wi-Fi, reboot)  
    │   └── README.md
    ├── tools/             # Extra utilities (Calc, Browser, Terminal, Chat)  
    │   └── README.md
    └── games/             # Self-contained games (Breakout, Minesweeper, Mineclear)  
        └── README.md
```

---

## 🖥️ Desktop & Mobile Modes

| Mode | Behaviour |
|------|-----------|
| **Desktop** (default) | Draggable windows, resizable, bottom dock |
| **Mobile** | Full-screen apps, top system-bar, hamburger launcher |

[→ Read DESKTOP.md](docs/DESKTOP.md)

---
## 📶 Network Configuration (WiFi)

| Mode | Behaviour |
|------|-----------|
| **AP** (default) | Pico W behaves as Access Point |
| **STA** | Pico W connects to WiFi Network |

[→ Read NETWORK.md](docs/NETWORK.md)

---

## 🌐 RESTful API

| Area | Endpoints |
|------|-----------|
| **Files** | `/api/list`, `/api/read/*`, `/api/write/*`, `/api/upload/*`, `/api/download/*`, `/api/delete/*` |
| **Chat** | `/api/chat/*` |
| **System** | `/api/info`, `/api/scan`, `/api/connect`, `/api/mode/ap`, `/api/restart` |

[→ Read API.md](docs/API.md)

---

## 🚀 Five Ready-Made Packages

| Script | Contents |
|--------|----------|
| `package-base.sh` | **Bare desktop** – only `main.py`, `index.html`, `config.json`, `favicon.ico` |
| `package-system.sh` | Base + **system apps** (FileManager, Editor, Wi-Fi, reboot) grouped under “Settings” |
| `package-tools.sh` | System + **tools** (Calculator, Browser, Terminal, Chat) |
| `package-games.sh` | System + **games** (Breakout, Minesweeper, Mineclear) grouped under “Games” |
| `package-everything.sh` | **All** apps, games, tools in one shot |

Run the script, then flash the resulting `/deploy` folder.

---

## ⚙️ Quick Start

1. **Prerequisites** – Pico W with MicroPython firmware  
2. **Flash** – copy `.uf2` to RPI-RP2 drive  
3. **Copy files** – `cd deploy && mpremote cp -r . :`  
4. **Connect** – browse to `http://192.168.4.1` (AP) or the assigned STA IP  

[→ Full instructions in INSTALL.md](docs/INSTALL.md)

---

## 📄 Licence

MIT – see [LICENCE.md](LICENCE.md)

---

## 🛠️ Hack Away

Fork, add new `.html`/`.ico` files, tweak `config.json`, or extend the REST API.  
Everything is intentionally small and easy to hack — have fun!

---
