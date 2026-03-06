const fs = require('fs');
const path = require('path');

function validateJSON(filePath) {
  try {
    const data = fs.readFileSync(filePath, 'utf8');
    JSON.parse(data);
    console.log(`✅ ${filePath} is valid JSON`);
    return true;
  } catch (error) {
    console.error(`❌ ${filePath} is invalid JSON: ${error.message}`);
    return false;
  }
}

function validateStations(filePath) {
  try {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    if (!Array.isArray(data)) {
      console.error(`❌ ${filePath} is not an array`);
      return false;
    }

    const ids = new Set();
    let valid = true;

    data.forEach((station, index) => {
      // Check required fields
      const requiredFields = ['id', 'name', 'streamUrl'];
      for (const field of requiredFields) {
        if (!station[field]) {
          console.error(`❌ Station ${index} missing ${field}`);
          valid = false;
        }
      }

      // Check for duplicate IDs
      if (station.id) {
        if (ids.has(station.id)) {
          console.error(`❌ Duplicate ID: ${station.id}`);
          valid = false;
        }
        ids.add(station.id);
      }

      // Check streamUrl format
      if (station.streamUrl && !station.streamUrl.startsWith('http')) {
        console.warn(`⚠️  Station ${station.name} has invalid streamUrl: ${station.streamUrl}`);
      }
    });

    if (valid) {
      console.log(`✅ ${filePath} data validation passed (${data.length} stations)`);
    }
    return valid;
  } catch (error) {
    console.error(`❌ Error validating ${filePath}: ${error.message}`);
    return false;
  }
}

// Validate files
const files = ['data/index.json', 'data/active.json'];
let allValid = true;

files.forEach(file => {
  if (fs.existsSync(file)) {
    if (validateJSON(file)) {
      validateStations(file);
    } else {
      allValid = false;
    }
  } else {
    console.error(`❌ ${file} does not exist`);
    allValid = false;
  }
});

if (allValid) {
  console.log('\n🎉 All validations passed!');
  process.exit(0);
} else {
  console.log('\n💥 Validation failed!');
  process.exit(1);
}