const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from current directory
app.use(express.static(path.join(__dirname)));

// CORS headers for API access
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});

// API endpoints
app.get('/api/stations', (req, res) => {
  res.redirect('/data/index.json');
});

app.get('/api/active', (req, res) => {
  res.redirect('/data/active.json');
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'Yo Radio API is running' });
});

app.listen(PORT, () => {
  console.log(`Yo Radio API server running on http://localhost:${PORT}`);
  console.log(`- Landing page: http://localhost:${PORT}/`);
  console.log(`- All stations: http://localhost:${PORT}/data/index.json`);
  console.log(`- Active stations: http://localhost:${PORT}/data/active.json`);
});