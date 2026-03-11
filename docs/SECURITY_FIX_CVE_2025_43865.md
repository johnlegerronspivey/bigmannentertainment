# Security Fix: CVE-2025-43865 (React Router Cache Poisoning)

## Date: January 2026

## CVE Details
- **CVE ID**: CVE-2025-43865
- **Severity**: High (CVSS 8.2)
- **Type**: Cache Poisoning / Potential Stored XSS
- **Affected Package**: react-router
- **Affected Versions**: >= 7.0.0, <= 7.5.1
- **Patched Version**: >= 7.5.2

## Vulnerability Description
CVE-2025-43865 is a cache poisoning vulnerability in React Router's framework mode. Attackers could spoof pre-rendered data by adding the `X-React-Router-Prerender-Data` header when loaders are used, enabling cache poisoning and potential stored XSS if caching is enabled.

## Resolution

### Current Status: ALREADY PATCHED
The application was already running `react-router-dom@7.12.0` and `react-router@7.12.0`, which are well above the patched version 7.5.2.

### Verification
```bash
yarn list react-router react-router-dom
# Output: react-router@7.12.0, react-router-dom@7.12.0
```

### Additional Fix Applied
While investigating CVE-2025-43865, a high-severity vulnerability in the `h3` package (Request Smuggling TE.TE) was discovered and fixed:
- **Package**: h3
- **Vulnerability**: Request Smuggling (TE.TE)
- **Patched Version**: >= 1.15.5
- **Fix**: Added resolution in package.json

## Files Modified
- `/app/frontend/package.json` - Added h3 resolution to ^1.15.5

## Audit Results After Fix
- High severity vulnerabilities: 0
- All react-router related vulnerabilities: Resolved

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43865
- https://github.com/advisories/GHSA-cpj6-fhp6-mr6j
- https://www.netlify.com/changelog/security-update-react-router-remix-vulnerabilities/
