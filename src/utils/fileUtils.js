const fs = require('fs');

function readFile(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeFile(filePath, content) {
  fs.writeFileSync(filePath, content);
}

function fileExists(filePath) {
  return fs.existsSync(filePath);
}

module.exports = { readFile, writeFile, fileExists };
