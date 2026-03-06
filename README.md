# 📻 Yo Radio API

<p align="center">
  <img src="images/radio-logo.svg" width="120" height="120" alt="Yo Radio Logo">
</p>

<p align="center">
  <strong>Nepal's Premier Radio Station Database</strong><br>
  A comprehensive, open-source collection of 400+ radio stations from all 7 provinces of Nepal.
</p>

<p align="center">
  <a href="https://shubhamnpk.github.io/yoradio-api/">🌐 Live Demo</a> •
  <a href="https://shubhamnpk.github.io/yoradio-api/docs.html">📚 API Docs</a> •
  <a href="https://github.com/Shubhamnpk/yoradio">📱 YoRadio App</a>
</p>

---

## ✨ Features

- 📡 **400+ Radio Stations** - Complete coverage across all 7 provinces
- 🔴 **Live Streaming** - Direct streaming URLs for web and apps
- 🔍 **Smart Search** - Filter by province, name, or frequency
- ✅ **Validated Streams** - Regularly checked for availability
- 🎵 **Live Web Player** - Built-in player with pagination (12 per page)
- 🆓 **100% Free** - No API keys, no limits, open source

---

## 🚀 Quick Start

### Web Player
Visit our [Live Radio Player](https://shubhamnpk.github.io/yoradio-api/#stations) to stream stations directly in your browser!

### API Usage

#### Get All Stations
```
GET https://shubhamnpk.github.io/yoradio-api/data/index.json
```

#### Get Active Stations (Verified)
```
GET https://shubhamnpk.github.io/yoradio-api/data/active.json
```

#### Response Format
```json
[
  {
    "id": "radio-kantipur",
    "name": "Radio Kantipur",
    "streamUrl": "https://radio-broadcast.ekantipur.com/stream",
    "frequency": 96.1,
    "address": "Subidhanagar, Tinkune, Kathmandu",
    "province": 3
  }
]
```

---

## 📊 Data Files

| File | Description | Stations |
|------|-------------|----------|
| `data/index.json` | All stations (HTTPS only, web-compatible) | ~350+ |
| `data/active.json` | Verified working stations | ~350+ |
| `data/old.json` | HTTP streams (app-only) or broken | ~50+ |

---

## 💻 Code Examples

### JavaScript
```javascript
// Fetch and filter stations
const response = await fetch('https://shubhamnpk.github.io/yoradio-api/data/index.json');
const stations = await response.json();

// Filter by province
const bagmati = stations.filter(s => s.province === 3);

// Search by name
const kantipur = stations.find(s => s.name.includes('Kantipur'));
```

### Python
```python
import json
import urllib.request

with urllib.request.urlopen('https://shubhamnpk.github.io/yoradio-api/data/index.json') as response:
    stations = json.load(response)

# Filter by province
bagmati_stations = [s for s in stations if s['province'] == 3]
print(f"Found {len(bagmati_stations)} stations in Bagmati")
```

### React Hook
```javascript
function useRadioStations() {
  const [stations, setStations] = useState([]);
  
  useEffect(() => {
    fetch('https://shubhamnpk.github.io/yoradio-api/data/index.json')
      .then(res => res.json())
      .then(setStations);
  }, []);
  
  return stations;
}
```

---

## 🗺️ Province Codes

| Code | Province | Region |
|------|----------|--------|
| 1 | Koshi | Eastern Nepal |
| 2 | Madhesh | Terai Region |
| 3 | Bagmati | Kathmandu Valley |
| 4 | Gandaki | Western Central |
| 5 | Lumbini | Birthplace of Buddha |
| 6 | Karnali | Remote Western |
| 7 | Sudurpashchim | Far Western |

---

## 🛠️ Local Development

### Running Locally

```bash
# Clone the repository
git clone https://github.com/Shubhamnpk/yoradio-api.git
cd yoradio-api

# Install dependencies
npm install

# Start the server
node server.js

# Open http://localhost:3000
```

### Features Available Locally
- ✅ Web player with pagination
- ✅ Proxy for HTTP streams (converts to HTTPS)
- ✅ All API endpoints

### Validation Scripts

```bash
# Basic validation
python validate_urls.py

# Advanced validation with FFmpeg
python validate_advanced.py

# Move HTTP streams to old.json
python move_http_to_old.py
```

---

## 📱 Apps Using This API

| App | Description | Link |
|-----|-------------|------|
| **YoRadio** | Official desktop/mobile radio app | [GitHub](https://github.com/Shubhamnpk/yoradio) |
| **YoRadio Web** | Web player with live streaming | [Try it](https://shubhamnpk.github.io/yoradio-api/) |
| **Your App** | Submit your project! | [Contribute](#contributing) |

> This database was originally created for YoRadio, but it's **free for everyone** to use!

---

## 🤝 Contributing

We welcome contributions! You can:

1. 🎵 **Add new stations** - Find missing radio stations
2. 🔧 **Update URLs** - Fix broken stream links
3. 🐛 **Report issues** - Use the "Report Broken" button in the web player
4. 💻 **Submit apps** - Add your project to the showcase
5. 📝 **Improve docs** - Help us document better

### Report Broken Streams
Click the ⚠️ button in the web player when a stream fails, or [open an issue](https://github.com/Shubhamnpk/yoradio-api/issues/new).

---

## 📁 Project Structure

```
yoradio-api/
├── 📄 index.html          # Main web player (Tailwind CSS)
├── 📄 docs.html           # API documentation
├── 📁 data/
│   ├── index.json         # All stations (HTTPS)
│   ├── active.json        # Verified stations
│   └── old.json           # HTTP/broken stations
├── 📁 images/
│   └── radio-logo.svg     # Logo & favicon
├── 📄 server.js           # Node.js server with proxy
├── 📄 validate_urls.py    # Basic URL validation
├── 📄 validate_advanced.py # Advanced validation (FFmpeg)
└── 📄 README.md           # This file
```

---

## ⚠️ Known Issues

### Browser Compatibility
- **HTTP streams** are blocked by modern browsers (mixed content policy)
- These have been moved to `data/old.json`
- They still work in the YoRadio desktop/mobile app
- For local development, use the `/proxy` endpoint

### Geo-Restrictions
Some stations only work from within Nepal due to licensing restrictions.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Credits

- **Data Source**: Various radio stations across Nepal
- **Maintainer**: [@Shubhamnpk](https://github.com/Shubhamnpk)
- **Created for**: [YoRadio](https://github.com/Shubhamnpk/yoradio)

---

<p align="center">
  Made with ❤️ for Nepal's radio community
</p>
