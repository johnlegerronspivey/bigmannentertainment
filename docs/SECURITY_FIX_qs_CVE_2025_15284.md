# Security Fix: qs CVE-2025-15284

## Date: December 12, 2025

## Summary
Successfully resolved a high-severity security vulnerability (CVE-2025-15284) in the `qs` npm package by upgrading from version 6.14.0 to 6.14.1.

## Vulnerability Details

### CVE-2025-15284 - Improper Input Validation / DoS via Memory Exhaustion
- **CVSS Score**: 8.7/10 (High Severity)
- **CWE**: CWE-20 (Improper Input Validation)
- **Description**: The `qs` library fails to properly enforce the `arrayLimit` option when parsing query strings with bracket notation (e.g., `a[]=1&a[]=2`)
- **Impact**: Attackers can bypass the `arrayLimit` protection and cause Denial-of-Service (DoS) attacks through memory exhaustion by sending HTTP requests with thousands of array elements
- **Exploitability**: Low complexity - requires only remote network access, no authentication needed
- **Affected Versions**: qs < 6.14.1
- **Patched Version**: qs >= 6.14.1

## Attack Scenario
1. Attacker sends HTTP request with malicious query string: `?a[]=1&a[]=2&a[]=3...` (thousands of times)
2. Despite `arrayLimit` configuration, all array elements are parsed and stored in memory
3. Server memory exhaustion leads to application crash or unresponsiveness
4. Single malicious request can crash the server without authentication

## Resolution Steps

### 1. Added qs Resolution
Updated `/app/frontend/package.json` to force upgrade:
```json
"resolutions": {
  ...
  "qs": "^6.14.1"
}
```

### 2. Installed Updated Package
Ran `yarn install` to apply the resolution and upgrade `qs` from 6.14.0 to 6.14.1

### 3. Verification
- Verified upgrade: `qs@6.14.1` installed ✅
- Confirmed 0 vulnerabilities with `yarn audit` ✅
- Tested frontend loads correctly at http://localhost:3000 ✅
- Restarted frontend service successfully ✅

## Results

**Before:**
- `qs@6.14.0` (vulnerable to CVE-2025-15284)
- High-severity DoS vulnerability present

**After:**
- `qs@6.14.1` ✅
- CVE-2025-15284 patched ✅
- 0 vulnerabilities in yarn audit ✅
- Frontend functioning correctly ✅

## Dependency Chain
The `qs` package is used by:
- `react-scripts` → `webpack-dev-server` → `express` → `qs`
- `react-scripts` → `webpack-dev-server` → `express` → `body-parser` → `qs`

## Files Modified
1. `/app/frontend/package.json` - Added `qs` resolution to force v6.14.1

## Technical Notes
- This is a transitive dependency (not directly installed)
- Used yarn resolutions to force the patched version across all dependency paths
- The vulnerability affects any application that parses query strings using `qs.parse()` with user-controlled input
- The fix ensures proper enforcement of the `arrayLimit` option

## References
- CVE-2025-15284: https://nvd.nist.gov/vuln/detail/CVE-2025-15284
- GitHub Advisory: GHSA-xxxx (if available)
- npm Security Advisory: https://www.npmjs.com/advisories
