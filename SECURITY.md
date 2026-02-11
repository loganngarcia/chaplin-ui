# Security Guidelines for Production Deployment

## ⚠️ Important Security Considerations

Chaplin-UI is designed for **local use** by default. If you plan to deploy it publicly, you **must** address these security concerns:

## 🔒 Required Changes for Production

### 1. CORS Configuration

**Current (Development):**
```python
allow_origins=["*"]  # ⚠️ Allows ANY website to access your API
```

**Production Fix:**
```python
allow_origins=["https://yourdomain.com"]  # Only allow your domain
```

**Location:** `web_app.py` line 72

### 2. Host Binding

**Current (Development):**
```python
WEB_APP_HOST = "0.0.0.0"  # Exposes to entire network
```

**Production Options:**
- **Option A (Localhost only):**
  ```python
  WEB_APP_HOST = "127.0.0.1"  # Localhost only
  ```
  Then use reverse proxy (nginx) with HTTPS

- **Option B (Reverse Proxy):**
  Keep `0.0.0.0` but run behind nginx with:
  - HTTPS/TLS
  - Rate limiting
  - Authentication

**Location:** `chaplin_ui/core/constants.py`

### 3. Authentication

**Current:** No authentication - anyone can use the API

**Production Fix:** Add authentication middleware

**Example with API Key:**
```python
from fastapi import Header, HTTPException

API_KEY = os.getenv("API_KEY", "your-secret-key")

@app.post("/api/process-video")
async def process_video(
    video: UploadFile = File(...),
    api_key: str = Header(None)
):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... rest of function
```

### 4. Rate Limiting

**Current:** No rate limiting - can be abused

**Production Fix:** Add rate limiting

**Example with slowapi:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/process-video")
@limiter.limit("5/minute")  # 5 requests per minute
async def process_video(...):
    ...
```

### 5. Input Validation

**Current:** Basic file type validation

**Production Enhancements:**
- File size limits
- Video duration limits
- Content-type verification
- Malicious file detection

**Example:**
```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
contents = await video.read()
if len(contents) > MAX_FILE_SIZE:
    raise HTTPException(400, "File too large")
```

### 6. Logging

**Current:** Logs transcription text (privacy concern)

**Production Fix:** Remove sensitive data from logs

Already fixed in code (uses `logger.debug()`), but verify:
- Set log level to `WARNING` or `ERROR` in production
- Don't log transcription text
- Don't log file paths with user data

## 🛡️ Recommended Production Setup

### Architecture

```
Internet → HTTPS (nginx) → Authentication → Rate Limiting → FastAPI → Local Processing
```

### nginx Configuration Example

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;
    
    location / {
        limit_req zone=api_limit burst=5;
        
        # Basic auth (or use OAuth/JWT)
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Variables

Use environment variables for sensitive config:

```bash
export API_KEY="your-secret-key-here"
export LLM_API_KEY="your-llm-key"
export WEB_APP_HOST="127.0.0.1"
export LOG_LEVEL="WARNING"
```

Then in code:
```python
import os
API_KEY = os.getenv("API_KEY")
```

## 🔍 Security Checklist

Before deploying publicly, verify:

- [ ] CORS restricted to your domain
- [ ] Authentication implemented
- [ ] Rate limiting enabled
- [ ] HTTPS/TLS configured
- [ ] Host binding secured (127.0.0.1 or reverse proxy)
- [ ] Sensitive data removed from logs
- [ ] File size limits enforced
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies are up-to-date (`pip list --outdated`)
- [ ] Firewall rules configured
- [ ] Regular security updates scheduled

## 🚨 Common Vulnerabilities

### 1. CORS Misconfiguration
- **Risk:** Any website can make requests to your API
- **Impact:** CSRF attacks, data theft
- **Fix:** Restrict `allow_origins`

### 2. No Rate Limiting
- **Risk:** DoS attacks, resource exhaustion
- **Impact:** Server overload, high costs
- **Fix:** Add rate limiting middleware

### 3. No Authentication
- **Risk:** Unauthorized access
- **Impact:** Abuse, data processing costs
- **Fix:** Add API keys or OAuth

### 4. Logging Sensitive Data
- **Risk:** Privacy violation, data exposure
- **Impact:** GDPR violations, trust issues
- **Fix:** Use `logger.debug()` for sensitive data

### 5. File Upload Abuse
- **Risk:** Large files, malicious files
- **Impact:** Disk space exhaustion, attacks
- **Fix:** Size limits, content validation

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## 💡 Security Reporting

Found a security vulnerability? Please report it responsibly:

1. **Don't** open a public issue
2. Email security concerns privately
3. Give us time to fix before disclosure
4. We'll credit you in security advisories

---

**Remember:** Security is an ongoing process. Regularly review and update your security measures!
