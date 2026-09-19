# SkyLines Security Audit Report

**Date:** September 2026  
**Scope:** Read-only security review of skylines-project/skylines (master branch)  
**Context:** Python 2.7 / Flask 1.1.2 + Ember 3.24 + PostGIS platform; Docker Compose deployment (#2601)  
**TLS:** External reverse proxy (assumed to terminate TLS before Caddy)

---

## Executive Summary

This audit identifies several security issues ranging from **Critical** to **Medium** severity, plus significant **Platform Debt** from Python 2.7 EOL. The codebase was designed for a different era of web security, but remains reasonably structured. The most pressing issues are the hardcoded default `SECRET_KEY` values and the permissive CORS configuration.

---

## 1. Critical / High Severity Findings

### 1.1 CRITICAL: Hardcoded Default `SECRET_KEY` Values

**Files:**
- `config/default.py:12` — `SECRET_KEY = "skylines"`
- `config/docker.py:10` — `SECRET_KEY = os.getenv("SECRET_KEY", "skylines-docker")`

**Impact:** The `SECRET_KEY` is used to sign JWT access tokens via `itsdangerous.JSONWebSignatureSerializer`. If an attacker knows this key, they can forge valid access tokens for any user, including administrators.

**Exploit Path:**
1. Attacker reads the public source code or guesses the default key
2. Attacker crafts a JWT payload: `{"user": 1, "exp": <future_timestamp>}`
3. Signs with `SECRET_KEY = "skylines"` or `"skylines-docker"`
4. Sends forged token in `Authorization: Bearer <token>` header
5. Gains full authenticated access as any user (including admin)

**Evidence (`skylines/api/oauth.py:32-41`):**
```python
app.jws = JSONWebSignatureSerializer(app.config.get("SECRET_KEY"))
# ...
token = {"user": request.user.id, "exp": int(time.time() + request.expires_in)}
return current_app.jws.dumps(token).decode("ascii")
```

**Recommendation (Pre-Cutover):**
- **Mandatory:** Never deploy without setting `SECRET_KEY` environment variable
- Remove default fallback in `config/docker.py` — fail fast if unset:
  ```python
  SECRET_KEY = os.environ["SECRET_KEY"]  # Crash if missing
  ```
- The `.env.example` already documents this, but compose validation should enforce it

---

### 1.2 HIGH: Overly Permissive CORS Configuration

**File:** `skylines/api/cors.py:14-30`

**Impact:** The CORS handler reflects any `Origin` header back as `Access-Control-Allow-Origin` with `Access-Control-Allow-Credentials: true`. This allows any malicious website to make authenticated cross-origin requests on behalf of logged-in users.

**Exploit Path:**
1. User is logged into skylines.aero with a valid session/token
2. User visits attacker's malicious site (e.g., `evil.com`)
3. Malicious JavaScript makes `fetch()` calls to `skylines.aero/api/*`
4. Browser sends credentials (cookies/tokens stored in localStorage)
5. CORS headers allow `evil.com` to read responses
6. Attacker can read user data, modify flights, delete account, etc.

**Evidence:**
```python
if "Origin" in request.headers:
    response.headers.add(
        "Access-Control-Allow-Origin", request.headers.get("Origin")
    )
    response.headers.add("Access-Control-Allow-Credentials", "true")
```

**Recommendation (Pre-Cutover):**
```python
ALLOWED_ORIGINS = {"https://skylines.aero", "https://www.skylines.aero"}

@staticmethod
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        # ... other headers
    return response
```

---

### 1.3 HIGH: Password Recovery Key Exposure to Admins

**File:** `skylines/api/views/users.py:100-103`

**Impact:** Admin users can request password recovery for any user and receive the recovery URL directly in the response, bypassing the email flow entirely.

**Exploit Path:**
1. Compromised admin account (or malicious admin)
2. POST `/users/recover` with target user's email
3. Response includes full recovery URL: `http://skylines.aero/users/recover?key=<hex>`
4. Admin can now reset any user's password

**Evidence:**
```python
current_user = User.get(request.user_id) if request.user_id else None
if current_user and current_user.admin:
    url = u"http://skylines.aero/users/recover?key=%x" % user.recover_key
    return jsonify(url=url)
```

**Recommendation (Pre-Cutover):**
- Remove this admin shortcut entirely, or
- Log all admin password reset requests for audit, and
- Require additional confirmation/2FA for admin actions

---

### 1.4 HIGH: Weak Password Recovery Key (32-bit)

**File:** `skylines/model/user.py:228-232`

**Impact:** The recovery key is only 31 bits of entropy (`& 0x7FFFFFFF`), making brute-force feasible. At ~2 billion possibilities, an attacker could enumerate all keys with sustained effort.

**Evidence:**
```python
def generate_recover_key(self, ip):
    self.recover_key = struct.unpack("I", os.urandom(4))[0] & 0x7FFFFFFF
```

**Recommendation (Post-Cutover):**
- Use cryptographically strong tokens (128+ bits), URL-safe base64 encoded
- Add expiration check (currently `recover_time` exists but isn't validated)
- Add rate limiting on the recovery endpoint

---

## 2. Medium Severity Findings

### 2.1 MEDIUM: No CSRF Protection

**Files:** All API endpoints; no CSRF middleware detected

**Impact:** State-changing requests (POST, PUT, DELETE) have no CSRF token validation. Combined with the permissive CORS (§1.2), this allows full CSRF attacks.

**Note:** The API is primarily used by the Ember SPA with bearer tokens, which provides some protection. However, if cookies are ever used or if the CORS issue is only partially fixed, CSRF remains exploitable.

**Recommendation:** Implement CSRF protection or ensure all state-changing operations require bearer tokens (not cookies).

---

### 2.2 MEDIUM: No Rate Limiting

**Files:** No rate limiting middleware found in codebase

**Affected Endpoints:**
- `POST /oauth/token` — password brute-force
- `POST /users/recover` — recovery key enumeration
- `POST /users` — account creation spam
- `POST /flights/upload` — resource exhaustion

**Recommendation (Pre-Cutover):**
- Add rate limiting at reverse proxy (Caddy or upstream nginx)
- Consider Flask-Limiter for application-level limits on auth endpoints

---

### 2.3 MEDIUM: Debug Mode Enabled by Default

**File:** `config/default.py:11`

```python
DEBUG = True
```

**Impact:** If `config/docker.py` isn't properly loaded, the app runs with debug mode enabled, potentially exposing stack traces and sensitive information.

**Note:** `config/docker.py` correctly defaults `DEBUG = False` based on env var, but relies on `SKYLINES_CONFIG` being set.

**Recommendation:**
- Add explicit `DEBUG = False` as the first line in `config/docker.py`
- Ensure compose always sets `SKYLINES_CONFIG`

---

### 2.4 MEDIUM: Tracking Key Only 32-bit

**File:** `skylines/model/user.py:206-207`

**Impact:** User tracking keys (used for live GPS tracking authentication) are only 32 bits, making collision or brute-force attacks possible on the UDP tracking protocol.

**Evidence:**
```python
def generate_tracking_key(self):
    self.tracking_key = struct.unpack("I", os.urandom(4))[0]
```

**Recommendation (Post-Cutover):**
- Consider longer keys for new users
- Add rate limiting on tracking server (currently none)

---

### 2.5 MEDIUM: UDP Tracking Protocol Has No Replay Protection

**File:** `skylines/tracking/server.py`

**Impact:** The XCSoar tracking protocol uses CRC for integrity but has no sequence numbers or timestamps that prevent replay attacks. An attacker who captures tracking packets can replay them.

**Recommendation (Post-Cutover):**
- Accept this as a protocol limitation, or
- Add server-side deduplication based on timestamp + tracking key

---

### 2.6 MEDIUM: Widgets Endpoint Allows Arbitrary JSONP Callback

**File:** `skylines/frontend/views/widgets.py:20, 53-54`

**Impact:** The `callback` parameter is rendered directly into JavaScript output without validation, potentially enabling XSS if the callback name contains malicious characters.

**Evidence:**
```python
callback = request.values.get("callback", "onFlightsLoaded")
return wrap(callback, render_template("widgets/flights.jinja", flights=flights))
```

**Template (`widgets/wrapper.jinja`):**
```jinja
{{ callback }}('{{ content }}');
```

**Recommendation:** Validate callback name against `^[a-zA-Z_][a-zA-Z0-9_.]*$`

---

### 2.7 MEDIUM: JWT Uses JWS (Signature Only), Not JWE (Encryption)

**File:** `skylines/api/oauth.py:4, 32`

**Impact:** Access tokens are signed but not encrypted. The `user` ID and expiration are visible to anyone who decodes the base64 token. This is information disclosure, not a direct exploit.

**Recommendation:** Accept as low risk (user IDs are not secret), but document that tokens should not contain sensitive data.

---

## 3. Docker Hardening for Cutover

### 3.1 HIGH: Containers Run as Root

**File:** `Dockerfile` (no USER directive)

**Impact:** All containers run as root, increasing blast radius if any container is compromised.

**Recommendation:**
```dockerfile
RUN useradd -r -s /bin/false skylines
USER skylines
```
Note: Requires adjusting file permissions for `/home/skylines/code/htdocs/files`

---

### 3.2 HIGH: Celery Running as Root

**Files:** `docker-compose.yml:17`, `docker-compose.prod.yml:40`

```yaml
C_FORCE_ROOT: "1"
```

**Impact:** Celery explicitly allows running as root, which is discouraged for security.

**Recommendation:** Run Celery worker container as non-root user (see §3.1)

---

### 3.3 MEDIUM: UDP Tracking Port Exposed to Internet

**File:** `docker-compose.prod.yml:129`

```yaml
ports:
  - "${TRACKING_PORT:-5597}:5597/udp"
```

**Impact:** The tracking server is directly exposed. While this is required for XCSoar devices, it increases attack surface.

**Recommendation:**
- Document that 5597/udp should be firewalled to expected IP ranges if possible
- Monitor for abuse (high volume from single IP)

---

### 3.4 MEDIUM: Image Tags Not Pinned to Digests

**Files:** `docker-compose.yml`, `docker-compose.prod.yml`

```yaml
image: postgis/postgis:12-2.5
image: redis:8-alpine
image: caddy:2-alpine
```

**Impact:** Mutable tags can be replaced with compromised images in supply chain attacks.

**Recommendation:** Pin to SHA256 digests:
```yaml
image: postgis/postgis:12-2.5@sha256:<digest>
```

---

### 3.5 LOW: Default PostgreSQL Credentials in Dev Compose

**File:** `docker-compose.yml:33`

```yaml
POSTGRES_PASSWORD: postgres
```

**Impact:** Only affects development; prod compose requires env vars. Low risk.

**Recommendation:** Keep as-is for dev; prod compose correctly uses `${POSTGRES_PASSWORD:?...}`

---

### 3.6 INFO: Security Headers in Caddyfile.prod

**File:** `docker/Caddyfile.prod:40-47`

```
header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "SAMEORIGIN"
    Referrer-Policy "strict-origin-when-cross-origin"
    -Server
}
```

**Status:** Good security headers are configured. Consider adding:
- `Content-Security-Policy` (complex for SPA, but worth investigating)
- `Permissions-Policy` to disable unnecessary browser features

---

## 4. Platform Debt: Python 2.7 EOL

### 4.1 CRITICAL-DEBT: Python 2.7 End of Life

**Files:** `Pipfile:7`, `Dockerfile:36-50`

**Impact:** Python 2.7 reached end-of-life January 1, 2020. No security patches are released. All Python dependencies are frozen at old, potentially vulnerable versions.

**Vulnerable Dependency Examples:**
- `werkzeug==0.15.3` — multiple CVEs fixed in later versions
- `requests==2.22.0` — old, though no critical CVEs
- `flask==1.1.2` — outdated
- `celery==3.1.26` — very old major version

**Recommendation:** 
- **Long-term:** Migrate to Python 3.9+ (significant effort)
- **Short-term:** Accept risk, minimize internet-exposed surface, apply container isolation

---

### 4.2 HIGH-DEBT: Debian Buster Archived

**File:** `Dockerfile:43-46`

```dockerfile
RUN echo "deb http://archive.debian.org/debian buster main" > /etc/apt/sources.list
```

**Impact:** Buster is archived and receives no security updates. System libraries may have unpatched vulnerabilities.

**Recommendation:** Same as Python 2.7 — requires migration to maintain security

---

## 5. Positive Security Observations

1. **Password Hashing:** Uses SHA-256 with salt (`skylines/model/user.py:166-179`). While not bcrypt/argon2, it's reasonable.

2. **SQL Injection Protection:** ORM (SQLAlchemy) is used consistently. No raw SQL with user input concatenation found.

3. **Path Traversal Protection:** `skylines/lib/files.py:15-39` properly sanitizes filenames using `os.path.basename()` and character filtering.

4. **File Upload Validation:** IGC files are parsed/validated before storage.

5. **User-Agent Requirement:** API requires User-Agent header, providing minimal bot filtering.

6. **No Server-Side Template Injection:** API responses are JSON; Jinja templates are minimal and don't interpolate user input into code.

---

## 6. Recommended Fix Priority

### Pre-Cutover (Block Deployment)

| Priority | Finding | Effort |
|----------|---------|--------|
| P0 | §1.1 Hardcoded SECRET_KEY | 10 min |
| P0 | §1.2 Permissive CORS | 30 min |
| P1 | §3.1 Containers as root | 1 hour |
| P1 | §2.2 Rate limiting (proxy) | 30 min |
| P1 | §1.3 Admin recovery URL leak | 15 min |

### Post-Cutover (Next Sprint)

| Priority | Finding | Effort |
|----------|---------|--------|
| P2 | §1.4 Weak recovery key | 1 hour |
| P2 | §2.6 JSONP callback validation | 15 min |
| P2 | §3.4 Image pinning | 30 min |
| P3 | §2.4 Tracking key length | 2 hours |
| P3 | §2.1 CSRF protection | 4 hours |

### Long-Term Technical Debt

| Priority | Finding | Effort |
|----------|---------|--------|
| P4 | §4.1 Python 3 migration | Weeks |
| P4 | §4.2 Bookworm base image | Included above |

---

## 7. Conclusion

The SkyLines codebase is reasonably secure for its era but requires immediate attention to the `SECRET_KEY` and CORS issues before production Docker deployment. The Python 2.7 technical debt is the largest long-term security liability and should be prioritized for migration.

For questions about this audit, please reference the finding numbers (e.g., §1.2) and file paths provided.
