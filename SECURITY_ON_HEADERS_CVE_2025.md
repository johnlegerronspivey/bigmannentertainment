# Security Update: on-headers - CVE-2025-7339

**Date:** 2025
**Severity:** Critical → Low (varies by source)
**CVE:** CVE-2025-7339
**Vulnerability Type:** Improper Handling of Unexpected Data Type (CWE-241)
**Published:** July 17, 2025

## Summary

Updated on-headers from version 1.0.2 to 1.1.0 to address a critical vulnerability in header handling (CVE-2025-7339).

## Vulnerability Details

### What Was Vulnerable

The vulnerability exists due to improper handling of unexpected data types in the `response.writeHead()` function. Specifically, when an array is passed to `response.writeHead()` instead of an object, the on-headers middleware may inadvertently modify HTTP response headers.

### Affected Versions

All versions of on-headers prior to 1.1.0 are vulnerable to this issue.

### Vulnerability Classification

Related to **CWE-241** (Improper Handling of Unexpected Data Type), which occurs when a product does not properly handle elements that are not of the expected type.

### Impact

- **Data Leakage:** Potential exposure of sensitive information through modified headers
- **Response Manipulation:** HTTP responses can be manipulated by attackers
- **Header Modification:** Unintended modification of HTTP response headers

### Severity Rating

While initially classified as "Low" severity by some sources, it is categorized as a **critical vulnerability** in other security databases due to its potential for unintended header modifications and data leakage.

## Remediation Actions Taken

### Version Upgraded

- **on-headers:** 1.0.2 → 1.1.0 ✅

### Update Method

Direct upgrade using yarn:
```bash
cd /app/frontend
yarn upgrade on-headers@^1.1.0
```

### Verification

```bash
yarn list --pattern "on-headers" --depth=0
```

Output:
```
└─ on-headers@1.1.0
```

## Workaround (Not Required - Already Patched)

If immediate upgrading were not possible, the temporary workaround would be to pass an object to `response.writeHead()` instead of an array. However, this is no longer necessary as we have applied the official patch.

## Testing & Validation

✅ **Services Status:** All services running correctly
✅ **Frontend Compilation:** Compiled successfully without errors
✅ **Application Functionality:** UI loads and functions correctly
✅ **Header Handling:** Response headers processed correctly
✅ **No Breaking Changes:** Application behavior unchanged

## Industry Response

Several major projects have already addressed this issue, including:
- netlify-cli updated to use patched version 1.1.0
- Various IBM products issued security bulletins
- OpenSearch-Dashboards tracked and addressed the issue

## References

- CVE-2025-7339: https://github.com/jshttp/on-headers/security/advisories/GHSA-76c9-3jph-rj3q
- Snyk Advisory: https://security.snyk.io/package/npm/on-headers/1.0.2
- Vulert Database: https://vulert.com/vuln-db/debian-13-node-on-headers-300576

## Status

**RESOLVED** - on-headers has been successfully updated to the patched version 1.1.0.
