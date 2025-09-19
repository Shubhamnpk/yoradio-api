# Yo Radio API

A comprehensive, open-source database of radio stations across Nepal. This API provides easy access to streaming URLs, frequencies, locations, and other details for over 4000+ radio stations from all 7 provinces.

## Features

- 📡 **Live Streaming URLs**: Direct access to radio station streams
- 📍 **Complete Station Data**: Name, frequency, address, province information
- 🚀 **Easy Integration**: Simple JSON API endpoints
- 🔄 **Regularly Updated**: Fresh data from across Nepal
- 📱 **Mobile Friendly**: Responsive design for all devices

## API Endpoints

### Get All Stations
```
GET /data/index.json
```
Returns the complete database of all radio stations.

**Response Format:**
```json
[
  {
    "id": "unique-station-id",
    "name": "Station Name",
    "streamUrl": "https://stream.example.com/live",
    "frequency": 96.1,
    "address": "Station Address, City, Nepal",
    "province": 3
  }
]
```

### Get Active Stations
```
GET /data/active.json
```
Returns a curated list of currently active and verified stations.

## Usage

### JavaScript Example
```javascript
// Fetch all stations
fetch('/data/index.json')
  .then(response => response.json())
  .then(data => {
    console.log('Total stations:', data.length);
    // Process your data here
  });

// Fetch active stations
fetch('/data/active.json')
  .then(response => response.json())
  .then(data => {
    // Display active stations
    data.forEach(station => {
      console.log(`${station.name} - ${station.frequency} MHz`);
    });
  });
```

### HTML Audio Player Example
```html
<audio controls>
  <source src="https://radio-broadcast.ekantipur.com/stream" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>
```

## Province Codes

- 1: Province 1 (Eastern Nepal)
- 2: Province 2 (Terai Region)
- 3: Bagmati Province (Central Nepal)
- 4: Gandaki Province
- 5: Lumbini Province
- 6: Karnali Province
- 7: Sudurpashchim Province

## Built With Yo Radio API

Here are some amazing projects using this API:

- [**Yoafsana Radio**](https://shubhamnpk.github.io/yoafsana-radio/) - A beautiful radio streaming web app
- [**Yo Radio**](https://example.com/yoradio) - Full-featured radio platform
- *Your project here!* - Contribute your creation

## Contributing

We welcome contributions! Please feel free to:

1. Add new radio stations
2. Update stream URLs
3. Improve station information
4. Enhance the documentation
5. Report issues or suggest features

### Adding New Stations

1. Fork the repository
2. Add station data to `data/index.json`
3. Update `data/active.json` if it's a verified active station
4. Submit a pull request

**Station Data Format:**
```json
{
  "id": "unique-id-string",
  "name": "Station Name",
  "streamUrl": "https://valid-stream-url.com/live",
  "frequency": 96.1,
  "address": "Complete address, City, Nepal",
  "province": 3
}
```

## Development

### Running Locally

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The server will run on `http://localhost:3000`

### Validation

Validate the JSON data files:
```bash
npm run validate
```

## Interactive Website Features

The website includes:
- **Live Station Browser**: Browse and search through all active radio stations
- **Real-time Audio Player**: Click any station to start streaming instantly
- **Smart Filtering**: Filter by province and search by station name/location
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Modern UI**: Clean, intuitive interface with smooth animations

## Deployment

This project uses GitHub Actions for automatic deployment to GitHub Pages:

### Automatic Deployment
- Push to `main` branch triggers automatic deployment
- Data validation runs before each deployment
- Available at: `https://[username].github.io/yoradio-api/`

### Manual Deployment Options
Can also be deployed to:
- Netlify
- Vercel
- Any static hosting service

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or contributions, please open an issue on GitHub.

---

**Made with ❤️ for Nepal's radio community**