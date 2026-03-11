# Security Fix: webpack-dev-server Vulnerabilities

## Date: December 12, 2025

## Summary
Successfully resolved 2 moderate security vulnerabilities in `webpack-dev-server` by upgrading from version 4.15.2 to 5.2.2.

## Vulnerabilities Fixed

### 1. CVE-2025-30360 - Source Code Theft (Moderate)
- **Advisory**: GHSA-9jgg-88mc-972h
- **CVSS Score**: 6.5
- **Description**: Source code could be stolen when accessing a malicious website with non-Chromium based browsers
- **Impact**: Users with predictable ports using non-Chromium browsers were vulnerable

### 2. CVE-2025-30359 - Source Code Theft via Prototype Pollution (Moderate)
- **Advisory**: GHSA-4v9v-hfq4-rm2v  
- **CVSS Score**: 5.3
- **Description**: Source code could be stolen through prototype pollution attacks
- **Impact**: Users with predictable ports and output paths were vulnerable

## Resolution Steps

### 1. Added webpack-dev-server Resolution
Updated `/app/frontend/package.json` to force upgrade:
```json
"resolutions": {
  ...
  "webpack-dev-server": "^5.2.1"
}
```

### 2. Migrated webpack-dev-server Configuration
Updated `/app/frontend/craco.config.js` to support webpack-dev-server v5 API:
- Migrated `onBeforeSetupMiddleware` → `setupMiddlewares`
- Migrated `onAfterSetupMiddleware` → `setupMiddlewares`
- Migrated `https` option → `server` option

### 3. Verification
- Ran `yarn install` to apply the resolution
- Verified upgrade: `webpack-dev-server@5.2.2` installed
- Confirmed 0 vulnerabilities with `yarn audit`
- Tested frontend loads correctly at http://localhost:3000

## Results

**Before:**
- 2 moderate vulnerabilities
- `webpack-dev-server@4.15.2`

**After:**
- 0 vulnerabilities ✅
- `webpack-dev-server@5.2.2` ✅
- Frontend functioning correctly ✅

## Files Modified
1. `/app/frontend/package.json` - Added webpack-dev-server resolution
2. `/app/frontend/craco.config.js` - Migrated to webpack-dev-server v5 API

## Notes
- The upgrade required API migration due to breaking changes between v4 and v5
- `react-scripts` v5.0.1 uses old API, so we had to override via craco config
- All functionality tested and confirmed working
- Development server hot reload functioning normally
