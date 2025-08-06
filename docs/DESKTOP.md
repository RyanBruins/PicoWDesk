## 📄 **DESKTOP.md**  
*Desktop & Mobile Modes, File System Layout, Icons, Restricted Files & System Apps*

---

### 1. Overview  
The **PicoWDesk** desktop is a **single-page browser UI** that runs on a Raspberry Pi Pico W.  
It supports two *runtime* modes:

| Mode | Description | Trigger |
|------|-------------|---------|
| **Desktop** (default) | Classic floating windows, resizable, draggable, dock at bottom | UA string is **NOT** a mobile device |
| **Mobile** | Full-screen apps, top system-bar, hamburger launcher, no resize handles | UA string **IS** a mobile device |

---

### 2. File-System Layout  
All files live in the **root of the Pico** (no sub-directories are supported).  
Typical root after a fresh “System” install:

```
/ (root)
 ├─ main.py               # MicroPython server
 ├─ config.json           # Wi-Fi & runtime settings
 ├─ index.html            # Desktop / Mobile UI
 ├─ favicon.ico           # Browser tab icon
 ├─ FileManager.html      # system app
 ├─ Editor.html           # system app
 ├─ Info.html             # system app (_Settings_Info.html in folder install)
 ├─ _Settings_NetworkSettings.html
 ├─ _Settings_Restart.html
 ├─ _Games_Minesweeper.html
 ├─ minesweeper.ico
 ├─ folder.ico            # generic folder icon
 └─ …                     # additional .html & .ico files
```

---

### 3. App Folders  
Use the **underscore pattern** to create *virtual* folders:

```
_FolderName_AppName.html
```

| Example File | Dock / Menu Entry | Folder |
|--------------|-------------------|--------|
| `_Games_Minesweeper.html` | “Minesweeper” inside “Games” folder | Games |
| `_Tools_Calculator.html`  | “Calculator” inside “Tools” folder | Tools |

#### Folder Icons  
1. `FolderName.ico` (e.g., `Games.ico`) → used automatically.  
2. If missing → fall back to `folder.ico`.  
3. `folder.ico` is **restricted** to prevent accidental deletion.

#### Folder Panel Behaviour  
- Clicking a folder icon opens a *floating panel* that lists the apps.  
- Panel closes when:  
  • an app is launched • another dock icon is clicked • user clicks outside.

---

### 4. Icon System (`*.ico`)  
- Each **.html** file can have a matching **.ico** file with the **same base name**.  
  - `FileManager.html` → `FileManager.ico`  
- If the `.ico` is missing, a **📄 emoji SVG** is rendered instead.  
- Icons are **50 × 50 px** on the dock and **40 × 40 px** inside folder panels.  
- PNG → rename to `.ico`; the browser will still display it.

---

### 5. Restricted Files  
`config.json` → `RESTRICTED` set in `main.py`:

| File | Why Protected |
|------|---------------|
| `main.py` | Core server code |
| `config.json` | Runtime secrets (Wi-Fi PSK) |
| `index.html` | Desktop UI |
| `folder.ico` | Generic folder icon |

**Effect:**  
- Cannot be **deleted**, **renamed**, or **overwritten** from the web UI or APIs.  
- Editing via **Editor.html** is still possible (if Editor is not in RESTRICTED).

---

### 6. System Apps (inside `/apps/system`)  
These apps are **shipped with every System / Tools / Everything install**:

| App | Filename | Purpose |
|-----|----------|---------|
| **File Manager** | `FileManager.html` | Browse, rename, delete, upload, download files |
| **Editor**       | `Editor.html`       | Plain-text editor with save / discard |
| **Info**         | `_Settings_Info.html` | System stats & runtime info |
| **Network Settings** | `_Settings_NetworkSettings.html` | STA network scan + credentials |
| **Restart**      | `_Settings_Restart.html` | Soft-reboot or switch to STA/AP |

> In **System**, **Tools** and **Everything** packages these files are **copied to root** and (optionally) prefixed with `_Settings_` to group them under a “Settings” folder.

---

### 7. Common Workflows with System Apps

| Task | Steps |
|------|-------|
| **Upload a new game** | 1. Open `FileManager.html` → “Upload” → select `.html` + `.ico` |
| **Edit a config file** | 1. Launch `Editor.html` → open `config.json` → edit → save |
| **Switch to STA mode** | 1. Open `_Settings_NetworkSettings.html` → scan → select SSID → enter PSK → save & reboot |
| **Delete a user file** | 1. `FileManager.html` → tick file → “Delete” (restricted files are greyed-out) |

---

### 8. Mobile Mode Quick Notes  
- Dock is **hidden**; a **48 px system bar** appears at the top.  
- App windows are **always full-screen** below the bar.  
- **Hamburger menu** (☰) opens a **grid launcher** identical to the dock icons.  
- Folders still work: tap folder → folder panel → tap app.

---

## ✅ Checklist for New Users
- [ ] Copy deployment package to Pico root.  
- [ ] Edit `config.json` with your Wi-Fi credentials.  
- [ ] Reboot → browse to Pico IP.  
- [ ] Use **File Manager** to upload new `.html`/`.ico` apps.  
- [ ] Use **Editor** to tweak code on-device.  
- [ ] Use **Network Settings** to switch between AP ↔ STA.

---
