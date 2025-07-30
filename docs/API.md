## 📄 **API.md**  
*Complete API Reference for Developers*

---

### Base URL  
All endpoints are served from the Pico at:

```
http://<pico-ip>/
```

---

## 1. File-Manager Endpoints

| Path | Method | Purpose | Request | Response |
|------|--------|---------|---------|----------|
| `/api/list` | **GET** | List all files with name, size, restricted flag | — | `[{"name":"calc.html","size":1234,"restricted":false}]` |
| `/api/read/<file>` | **GET** | Raw file contents | — | file body (text) |
| `/api/write/<file>` | **POST** | Overwrite or create file | body = raw text | `"OK"` or error |
| `/api/upload/<file>?offset=N&token=T&done` | **POST** | **Chunked upload** | body = binary chunk | `"OK"` |
| `/api/download/<file>` | **GET** | Force download with `Content-Disposition` | — | binary stream |
| `/api/delete/<file>` | **POST** | Delete file | — | `"OK"` or 404 |

> **Notes**  
> - `RESTRICTED` files return **403**.  
> - `upload` supports resumable uploads via `offset` & `done` flag.

---

## 2. Chat Endpoints

| Path | Method | Purpose | Request | Response |
|------|--------|---------|---------|----------|
| `/api/chat/history` | **GET** | Full history | — | `[{"id":1,"name":"bob","message":"hi"}]` |
| `/api/chat/poll?after=N` | **GET** | Messages after id | `after` query | same format or `null` |
| `/api/chat/send` | **POST** | New message | `{"name":"bob","message":"hi"}` | `"OK"` |

> History is **in-memory**; lost on reboot.

---

## 3. System & Wi-Fi Endpoints

| Path | Method | Purpose | Request | Response |
|------|--------|---------|---------|----------|
| `/api/info` | **GET** | System stats (mem, fs, IPs, temp, mode) | — | JSON object |
| `/api/scan` | **GET** | Available Wi-Fi networks | — | `[{"ssid":"MyNet","rssi":-42}]` |
| `/api/connect` | **POST` | Set STA credentials & reboot | `{"ssid":"MyNet","psk":"secret"}` | `"OK"` |
| `/api/mode/ap` | **POST` | Force AP mode & reboot | — | `"OK"` |
| `/api/mode/sta` | **POST` | Switch to STA mode & reboot | — | `"OK"` |
| `/api/restart` | **POST` | Soft-reboot | — | `"OK"` |

---

## 4. Static File Serving

Everything else is served **as-is** from the root:

```
GET /index.html        -> index.html
GET /favicon.ico       -> favicon.ico
GET /MyApp.html        -> MyApp.html
```

- **MIME** is inferred from extension.  
- **Cache-Control**: 1 h for `.ico`, 1 s for others.

---

## 5. Adding New Server-Side APIs

1. **Edit `main.py` → section 8**  
2. Add a new `elif clean_path == "/api/myendpoint":` block.  
3. **Validate path & method**  
   ```python
   if method != "POST":
       send(cl, "Method not allowed", code=405)
       return
   ```
4. **Read body** if needed:  
   ```python
   payload = json.loads(body)
   ```
5. **Return JSON**:  
   ```python
   send(cl, json.dumps({"result":42}), "application/json")
   ```
6. **Re-run deployment script** and flash Pico.

---

## 6. Client-Side Usage Pattern

```js
// 1. List files
const files = await fetch('/api/list').then(r => r.json());

// 2. Read a file
const txt = await fetch('/api/read/config.json').then(r => r.text());

// 3. Write a file
await fetch('/api/write/settings.json', {
  method: 'POST',
  body: JSON.stringify({theme:"dark"})
});

// 4. Send chat
await fetch('/api/chat/send', {
  method: 'POST',
  body: JSON.stringify({name:"Alice", message:"hello"})
});
```

---

### ❤️ Happy Hacking!  
Extend, remix, and share your PicoWDesk creations!