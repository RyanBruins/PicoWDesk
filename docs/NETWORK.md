# 📶 PicoWDesk  Networking Guide  
`/docs/NETWORK.md`

This file covers everything you need to know about getting your Pico W Desktop on-line and keeping it there.

---

## 🔧 1.  Configuration File – `config.json`

All network behaviour is **completely** driven by the JSON keys below.  
Edit the file directly (USB mass-storage) or let the **Network Settings** app do it for you (section 4).

| Key | Default | Purpose |
|-----|---------|---------|
| `"ssid"` | `""` | Home / office Wi-Fi name to connect to in STA mode. |
| `"psk"` | `""` | WPA2-PSK password for the above SSID. |
| `"hostname"` | `"picowdesk"` | mDNS and DHCP hostname request (STA mode only). |
| `"mode"` | `"AP"` | **Boot mode** – `"AP"` or `"STA"` (case-insensitive). |
| `"AP_NAME"` | `"PicoWDesk"` | SSID broadcast when running in **AP-only** mode. |
| `"AP_PASS"` | `"picowdesk12345"` | WPA2 password for the AP; **≥ 8 characters**. |
| `"PORT"` | `80` | TCP port the HTTP server listens on in **both** modes. |

> 💡 The file is re-written automatically when you use the **Network Settings** app, so manual edits are optional.

---

## 🔄 2.  Two Operating Modes – AP vs STA

| Mode | Description | Typical Use | IP Address |
|------|-------------|-------------|------------|
| **AP** (Access Point) | Pico W becomes its **own** Wi-Fi router. | First-time setup, places without Wi-Fi, or when you want an isolated network. | `192.168.4.1/24` (fixed) |
| **STA** (Station) | Pico W **joins** an existing Wi-Fi network like any laptop or phone. | Permanent installation at home, school, office, etc. | Assigned by your router via DHCP |

### Boot Logic
1. On power-up the firmware reads `CFG["mode"]`.
2. **If `"AP"`** → immediately start the access point.  
   (LED blinks 1 Hz square wave.)
3. **If `"STA"`** → attempt to connect to `ssid/psk`.  
   - Success: LED stays solid on.  
   - Failure: **fall back to AP mode** and **rewrite `config.json["mode"] = "AP"`** so the next reboot is guaranteed usable.  
   - Empty `ssid`: same as failure.

---

## ⭐ 3.  Using the **Network Settings** App

Open the **Network Settings** icon on the desktop or mobile launcher:

1. **Current Status**  
   Shows the active mode, SSID, IP addresses and RSSI (if STA).

2. **Scan & Connect (STA)**  
   - Press **“Scan”** to list nearby networks sorted by signal strength.  
   - Click a row to auto-fill SSID.  
   - Enter the password, then **“Connect to Wi-Fi”**.  
   - Pico writes the new credentials to `config.json`, sets `"mode":"STA"` and reboots.

3. **Switch to AP-Only**  
   - Press **“Switch to AP-only Mode!”** (only visible if currently in STA).  
   - Pico sets `"mode":"AP"` and reboots.

4. **Switch to STA Mode**  
   - Press **“Switch to STA Mode!”** (only visible if currently in AP).  
   - Pico sets `"mode":"STA"` and reboots.

> 🔄 Every mode change triggers a **1-second delayed reboot** so the new settings take effect.

---

## 🧪 4.  Manual / Advanced Tweaks

### Hot-Swap without Reboot
The **Network Settings** GUI is the recommended path.  
If you edit `config.json` manually:

1. Save the file.
2. Use the **Reboot** system app **or** power-cycle the board.
3. Observe the LED pattern to confirm the expected mode.

### Custom AP Channel
Channel 6 is hard-coded in `main.py`.  
If you need a different channel, edit the `ap.config(...)` line and re-flash `main.py`.

### Static STA IP
Not exposed in the UI.  
Advanced users can modify `main.py` to call `sta.ifconfig((ip, mask, gw, dns))` right after a successful connection.

---

## 📝 5.  Quick Reference Commands (REST API)

| Endpoint | Method | Payload | Effect |
|----------|--------|---------|--------|
| `/api/info` | GET | — | Returns JSON with mode, SSID, IP, RSSI, etc. |
| `/api/scan` | GET | — | JSON array of `{ssid, rssi}` visible networks. |
| `/api/connect` | POST | `{"ssid":"MyNet","psk":"secret"}` | Sets STA credentials, reboots. |
| `/api/mode/ap` | POST | — | Forces AP mode, reboots. |
| `/api/mode/sta` | POST | — | Forces STA mode, reboots. |

---

## 🎉 6.  Troubleshooting

| Symptom | Check |
|---------|-------|
| Pico AP never appears in Wi-Fi list | Ensure `mode = "AP"` in `config.json` and LED is blinking 0.5 Hz. |
| STA connection fails repeatedly | Verify SSID/password and ensure 2.4 GHz band (Pico W is 2.4 GHz only). |
| IP shown is `0.0.0.0` in STA | DHCP server not responding – check router. |

---

Happy networking!