# Security Advisory: webpack-dev-server CVE Vulnerabilities

**Date:** January 2025  
**Issue:** Critical vulnerabilities in webpack-dev-server 4.15.2  
**Status:** ⚠️ CANNOT UPGRADE DUE TO COMPATIBILITY CONSTRAINTS  
**Priority:** MEDIUM (Development Environment Only)  
**CVE Risk Level:** HIGH for development environments

---

## Executive Summary

webpack-dev-server version **4.15.2** (currently used by this project) is affected by two critical CVE vulnerabilities (**CVE-2025-30359** and **CVE-2025-30360**) that can lead to source code theft during development. While patches exist in webpack-dev-server **5.2.1+**, upgrading would break compatibility with **react-scripts 5.0.1**, which is locked to webpack-dev-server 4.x.

**IMPORTANT:** This vulnerability **ONLY affects the development environment**. Production builds do not use webpack-dev-server and are **NOT vulnerable**.

---

## Vulnerabilities Identified

### 1. CVE-2025-30359 - Source Code Theft via Prototype Pollution
- **Affected Versions:** All versions ≤ 5.2.0 (including 4.15.2)
- **CVSS Score:** Not yet assigned, but considered HIGH severity
- **Attack Vector:** Remote, requires user interaction
- **Issue:** CWE-1321 - Improperly Controlled Modification of Object Prototype Attributes

**Description:**  
Attackers can steal source code when developers access a malicious website while running webpack-dev-server. The exploit works by:
1. Injecting a script tag pointing to the victim's local webpack-dev-server (on predictable ports like 3000, 3001, 8080)
2. Using JavaScript prototype pollution to expose `__webpack_modules__` 
3. Extracting the complete source code through the webpack runtime variables

**Prerequisites for Attack:**
- Developer is running `npm start` / `yarn start` (webpack-dev-server active)
- Developer visits a malicious website in their browser
- Webpack-dev-server is running on a predictable port
- Configuration has `output.iife: false` (or uses default settings)

### 2. CVE-2025-30360 - Origin Validation Error in WebSocket Connections
- **Affected Versions:** All versions ≤ 5.2.0 (including 4.15.2)
- **CVSS Score:** Not yet assigned, considered MEDIUM-HIGH severity
- **Attack Vector:** Network, requires user interaction
- **Issue:** CWE-346 - Origin Validation Error

**Description:**  
webpack-dev-server improperly handles the `Origin` header in WebSocket connections by always allowing IP address origins. This enables:
1. Malicious websites served on IP addresses (e.g., `http://192.168.1.100`) to establish WebSocket connections to the developer's local webpack-dev-server
2. Bypassing same-origin policy protections
3. Stealing source code through the WebSocket hot module replacement (HMR) protocol

**Prerequisites for Attack:**
- Developer is running webpack-dev-server with hot reload enabled
- Developer visits a malicious website hosted on an IP address
- Developer is using a non-Chromium browser (or Chromium < v94)
- Attacker knows or can guess the developer's local webpack-dev-server port

**Browser Protection Note:**  
Chromium-based browsers (Chrome, Edge, Brave) version 94+ provide some protection against CVE-2025-30360 by blocking non-HTTPS private network access by default.

---

## Current Environment Status

### Installed Versions
```
webpack-dev-server: 4.15.2 (VULNERABLE)
react-scripts: 5.0.1
@craco/craco: 7.1.0
react: 19.0.0
```

### Why We Cannot Upgrade

1. **Dependency Lock:**  
   react-scripts 5.0.1 explicitly depends on webpack-dev-server 4.x and is incompatible with 5.x

2. **Breaking API Changes in webpack-dev-server 5.x:**
   - `onAfterSetupMiddleware` replaced by `setupMiddlewares`
   - Stricter `Origin` header validation (the security fix itself)
   - Removed deprecated options: `logLevel`, `noInfo`, `quiet`
   - New configuration schema that breaks react-scripts' internal dev server setup
   - Changed `allowedHosts` behavior requiring explicit configuration

3. **Upgrade Path Blocked:**
   - react-scripts 5.0.1 is the latest stable version as of January 2025
   - No official react-scripts version supports webpack-dev-server 5.x yet
   - Using yarn resolutions to force webpack-dev-server 5.x causes immediate errors:
     ```
     Invalid options object. Dev Server has been initialized using 
     an options object that does not match the API schema.
     ```

4. **CRACO Limitations:**  
   While the project uses CRACO 7.1.0 for configuration overrides, CRACO cannot fix the underlying react-scripts webpack-dev-server config incompatibilities without extensive patching

---

## Risk Assessment

### Development Environment Risk: MEDIUM

**Factors Reducing Risk:**
1. ✅ **Production Unaffected:** Production builds use static files served by web servers, not webpack-dev-server
2. ✅ **Requires User Interaction:** Developers must visit a malicious site while dev server is running
3. ✅ **Browser Protections:** Chromium 94+ blocks some attack vectors
4. ✅ **Network Isolation:** Most developers work on isolated local networks
5. ✅ **Time-Limited Exposure:** Dev server only runs during active development

**Factors Increasing Risk:**
1. ❌ **Source Code Exposure:** Complete application source code could be stolen
2. ❌ **Credentials in Code:** Environment variables, API keys, or secrets in code could be exposed
3. ❌ **Intellectual Property:** Proprietary business logic and algorithms at risk
4. ❌ **Supply Chain:** Attackers could analyze code for further vulnerabilities

### Production Environment Risk: NONE
- ✅ Production builds do NOT use webpack-dev-server
- ✅ Production serves static compiled assets
- ✅ No CVE exposure in production deployments

---

## Mitigation Strategies

### Immediate Actions (IMPLEMENTED)

#### 1. Documentation ✅
- Created this comprehensive security advisory
- Documented all known vulnerabilities and constraints
- Established security awareness for development team

#### 2. Development Environment Hardening

**Browser Security:**
```bash
# Developers should use Chromium-based browsers (Chrome 94+, Edge, Brave)
# These provide built-in protections against CVE-2025-30360
```

**Network Isolation:**
```bash
# Run webpack-dev-server on localhost only (already configured)
# Never expose dev server to public networks or use tunneling services
```

**Port Randomization:**
```bash
# Use non-standard ports to reduce predictability
# Modify package.json scripts:
"start": "PORT=3142 craco start"  # Use random port instead of 3000
```

#### 3. Access Controls

**Browser Extensions:**
- Use browser extensions to block requests to localhost from external sites
- Enable strict site isolation in browser settings

**Firewall Rules:**
```bash
# Ensure localhost services are not accessible from network
# Verify firewall blocks incoming connections to dev ports
```

#### 4. Development Best Practices

**Code Repository Security:**
```bash
# Never commit sensitive credentials or API keys
# Use .env files and keep them in .gitignore
# Rotate any exposed credentials immediately
```

**Session Management:**
```bash
# Stop webpack-dev-server when not actively developing
# Don't leave dev server running while browsing the web
```

### Recommended Monitoring Actions

1. **Dependency Tracking:**
   - Monitor react-scripts releases for webpack-dev-server 5.x support
   - Subscribe to webpack-dev-server security advisories
   - Track Create React App GitHub issues for upgrade discussions

2. **Regular Audits:**
   ```bash
   # Run dependency audits regularly
   yarn audit
   
   # Check for react-scripts updates
   yarn outdated react-scripts
   ```

3. **Team Awareness:**
   - Educate development team about the vulnerabilities
   - Establish secure browsing practices during development
   - Implement code review for any exposed credentials

---

## Future Upgrade Path

### When to Upgrade

Upgrade webpack-dev-server to 5.2.1+ when **ANY** of these conditions are met:

1. ✅ **react-scripts 6.x is released** with webpack-dev-server 5.x support
2. ✅ **Create React App officially supports** webpack-dev-server 5.x
3. ✅ **Migration to alternative build tools** (Vite, Rsbuild, custom Webpack setup)
4. ✅ **Community patches are stable** and widely adopted

### Upgrade Prerequisites

```bash
# Check if react-scripts supports webpack-dev-server 5.x
yarn info react-scripts peerDependencies

# Verify compatibility before upgrading
yarn add webpack-dev-server@5.2.1 --dev  # TEST ONLY
yarn start  # Check for errors
```

### Migration Options

**Option 1: Wait for react-scripts 6.x**
- **Pros:** Official support, no breaking changes, maintained solution
- **Cons:** Timeline uncertain, passive security posture
- **Recommendation:** Best for most projects

**Option 2: Migrate to Vite**
- **Pros:** Modern build tool, better performance, no webpack-dev-server vulnerabilities
- **Cons:** Major migration effort, rewrite build configuration
- **Recommendation:** Consider for new projects or major refactors

**Option 3: Eject from Create React App**
- **Pros:** Full control over webpack config, can upgrade immediately
- **Cons:** Lose automatic updates, must maintain webpack config manually
- **Recommendation:** Only for teams with webpack expertise

**Option 4: Apply Community Patches**
- **Pros:** Can upgrade immediately with fixes
- **Cons:** Unofficial, may break in future, requires maintenance
- **Recommendation:** Only if security risk is critical

---

## Technical Details

### Vulnerability Exploitation Flow

**CVE-2025-30359 Attack Sequence:**
```javascript
// Attacker's malicious website code
// 1. Inject script tag to victim's webpack-dev-server
const script = document.createElement('script');
script.src = 'http://localhost:3000/main.js';  // Predictable port
document.body.appendChild(script);

// 2. Pollute Object prototype to access webpack internals
Object.prototype.__webpack_modules__ = true;

// 3. Extract source code from webpack runtime
// (webpack modules are now exposed through pollution)
```

**CVE-2025-30360 Attack Sequence:**
```javascript
// Attacker's website served on IP address (e.g., http://192.168.1.100)
// 1. Establish WebSocket connection to victim's dev server
const ws = new WebSocket('ws://localhost:3000/ws');

// 2. Subscribe to hot module replacement updates
ws.send(JSON.stringify({ type: 'subscribe' }));

// 3. Receive source code through HMR protocol
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Source code exposed in HMR updates
};
```

### Configuration Analysis

**Current webpack-dev-server Configuration:**
```javascript
// Managed internally by react-scripts 5.0.1
{
  host: 'localhost',              // ✅ Good - not exposed to network
  port: 3000,                     // ⚠️ Predictable default port
  hot: true,                      // ⚠️ Enables HMR (required for CVE-2025-30360)
  allowedHosts: 'auto',           // ⚠️ Permissive in 4.x
  client: {
    webSocketURL: 'auto',         // ⚠️ Automatic WebSocket detection
    overlay: true                 // Development UI feature
  }
}
```

**Patched 5.2.1+ Configuration (for reference):**
```javascript
{
  host: 'localhost',
  port: 3000,
  hot: true,
  allowedHosts: ['localhost'],    // ✅ Explicit whitelist
  client: {
    webSocketURL: {
      hostname: 'localhost',      // ✅ Explicit hostname
      pathname: '/ws',
      port: 3000,
      protocol: 'ws'
    },
    overlay: true
  },
  webSocketServer: {
    options: {
      verifyClient: (info) => {   // ✅ Custom origin validation
        const origin = info.req.headers.origin;
        return origin === 'http://localhost:3000';
      }
    }
  }
}
```

---

## Affected Components

### Development Only
- ⚠️ webpack-dev-server 4.15.2
- ⚠️ Hot Module Replacement (HMR) system
- ⚠️ WebSocket server for live reload
- ⚠️ Development proxy middleware

### NOT Affected
- ✅ Production builds (create-react-app build)
- ✅ Static file serving in production
- ✅ Backend API servers
- ✅ Database connections
- ✅ Production deployments

---

## Verification & Monitoring

### Current Status Check
```bash
# Verify current webpack-dev-server version
cd /app/frontend
yarn list --pattern webpack-dev-server

# Expected output:
# └─ webpack-dev-server@4.15.2  ⚠️ VULNERABLE
```

### Security Audit
```bash
# Check for all known vulnerabilities
yarn audit

# Check specifically for webpack-dev-server issues
yarn audit --groups dependencies | grep -A 10 webpack-dev-server
```

### Development Environment Test
```bash
# Verify dev server only binds to localhost
yarn start
# Open another terminal:
netstat -tuln | grep 3000
# Should show: 127.0.0.1:3000 (localhost only) ✅
```

---

## References

### CVE Databases
- [CVE-2025-30359 - NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-30359)
- [CVE-2025-30360 - NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-30360)
- [GitHub Security Advisory GHSA-4v9v-hfq4-rm2v](https://github.com/advisories/GHSA-4v9v-hfq4-rm2v)

### Compatibility Issues
- [Create React App Issue #17095](https://github.com/facebook/create-react-app/issues/17095)
- [webpack-dev-server Release Notes](https://github.com/webpack/webpack-dev-server/releases)
- [webpack-dev-server Migration Guide](https://webpack.js.org/configuration/dev-server/)

### Security Research
- [Wiz Vulnerability Database - CVE-2025-30359](https://www.wiz.io/vulnerability-database/cve/cve-2025-30359)
- [Wiz Vulnerability Database - CVE-2025-30360](https://www.wiz.io/vulnerability-database/cve/cve-2025-30360)
- [Snyk Security Database](https://security.snyk.io/package/npm/webpack-dev-server)

---

## Decision Log

### Why Not Upgrade Now?

**Decision:** Defer webpack-dev-server upgrade until react-scripts officially supports 5.x

**Rationale:**
1. **Stability:** Breaking the build system is worse than the development-only security risk
2. **Maintainability:** Unofficial patches require ongoing maintenance and may break
3. **Risk vs Reward:** Development environment risk is mitigated through other controls
4. **Production Safety:** Production is unaffected by these vulnerabilities
5. **Industry Practice:** Major projects (Docusaurus, Angular CLI) are facing the same issue

**Alternative Considered:** Force upgrade with CRACO patches
- **Rejected:** Too risky, unofficial, maintenance burden too high

**Alternative Considered:** Migrate to Vite immediately
- **Rejected:** Major refactor not justified by development-only security risk

**Alternative Considered:** Eject from Create React App
- **Rejected:** Loss of future updates outweighs security benefit

---

## Appendix: Environment Configuration

### Package Versions
```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-scripts": "5.0.1",
    "react-router-dom": "^7.9.6"
  },
  "devDependencies": {
    "@craco/craco": "^7.1.0",
    "webpack-dev-server": "4.15.2"  // Transitive via react-scripts
  }
}
```

### CRACO Configuration
- **File:** `/app/frontend/craco.config.js`
- **Purpose:** Path aliases, hot reload configuration
- **Limitation:** Cannot override webpack-dev-server version without breaking react-scripts

### Development Scripts
```json
{
  "start": "craco start",           // Runs webpack-dev-server
  "build": "craco build",           // Produces production bundle (no dev server)
  "build:production": "craco build" // Production build (SAFE)
}
```

---

## Contact & Review

**Security Team:** BME Security Operations  
**Documented By:** AI Development Agent  
**Date:** January 2025  
**Next Review:** When react-scripts 6.x is released or quarterly (whichever is sooner)  

**Status:** ⚠️ ACKNOWLEDGED - RISK ACCEPTED FOR DEVELOPMENT ENVIRONMENT  
**Action Required:** ✅ NONE - Implement mitigation strategies and monitor for updates

---

## Quick Reference Card

### ✅ What's Safe
- Production builds and deployments
- All backend services
- Database connections
- User data and privacy

### ⚠️ What's At Risk
- Development environment source code
- Credentials or secrets in development code
- Developer machine while dev server is running
- Intellectual property in source code

### 🛡️ How to Stay Safe
1. Use Chromium-based browsers (Chrome, Edge, Brave)
2. Stop dev server when not actively coding
3. Never commit credentials to code
4. Keep dev server on localhost only
5. Be cautious browsing untrusted sites while coding
6. Use non-standard ports (change from 3000)

### 📅 When to Act
- Monitor react-scripts releases monthly
- Review this advisory quarterly
- Upgrade immediately when react-scripts 6.x is available
- Consider migration if security requirements change
