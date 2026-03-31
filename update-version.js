// update-version.js
const fs = require('fs');
const path = require('path');

// Lê o package.json para pegar a versão
const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
const newVersion = packageJson.version;

// Lê o version.json atual
const versionJsonPath = path.join(__dirname, 'version.json');
let versionData = { version: newVersion, lastUpdated: new Date().toISOString(), changelog: [] };

if (fs.existsSync(versionJsonPath)) {
    const existing = JSON.parse(fs.readFileSync(versionJsonPath, 'utf8'));
    versionData.changelog = existing.changelog || [];
}

// Adiciona nova entrada no changelog
versionData.changelog.unshift(`v${newVersion} - Deploy em ${new Date().toLocaleString()}`);

// Mantém apenas as últimas 10 entradas
if (versionData.changelog.length > 10) {
    versionData.changelog = versionData.changelog.slice(0, 10);
}

// Salva o version.json
fs.writeFileSync(versionJsonPath, JSON.stringify(versionData, null, 2));

console.log(`✅ Version.json atualizado para v${newVersion}`);