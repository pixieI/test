# Supercharged URL Shortener 🚀

A feature-rich, persistent URL shortener built with Flask — supports custom aliases, click analytics, QR code generation, a clean web UI, and a REST API.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔗 **URL Shortening** | Generate 6-character short codes for long URLs |
| ✏️ **Custom Aliases** | Optionally provide your own short code (e.g., `my-link`) |
| 💾 **JSON Persistence** | All URLs saved to `urls.json` — survives server restarts |
| 👁️ **Click Analytics** | Track visit count and last access time per URL |
| 📱 **QR Codes** | Generate and download QR codes for any short URL at `/qr/<code>` |
| 🗑️ **Delete URLs** | Remove unwanted URLs from the web UI |
| 🔌 **REST API** | Programmatic access via JSON endpoints |
| 🎨 **Clean UI** | Responsive, modern interface with copy-to-clipboard |

## 🚀 Quick Start

1. **Install dependencies:**
   
```bash
   pip install -r requirements.txt
   
```

2. **Run the app:**
   
```bash
   python app.py
   
```

3. **Open in browser:**
   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 📖 Usage

### Web UI
1. Enter a URL (e.g., `https://example.com/very/long/path`)
2. Optionally type a custom alias (e.g., `my-cool-link`)
3. Click **Shorten**
4. Copy the short URL, download the QR code, or share it
5. Visit `/short/<code>` to get redirected

### REST API

**Shorten a URL:**
```bash
curl -X POST http://127.0.0.1:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'
```

**Shorten with custom code:**
```bash
curl -X POST http://127.0.0.1:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url", "custom_code": "my-link"}'
```

**Get stats for a short code:**
```bash
curl http://127.0.0.1:5000/api/stats/abc123
```

**List all URLs:**
```bash
curl http://127.0.0.1:5000/api/urls
```

### API Response Format
```json
{
  "short_code": "abc123",
  "original_url": "https://example.com/long/url",
  "short_url": "http://127.0.0.1:5000/short/abc123",
  "qr_url": "http://127.0.0.1:5000/qr/abc123",
  "created": "2025-01-15T10:30:00+00:00",
  "clicks": 42,
  "last_access": "2025-01-15T14:22:00+00:00"
}
```

## 📁 Project Structure

```
test/
├── app.py              # Flask application (~300 lines)
├── requirements.txt    # Dependencies
├── templates/
│   └── index.html      # Web UI with all features
├── urls.json           # Persistent URL store (auto-created)
├── README.md           # This file
└── TODO.md             # Development checklist
```

## 🧪 Testing

```bash
# Run the app
python app.py

# Test API with curl
curl -X POST http://127.0.0.1:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'

# Visit the short URL
open http://127.0.0.1:5000/short/<your-code>
```

## 🛠️ Tech Stack

- **Python 3.10+**
- **Flask 3.0** — web framework
- **qrcode[pil]** — QR code generation
- **JSON** — persistent storage (no database required)
