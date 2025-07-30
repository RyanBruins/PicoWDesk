# PicoWDesk – Installation Guide

> This guide provides instructions for installing and running PicoWDesk on a Raspberry Pi Pico W.

---

## Prerequisites

1. **Raspberry Pi Pico W** with MicroPython firmware  
   (➜ [official UF2](https://micropython.org/download/rpi-pico-w/)).

2. **USB data cable** (not charge-only).

3. **Host computer** (Windows, macOS, Linux) with:
   - Python 3.x
   - `rshell` or `mpremote` (both installable via `pip install rshell mpremote`)

---

## Step-by-Step

### 1. Connect the Pico W
- Hold **BOOTSEL** while plugging in USB.  
- A new USB mass-storage drive (RPI-RP2) appears.

### 2. Flash MicroPython
- Copy the downloaded `.uf2` file onto the drive.  
- Drive disappears → MicroPython is installed.

### 3. Mount the Pico Filesystem
Using **mpremote** (recommended):

```bash
mpremote mount .
```
Or with rshell:
```bash
rshell -p /dev/ttyACM0  # adjust port as needed
```
4. Copy the Deployment Files
From the deploy folder (created by the packaging script):
```bash
cd deploy
mpremote cp -r . :
```
This copies main.py, index.html, config.json, favicon.ico, plus any apps you chose.
5. (Optional) Edit Wi-Fi Credentials
Edit config.json before copying, or afterwards:
```bash
mpremote edit config.json
```
Add your SSID & password:
```JSON
"ssid": "YourNetwork",
"psk":  "YourPassword"
```
6. Reboot
- Unplug/re-plug USB, or
- mpremote reset

The LED will blink connecting → connected (STA) or AP mode.
Open a browser to:
- STA mode: the Pico’s assigned IP (check your router).
- AP mode: http://192.168.4.1/

# Troubleshooting
| Symptom                | Fix                                              |
| ---------------------- | ------------------------------------------------ |
| LED blinks “error”     | Check `config.json` for typos in SSID/PSK.       |
| Cannot connect via USB | Try another cable or port.                       |
| Web page not loading   | Confirm you are on the correct IP or Wi-Fi SSID. |

Enjoy your PicoWDesk!