const fs = require('fs');

function readFile(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeFile(filePath, content) {
  fs.writeFileSync(filePath, content);
}

module.exports = { readFile, writeFile };