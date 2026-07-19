# Security Standards - BrahmaVidya Galaxy

## 1. Authentication & Session Integrity
- **Access Tokens (JWT)**: Short-lived tokens (expires in 15 minutes) carrying the user's immediate session profile and active scope.
- **Refresh Tokens**: Long-lived tokens stored exclusively inside secure, `HttpOnly` cookies. The browser cannot read these values via script, protecting them from XSS.
- **Token Rotation**: Each refresh request invalidates the old token and issues a new pairing, preventing reuse.

---

## 2. Dynamic Input Control & XSS Mitigation
- **Markdown Sanitization**: All rich text learning blocks, instructor bios, and dynamic texts must be processed before rendering using a strict sanitization pipeline.
- **Form Controls**: Administrative form inputs must validate parameter length and character lists before execution:
  - Slugs must match standard URL characters: `^[a-z0-9-_]+$`.
  - Layout blocks JSON arrays must be verified by `JSON.parse` blocks catching nested script vectors.
- **Query Protection**: Database operations must use parameterized queries exclusively. Manual SQL string concatenations are forbidden.

---

## 3. Cryptographic Signature Rules (Certificate Verification)
- **Hash Seeding**: Certificate validation keys must not use guessable sequential patterns.
- **Hash Formulation**: Calculated as `SHA-256(recipient_id + course_id + issue_timestamp + secret_salt)`.
- **Integrity Checks**: The public verification view (`/verify/:hash`) must check database records for matching signatures. No fake client-side verification is permitted.

---

## 4. API Throttling & Security Rules
- **Rate Limiting**: Public endpoints (login, registration, certificate verification) must enforce request thresholds:
  - Max 100 requests per 15 minutes per IP address.
  - Verification calls: Max 10 calls per minute per IP.
- **Cross-Origin Resource Sharing (CORS)**: Strict rules limit resource sharing to registered frontend subdomains:
```typescript
const allowedOrigins = ['https://brahmavidya.edu', 'https://galaxy.brahmavidya.edu'];
```
- **Security Headers**: Standard security headers (such as `Helmet` or Nginx rules) must be configured on our ingress:
  - `Content-Security-Policy`: Standard scripts and fonts only.
  - `X-Frame-Options: DENY` (or limit to permitted frames).
  - `Strict-Transport-Security` (forcing HTTPS).
