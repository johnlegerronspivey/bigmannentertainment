#!/usr/bin/env node
/**
 * Post-install patch: Fix webpack-dev-server v5 compatibility with react-scripts
 * react-scripts calls devServer.close() but webpack-dev-server v5 uses devServer.stop()
 */
const fs = require('fs');
const path = require('path');

const startJsPath = path.join(__dirname, '..', 'node_modules', 'react-scripts', 'scripts', 'start.js');

try {
  if (fs.existsSync(startJsPath)) {
    let content = fs.readFileSync(startJsPath, 'utf8');
    if (content.includes('devServer.close()') && !content.includes('devServer.stop')) {
      content = content.replace(
        /devServer\.close\(\)/g,
        'typeof devServer.close === "function" ? devServer.close() : (typeof devServer.stop === "function" ? devServer.stop() : null)'
      );
      fs.writeFileSync(startJsPath, content, 'utf8');
      console.log('[postinstall] Patched react-scripts/start.js for webpack-dev-server v5 compat');
    }
  }
} catch (e) {
  console.warn('[postinstall] Could not patch start.js:', e.message);
}
