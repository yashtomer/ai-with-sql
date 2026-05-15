const fs = require('fs');
const path = require('path');

// Helper to load .env manually if dotenv isn't available
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
const BACKEND_PORT = env.BACKEND_PORT || 8080;

module.exports = {
  apps: [
    {
      name: "ai-sql-backend",
      script: "./venv/bin/python3",
      args: `-m uvicorn app:app --host 0.0.0.0 --port ${BACKEND_PORT}`,
      cwd: "./",
      watch: false,
      env: {
        NODE_ENV: "production",
      }
    }
  ]
};
