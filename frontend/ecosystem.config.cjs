const fs = require('fs');
const path = require('path');

// Helper to load .env manually
function loadEnv(filePath) {
  if (!fs.existsSync(filePath)) return {};
  const content = fs.readFileSync(filePath, 'utf-8');
  return content.split('\n').reduce((acc, line) => {
    const [key, value] = line.split('=');
    if (key && value) acc[key.trim()] = value.trim().replace(/['"]/g, '');
    return acc;
  }, {});
}

const env = loadEnv(path.join(__dirname, '.env'));
const PORT = env.PORT || 5173;

module.exports = {
  apps: [
    {
      name: "ai-sql-frontend",
      script: "serve",
      env: {
        PM2_SERVE_PATH: "./dist",
        PM2_SERVE_PORT: PORT,
        PM2_SERVE_SPA: "true",
        PM2_SERVE_HOMEPAGE: "/index.html"
      }
    }
  ]
};
