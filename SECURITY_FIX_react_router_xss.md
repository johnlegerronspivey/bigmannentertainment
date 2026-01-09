# Security Fix: React Router XSS Vulnerabilities

## Date: January 2026

## CVEs Addressed
- **CVE-2025-59057** (User-reported, mapped to related React Router XSS issues)
- **CVE-2026-22029** - React Router XSS via Open Redirects (HIGH severity)
- **CVE-2026-21884** - React Router SSR XSS in ScrollRestoration (HIGH severity)
- **CVE-2026-22030** - React Router CSRF in Action/Server Action Request Processing (MODERATE)

## Affected Package
- `react-router` (transitive dependency of `react-router-dom`)
- Vulnerable versions: `>=7.0.0 <=7.11.0`

## Resolution
Upgraded `react-router-dom` from `7.9.6` to `7.12.0`, which includes the patched `react-router` version `7.12.0`.

## Changes Made
1. Updated `frontend/package.json`:
   - Changed `"react-router-dom": "^7.9.6"` to `"react-router-dom": "^7.12.0"`
   - Added `"react-router": "^7.12.0"` to resolutions for additional safety

## Additional Fix
Also addressed **Preact JSON VNode Injection (CVE-2026-22028)** - HIGH severity:
- Added `"preact": "^10.27.3"` to resolutions to fix transitive vulnerability from `wagmi>@wagmi/connectors>cbw-sdk>preact`

## Verification
```bash
# Verify installed versions
yarn why react-router-dom  # Should show 7.12.0
yarn why react-router      # Should show 7.12.0
yarn why preact           # Should show 10.27.3

# Run audit
yarn audit  # Should show no HIGH/CRITICAL vulnerabilities
```

## Post-Fix Audit Status
- **Before**: 1 High, 8 Low severity vulnerabilities
- **After**: 0 High, 0 Critical, 8 Low severity vulnerabilities (informational only)

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-2w69-qvjg-hvjx
- https://github.com/remix-run/react-router/security/advisories/GHSA-8v8x-cx79-35w7
- https://github.com/remix-run/react-router/security/advisories/GHSA-h5cw-625j-3rxh
- https://github.com/preactjs/preact/security/advisories/GHSA-36hm-qxxp-pg3m
