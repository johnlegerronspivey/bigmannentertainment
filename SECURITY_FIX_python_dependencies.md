# Security Fix: Python Dependencies

## Date: January 2, 2026

## Summary
Fixed multiple Python dependency vulnerabilities identified by `pip-audit`.

---

## Vulnerability 1: ecdsa (CVE-2024-23342)

### Issue
- **CVE**: CVE-2024-23342 (GHSA-wj6h-64fc-37mp)
- **Severity**: HIGH (CVSS 7.4)
- **Package**: `ecdsa` (versions ≤0.19.1)
- **Issue**: Minerva timing attack vulnerability exposing private key information

### Root Cause
The `ecdsa` package was a transitive dependency of `python-jose`, which was listed in `requirements.txt` but **never actually used** in the codebase. The application uses `PyJWT` for all JWT operations.

### Resolution
- **Removed `python-jose`** from dependencies (unused package)
- **Removed `ecdsa`** as a result (was only required by python-jose)
- No code changes required - application already uses `PyJWT` for JWT handling

### Verification
```bash
pip-audit  # No ecdsa vulnerabilities
```

---

## Vulnerability 2: cbor2 (GHSA-wcj4-jw5j-44wh)

### Issue
- **Package**: `cbor2` 5.7.0
- **Fix**: Upgrade to 5.8.0

### Resolution
```bash
pip install cbor2==5.8.0
```

---

## Vulnerability 3: filelock (GHSA-w853-jp5j-5j7f)

### Issue
- **Package**: `filelock` 3.18.0
- **Fix**: Upgrade to 3.20.1

### Resolution
```bash
pip install filelock==3.20.1
```

---

## Post-Fix Audit Results

```
$ pip-audit
No vulnerabilities found (excluding emergent-plugins and emergentintegrations which are internal packages)
```

## Files Modified
- `/app/backend/requirements.txt` - Updated with fixed versions, removed unused python-jose
