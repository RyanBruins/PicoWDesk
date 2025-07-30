# ----------------------------------------------------------
#  PicoWDesk – MicroPython Web Desktop for Raspberry Pi Pico W
#  https://github.com/RyanBruins/PicoWDesk
#  Licence: MIT
#
#  main.py
#  ----------
#  • HTTP server (asyncio) serving both static files and JSON APIs
#  • Wi-Fi manager: falls back to AP mode if STA credentials fail
#  • Real-time LED status indicators
#  • File-manager, chat, system-info and configuration APIs
#
#  Configuration is **completely** driven by config.json;
#  no hard-coded values are used except safe fall-backs.
# ----------------------------------------------------------
import gc
import json
import os
import socket
import select
import machine
import network
import time
from machine import Pin, ADC
import uasyncio as asyncio

PICOWDESK_VERSION = "1.0.0"  #PicoWDesk Release Version

# ----------------------------------------------------------
# 1.  LOGGING
# ----------------------------------------------------------
def log(msg: str) -> None:
    """Prefix all console output with [PicoWDesk] for clarity."""
    print("[PicoWDesk]", msg)


# ----------------------------------------------------------
# 2.  CONFIGURATION LOADING
# ----------------------------------------------------------
try:
    with open('config.json') as f:
        CFG = json.load(f)
except OSError:
    CFG = {}

# Provide safe fall-backs and document each key
CFG.setdefault("ssid", "")                     # Home Wi-Fi SSID for STA mode (connect_sta)
CFG.setdefault("psk", "")                      # Wi-Fi password (STA) 
CFG.setdefault("hostname", "picowdesk")        # mDNS / DHCP hostname when in STA mode
CFG.setdefault("mode", "AP")                   # Boot mode: "AP" or "STA"
CFG.setdefault("AP_NAME", "PicoWDesk")         # Broadcast SSID when in AP mode (start_ap)
CFG.setdefault("AP_PASS", "picowdesk12345")    # Password for AP mode (start_ap)
CFG.setdefault("PORT", 80)                     # TCP port the HTTP server listens on (serve)
CFG.setdefault("RESTRICTED", ["main.py", "config.json", "index.html"])  # Files protected from web edits
CFG.setdefault("CHUNK", 4096)                  # I/O block size for file streams (upload/download)
CFG.setdefault("MAX_SINGLE_SEND", 512)         # Max bytes per socket.write() call (send_all)

AP_NAME         = CFG["AP_NAME"]
AP_PASS         = CFG["AP_PASS"]                   # re-use single password field
PORT            = CFG["PORT"]
RESTRICTED      = set(CFG["RESTRICTED"])       # convert to set for O(1) lookups
CHUNK           = CFG["CHUNK"]
MAX_SINGLE_SEND = CFG["MAX_SINGLE_SEND"]

LED = Pin("LED", Pin.OUT)                    # on-board LED indicator
# ----------------------------------------------------------
# 3.  LED STATUS TASK
#     Visual feedback for current operational state
# ----------------------------------------------------------
current_led_state = "error"                  # global state variable

async def led_task() -> None:
    """Blink patterns for connecting / connected / AP / error."""
    while True:
        state = current_led_state
        if state == "connecting":
            LED.on();  await asyncio.sleep_ms(100)
            LED.off(); await asyncio.sleep_ms(100)
        elif state == "connected":
            LED.on();  await asyncio.sleep_ms(1000)
        elif state == "ap":
            LED.on();  await asyncio.sleep_ms(1000)
            LED.off(); await asyncio.sleep_ms(1000)
        elif state == "error":
            LED.on();  await asyncio.sleep_ms(150)
            LED.off(); await asyncio.sleep_ms(150)
            LED.on();  await asyncio.sleep_ms(150)
            LED.off(); await asyncio.sleep_ms(1000)
        else:
            LED.off(); await asyncio.sleep_ms(1000)

def set_led_state(state: str) -> None:
    global current_led_state
    current_led_state = state

# ----------------------------------------------------------
# 4.  WI-FI MANAGEMENT
# ----------------------------------------------------------
def start_ap() -> network.WLAN:
    """Start Pico W as a Wi-Fi access point."""
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    time.sleep_ms(100)
    ap.active(True)
    ap.config(essid=AP_NAME, password=AP_PASS, channel=6)
    log(f"AP ready: {ap.ifconfig()}")
    return ap


def connect_sta(timeout: int = 20) -> bool:
    """Attempt STA connection; return True on success."""
    sta = network.WLAN(network.STA_IF)
    if sta.isconnected():
        log(f"STA already connected: {sta.ifconfig()}")
        return True

    log("STA connecting…")
    sta.active(True)
    sta.config(hostname=CFG["hostname"])
    sta.connect(CFG["ssid"], CFG["psk"])

    for i in range(timeout):
        if sta.isconnected():
            log(f"STA connected: {sta.ifconfig()}")
            return True
        log(f"STA retry {i+1}/{timeout}")
        time.sleep(1)

    log("STA failed")
    sta.active(False)
    return False


# ----------------------------------------------------------
# 5.  GENERIC HTTP HELPERS
# ----------------------------------------------------------
def send(cl: socket.socket, data, mime: str = "text/html", code: int = 200) -> None:
    """Send a complete HTTP response (small payloads)."""
    cl.send(f"HTTP/1.1 {code} OK\r\nContent-Type:{mime}\r\n\r\n".encode())
    cl.send(data.encode() if isinstance(data, str) else data)


async def send_all(sock: socket.socket, data: bytes) -> None:
    """Send entire byte buffer, coping with short writes."""
    mv = memoryview(data)
    sent = 0
    while sent < len(mv):
        try:
            n = sock.write(mv[sent:sent + MAX_SINGLE_SEND])
            if n is None:                   # non-blocking path (not used here)
                await asyncio.sleep_ms(10)
                continue
            sent += n
        except OSError as e:
            if e.errno == 11:               # EAGAIN
                await asyncio.sleep_ms(10)
                continue
            raise


async def recv_exact(sock: socket.socket, wanted: int) -> bytes:
    """Block until exactly *wanted* bytes are received."""
    buf = b''
    while len(buf) < wanted:
        part = sock.recv(wanted - len(buf))
        if not part:
            raise OSError("Connection closed")
        buf += part
    return buf


# ----------------------------------------------------------
# 6.  FILE UPLOAD STREAMING
# ----------------------------------------------------------
UPLOADS = {}                    # { "<filename>:<token>": file_object }

def _close_upload(name: str) -> None:
    """Flush, close and remove upload entry."""
    if name in UPLOADS:
        UPLOADS[name].flush()
        UPLOADS[name].close()
        del UPLOADS[name]


async def handle_upload(cl: socket.socket, path: str, body: bytes) -> None:
    """Handle chunked file upload via /api/upload/<filename>?offset=X&token=Y&done"""
    path_only = path.split('?')[0]
    name = path_only[len("/api/upload/"):]
    qs = path.split('?')[1] if '?' in path else ''
    params = {kv.split('=')[0]: kv.split('=')[1] for kv in qs.split('&') if kv}

    offset = int(params.get('offset', 0))
    token  = params.get('token', '0')
    done   = params.get('done') is not None
    key = f"{name}:{token}"

    if name in RESTRICTED:
        send(cl, "", code=403)
        return

    # First chunk – create file
    if key not in UPLOADS and offset == 0:
        free = os.statvfs("/")[0] * os.statvfs("/")[3]
        UPLOADS[key] = open(name, "wb")

    if key not in UPLOADS:
        send(cl, "Bad token", code=400)
        return

    f = UPLOADS[key]
    f.seek(offset)
    f.write(body)

    if done:
        _close_upload(key)

    send(cl, "OK")


# ----------------------------------------------------------
# 7.  IN-MEMORY CHAT SYSTEM
# ----------------------------------------------------------
CHAT_HISTORY = []               # [{"id":int, "name":str, "message":str}, …]
CHAT_SEQ     = 0
MAX_CHAT_LEN = 50


def chat_add(name: str, message: str) -> None:
    """Append a new chat message; maintain sliding window."""
    global CHAT_SEQ
    CHAT_SEQ += 1
    CHAT_HISTORY.append({
        "id": CHAT_SEQ,
        "name": (name[:10] if len(name) > 10 else name),
        "message": (message[:256] if len(message) > 256 else message)
    })
    if len(CHAT_HISTORY) > MAX_CHAT_LEN:
        CHAT_HISTORY.pop(0)


# ----------------------------------------------------------
# 8.  HTTP ROUTE HANDLERS
#     Grouped by functional area
# ----------------------------------------------------------
async def serve() -> None:
    """Main async HTTP server loop."""
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ai = socket.getaddrinfo("0.0.0.0", PORT)[0][-1]
    s.bind(ai)
    s.listen(5)
    s.setblocking(False)
    log(f"HTTP listening on port {PORT}")

    poller = select.poll()
    poller.register(s, select.POLLIN)

    while True:
        if poller.poll(100):
            try:
                cl, addr = s.accept()
                cl.setblocking(True)

                # ---- Parse request line & headers ----
                req_line = cl.readline().decode().strip()
                if not req_line:
                    cl.close(); continue
                method, full_path, _ = req_line.split(" ", 2)
                clean_path = full_path.split('?')[0]
                if clean_path == "/":
                    clean_path = "/index.html"

                content_len = 0
                while True:
                    line = cl.readline()
                    if not line or line == b"\r\n":
                        break
                    if line.lower().startswith(b"content-length:"):
                        content_len = int(line.split(b":", 1)[1].decode().strip())

                body = b''
                while len(body) < content_len:
                    part = cl.recv(content_len - len(body))
                    if not part:
                        break
                    body += part

                # ============================================================
                # 8.1  FILE-MANAGER API
                # ============================================================
                if clean_path == "/api/list":
                    # GET – list all files (name, size, restricted flag)
                    files = [{"name": f, "size": os.stat(f)[6],
                              "restricted": f in RESTRICTED}
                             for f in os.listdir()]
                    send(cl, json.dumps(files), "application/json")

                elif clean_path.startswith("/api/read/"):
                    # GET – return raw file content (403 for restricted)
                    name = clean_path[10:]
                    if name in RESTRICTED:
                        send(cl, "", code=403)
                    else:
                        try:
                            with open(name) as f:
                                send(cl, f.read(), "text/plain")
                        except OSError:
                            send(cl, "", code=404)

                elif clean_path.startswith("/api/write/"):
                    # POST – overwrite file with body (403 for restricted)
                    name = clean_path[len("/api/write/"):]
                    if name in RESTRICTED:
                        send(cl, "", code=403)
                    else:
                        try:
                            with open(name, "w") as f:
                                f.write(body.decode())
                            send(cl, "OK")
                        except OSError as e:
                            send(cl, f"Write failed: {e}", code=500)

                elif clean_path.startswith("/api/upload/"):
                    # POST (chunked) – append data at offset
                    await handle_upload(cl, full_path, body)

                elif clean_path.startswith("/api/download/"):
                    # GET – force download with Content-Disposition
                    name = clean_path[14:]
                    if name in RESTRICTED:
                        send(cl, "", code=403)
                    else:
                        try:
                            st = os.stat(name)
                            size = st[6]
                            cl.send(f"HTTP/1.1 200 OK\r\n"
                                    f"Content-Type: application/octet-stream\r\n"
                                    f"Content-Disposition: attachment; filename=\"{name}\"\r\n"
                                    f"Content-Length: {size}\r\n\r\n".encode())
                            with open(name, "rb") as f:
                                while True:
                                    chunk = f.read(CHUNK)
                                    if not chunk:
                                        break
                                    await send_all(cl, chunk)
                        except OSError:
                            send(cl, "", code=404)

                elif clean_path.startswith("/api/delete/"):
                    # POST – delete file (403 for restricted)
                    name = clean_path[12:]
                    if name in RESTRICTED:
                        send(cl, "", code=403)
                    else:
                        try:
                            os.remove(name)
                            send(cl, "OK")
                        except OSError:
                            send(cl, "", code=404)

                # ============================================================
                # 8.2  CHAT API
                # ============================================================
                elif clean_path == "/api/chat/history":
                    # GET – entire chat history
                    send(cl, json.dumps(CHAT_HISTORY), "application/json")

                elif clean_path == "/api/chat/poll":
                    # GET – only messages newer than ?after=<id>
                    qs = full_path.split('?')[1] if '?' in full_path else ''
                    params = {kv.split('=')[0]: kv.split('=')[1]
                              for kv in qs.split('&') if kv}
                    after = int(params.get('after', 0))
                    newer = [m for m in CHAT_HISTORY if m['id'] > after]
                    send(cl, json.dumps(newer if newer else None), "application/json")

                elif clean_path == "/api/chat/send":
                    # POST – {name:"", message:""}
                    try:
                        payload = json.loads(body)
                        chat_add(payload['name'], payload['message'])
                        send(cl, "OK")
                    except Exception as e:
                        send(cl, str(e), code=400)

                # ============================================================
                # 8.3  SYSTEM & WIFI CONFIG API
                # ============================================================
                elif clean_path == "/api/info":
                    # GET – system statistics
                    import sys               # <-- new
                    sta = network.WLAN(network.STA_IF)
                    ap  = network.WLAN(network.AP_IF)
                    temp = 27 - (ADC(4).read_u16() * 3.3 / 65535 - 0.706) / 0.001721
                    info = {
                        "mem_used":  gc.mem_alloc(),
                        "mem_free":  gc.mem_free(),
                        "fs_free":   os.statvfs("/")[0] * os.statvfs("/")[3],
                        "fs_used":   os.statvfs("/")[0] * os.statvfs("/")[2] -
                                     os.statvfs("/")[3] * os.statvfs("/")[0],
                        "fs_total":  os.statvfs("/")[0] * os.statvfs("/")[2],
                        "ssid": sta.config("ssid") if sta.isconnected() else None,
                        "ip_sta":    sta.ifconfig()[0] if sta.isconnected() else None,
                        "ip_ap":     ap.ifconfig()[0]  if ap.active()   else None,
                        "gateway":   sta.ifconfig()[2] if sta.isconnected() else None,
                        "rssi":      sta.status("rssi") if sta.isconnected() else 0,
                        "cpu_temp":  round(temp, 1),
                        "mode":      CFG.get("mode", "AP"),
                        "fw_build":  os.uname().version.split()[0],   # Pico W Firmware Version
                        "pwd_version": PICOWDESK_VERSION              # PicoWDesk Version
                    }
                    send(cl, json.dumps(info), "application/json")
                
                elif clean_path == "/api/scan":
                    # GET – Wi-Fi scan results
                    sta = network.WLAN(network.STA_IF)
                    sta.active(True)
                    nets = sta.scan()
                    visible = [n for n in nets if n[0] and len(n[0].strip()) > 0]
                    visible.sort(key=lambda n: n[3], reverse=True)   # strongest first
                    send(cl, json.dumps(
                        [{"ssid": n[0].decode(), "rssi": n[3]} for n in visible]),
                        "application/json")

                elif clean_path == "/api/connect":
                    # POST – {ssid:"", psk:""}  → reboot into STA
                    d = json.loads(body)
                    CFG["ssid"] = d["ssid"]
                    CFG["psk"]  = d["psk"]
                    CFG["mode"] = "STA"
                    with open("config.json", "w") as f:
                        json.dump(CFG, f)
                    send(cl, "OK")
                    asyncio.create_task(reboot_later())

                elif clean_path == "/api/mode/ap":
                    # POST – force AP mode → reboot
                    CFG["mode"] = "AP"
                    with open("config.json", "w") as f:
                        json.dump(CFG, f)
                    send(cl, "OK")
                    asyncio.create_task(reboot_later())

                elif clean_path == "/api/mode/sta":
                    # POST – force STA mode → reboot
                    CFG["mode"] = "STA"
                    with open("config.json", "w") as f:
                        json.dump(CFG, f)
                    send(cl, "OK")
                    asyncio.create_task(reboot_later())

                elif clean_path == "/api/restart":
                    # POST – reboot device
                    send(cl, "OK")
                    asyncio.create_task(reboot_later())

                # ============================================================
                # 8.4  STATIC FILE SERVING (fallback)
                # ============================================================
                else:
                    try:
                        stat = os.stat(clean_path[1:])
                        size = stat[6]
                        with open(clean_path[1:], "rb") as f:
                            mime = ("image/x-icon" if clean_path.endswith(".ico") else
                                    "text/html"    if clean_path.endswith(".html") else
                                    "text/plain")
                            max_age = 3600 if mime == "image/x-icon" else 1
                            cl.send(f"HTTP/1.1 200 OK\r\n"
                                    f"Content-Type: {mime}\r\n"
                                    f"Cache-Control: max-age={max_age}\r\n"
                                    f"Content-Length: {size}\r\n\r\n".encode())
                            remaining = size
                            while remaining > 0:
                                chunk = f.read(min(512, remaining))
                                if not chunk:
                                    break
                                bytes_sent = cl.send(chunk)
                                remaining -= bytes_sent
                                await asyncio.sleep_ms(1)
                    except OSError:
                        cl.send(b"HTTP/1.1 404 Not Found\r\n\r\n")

                cl.close()
                log(f"Served {clean_path}")
            except Exception as e:
                log(f"Handler: {e}")
                try:
                    cl.close()
                except:
                    pass
        await asyncio.sleep_ms(20)


# ----------------------------------------------------------
# 9.  REBOOT UTILITIES
# ----------------------------------------------------------
async def reboot_later() -> None:
    """Wait 1 s then reboot (used after config changes)."""
    await asyncio.sleep(1)
    machine.reset()


# ----------------------------------------------------------
# 10.  BOOT SEQUENCE
# ----------------------------------------------------------
async def main() -> None:
    log("=== PicoWDesk boot ===")
    asyncio.create_task(led_task())
    set_led_state("connecting")
    # ----------  ALWAYS start from what config.json says  ----------
    boot_mode = CFG.get("mode", "AP").strip().upper()
    log(f"Boot mode requested: {boot_mode}")

    if boot_mode == "STA":
        ssid = CFG.get("ssid", "").strip()
        if ssid:
            if connect_sta():
                CFG["mode"] = "STA"          # ensure persistence
                log("STA success")
                set_led_state("connected")
            else:
                log("STA failed → falling back to AP")
                CFG["mode"] = "AP"           # force AP for next boot
                with open("config.json", "w") as f:
                    json.dump(CFG, f)
                set_led_state("ap")
        else:
            log("No SSID → forcing AP")
            CFG["mode"] = "AP"
            with open("config.json", "w") as f:
                json.dump(CFG, f)
            set_led_state("ap")
    else:
        # Explicit AP
        log("AP mode requested")
        set_led_state("ap")

    # ----------  Bring up the interface that has been decided  ----------
    if CFG["mode"] == "AP":
        start_ap()
        log("Running in AP mode")
    else:
        log("Running in STA mode")

    await serve()


if __name__ == "__main__":
    asyncio.run(main())