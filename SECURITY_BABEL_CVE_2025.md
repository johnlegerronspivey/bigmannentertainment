# Security Update: @babel/helpers and @babel/runtime - CVE-2025-27789

**Date:** 2025
**Severity:** Medium
**CVE:** CVE-2025-27789
**Vulnerability Type:** Regular Expression Denial of Service (ReDoS)

## Summary

Updated @babel/helpers and @babel/runtime from version 7.26.0 to 7.28.4 to address a Regular Expression Denial of Service (ReDoS) vulnerability (CVE-2025-27789).

## Vulnerability Details

### What Was Vulnerable

Babel is a compiler for writing next generation JavaScript. When using affected versions to compile regular expression named capturing groups, Babel generates a polyfill for the `.replace` method that has **quadratic complexity** on certain replacement pattern strings.

### Affected Versions

- `@babel/helpers` < 7.26.10
- `@babel/runtime` < 7.26.10
- Also affects versions >= 8.0.0-alpha.0, < 8.0.0-alpha.16

### Vulnerability Conditions

The generated code is vulnerable only when ALL of the following conditions are met:

1. Using Babel to compile regular expression named capturing groups
2. Using the `.replace` method on a regular expression that contains named capturing groups
3. The code passes untrusted strings as the second argument of `.replace`

### Impact

The vulnerability can lead to:
- Excessive CPU usage
- Potential denial of service when processing certain input patterns
- Application unresponsiveness when handling untrusted strings in `.replace` method's second argument

## Remediation Actions Taken

### Versions Upgraded

- **@babel/helpers:** 7.26.0 → 7.28.4 ✅
- **@babel/runtime:** 7.26.0 → 7.28.4 ✅

### Update Method

Direct upgrade using yarn:
```bash
cd /app/frontend
yarn upgrade @babel/helpers@^7.26.10 @babel/runtime@^7.26.10
```

### Verification

```bash
yarn list --pattern "@babel/helpers|@babel/runtime" --depth=0
```

Output:
```
├─ @babel/helpers@7.28.4
└─ @babel/runtime@7.28.4
```

## Critical Requirement

⚠️ **Important:** Simply updating Babel dependencies is insufficient—**code must be recompiled after updating**. This has been completed as part of the application restart.

## Testing & Validation

✅ **Services Status:** All services running correctly
✅ **Frontend Compilation:** Compiled successfully without errors
✅ **Application Functionality:** UI loads and functions correctly
✅ **No Breaking Changes:** Application behavior unchanged

## References

- CVE-2025-27789: https://nvd.nist.gov/vuln/detail/CVE-2025-27789
- GitHub Advisory: https://github.com/advisories/GHSA-968p-4wvh-cqc8
- Babel Security Advisory: https://security.snyk.io/package/npm/@babel%2Fhelpers/7.26.0

## Status

**RESOLVED** - Both @babel/helpers and @babel/runtime have been successfully updated to secure versions (7.28.4), which is well above the minimum required version (7.26.10).
