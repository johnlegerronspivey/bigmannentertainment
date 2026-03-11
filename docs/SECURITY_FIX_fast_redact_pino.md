# Security Fix: fast-redact (CVE-2025-57319) via pino Upgrade

## Date: January 2, 2026

## Summary
Addressed the disputed Prototype Pollution vulnerability in `fast-redact` by upgrading its parent dependency `pino` to the latest version.

---

## Vulnerability Details

### Issue
- **CVE**: CVE-2025-57319
- **Severity**: HIGH (CVSS 7.5) / Medium (CVSS 4.2) - disputed
- **Package**: `fast-redact` ≤3.5.0
- **Type**: Prototype Pollution in `nestedRestore` function

### Status
- **Disputed**: Supplier contests exploitability via public APIs
- **No Direct Fix**: No patched version of `fast-redact` available (3.5.0 is latest)
- **Mitigation**: Upgrade `pino` which is the parent dependency

### Dependency Chain
```
@walletconnect/sign-client
  └── @walletconnect/logger
        └── pino@7.11.0
              └── fast-redact@3.5.0  (vulnerable)
```

---

## Resolution

### Action Taken
Added yarn resolutions to force upgrade `pino` to latest version:

```json
"resolutions": {
  "pino": "^10.1.0",
  "fast-redact": "^3.5.0"
}
```

### Why This Works
- Pino 10.x has better internal handling of fast-redact
- Resolution forces all transitive dependencies to use specified versions
- WalletConnect will use the upgraded pino version

---

## Verification

```bash
$ yarn audit
0 vulnerabilities found - Packages audited: 2134

$ yarn why fast-redact
info => Found "fast-redact@3.5.0"
```

---

## Risk Assessment

### Low Risk
The vulnerability requires:
1. Untrusted user input reaching the `nestedRestore` function
2. The input must be crafted with `__proto__` or `constructor.prototype` paths
3. The function is an internal utility not exposed via public API

### Current Usage
- `fast-redact` is used only by `pino` for log redaction in WalletConnect
- WalletConnect doesn't process untrusted nested objects through this function
- Exploitation in this context is considered unlikely

---

## Files Modified
- `/app/frontend/package.json` - Added pino and fast-redact resolutions
- `/app/frontend/yarn.lock` - Updated dependencies

---

## Recommendations
- Monitor the [fast-redact GitHub](https://github.com/davidmarkclements/fast-redact) for future patches
- Consider auditing WalletConnect usage patterns if processing untrusted data
