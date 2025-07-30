# README.md – `/apps/system`

This folder contains the **core system apps** that let you manage the Pico W entirely from the browser GUI.

1. **App file** – a single HTML file that runs entirely on its own.  
   *Example:* `Info.html`

2. **Icon file** – 64 × 64 px ICO with **exactly the same base name** as the HTML file.  
   *Example:* `Info.ico`

---

## FileManager.html  
All-purpose file browser.  
- **Edit** launches `Editor.html` for text / HTML files.  
- **View** launches `Viewer.html` for `.ico`, `.png`, `.jpg`, `.gif`, etc.  
- **Rename** lets you move an app into a folder by adding the `_FolderName_` prefix.  
- **Delete** removes any user file (restricted files are greyed out).  

---

## Editor.html  
Full text editor for any file.  
- Open, modify, save, or “save-as” plain text, HTML, JSON, or any other text format.  

---

## Viewer.html  
Simple image viewer.  
- Displays `.ico`, `.png`, `.jpg`, `.gif` and other common web formats directly in the browser.  


## Info.html  
Shows live system information: free memory, flash usage, temperature, network addresses, etc.  This is included in the "Settings" app folder by the packaging scripts.

## NetworkSettings.html  
Connects the Pico to your Wi-Fi.  
- Scans nearby networks, lets you enter a password, and switches between STA and AP mode.  This is included in the "Settings" app folder by the packaging scripts.

### Restart.html  
Soft-reboots the Pico from the browser—no button presses required. This is included in the "Settings" app folder by the packaging scripts.  


---

### Icons  
Each `.html` file should have a matching **64 × 64 px** `.ico` file with the same base name (e.g., `FileManager.ico`).  
These icons appear on the dock, in folder panels, and inside the file manager.

### Organizing into folders  
By default these apps appear loose on the dock.  
To group them under a folder (e.g., *Tools*, *Dev*, etc.):

- **Prefix the HTML file ONLY with `_FolderName_`**  
  *Example:* `_Settings_Info.html`  
  The icon **keeps its original name**: `Info.ico`

- `Settings.ico` is provided as a default icon for the "Settings" app folder; otherwise the generic `folder.ico` is used.

### Packaging  
`package-system.sh`, `package-tools.sh`, `package-games.sh` and `package-everything.sh` automatically copy every `.html` and `.ico` from this folder into the final deployment.