# Privacy Policy & Security Considerations

## 🔒 Privacy-First Design

Chaplin-UI is designed with privacy in mind. Here's what you need to know:

## 📊 Data Collection & Processing

### What We Process

- **Video Files**: Temporarily stored on disk during processing, then immediately deleted
- **Transcription Text**: Processed locally, never sent to external servers (unless you configure external LLM)
- **Camera Feed**: Only accessed when you explicitly click "Start recording"

### What We DON'T Collect

- ❌ No user accounts or personal information
- ❌ No permanent video storage
- ❌ No analytics or tracking
- ❌ No data sent to third-party services (by default)
- ❌ No cookies or persistent storage

## 🎬 Video Processing

### Temporary Storage

- Videos are saved to temporary files during processing
- Files are **automatically deleted** after processing completes
- Files are stored in your system's temp directory (e.g., `/tmp` on Linux/Mac)
- If processing fails, cleanup still attempts to remove files

### Video Content

- Videos are processed **locally** on your machine
- No video content is sent to external servers
- The VSR model runs entirely on your device

## 📝 Transcription Data

### Logging

⚠️ **Important**: Transcription text is logged to the console/server logs by default.

**What gets logged:**
- Raw VSR output (e.g., "HELLO WORLD")
- Corrected LLM output (e.g., "Hello world.")
- Video file paths (temporary paths)

**To reduce logging:**
- Set log level to `WARNING` or `ERROR` in production
- Modify `chaplin_ui/core/logging_config.py` to exclude sensitive data

### LLM Processing

- By default, text is sent to **Ollama** or **LM Studio** running locally
  - Ollama: `localhost:11434`
  - LM Studio: `localhost:1234`
- This is **local** - no data leaves your machine
- If you configure external LLM APIs (OpenAI, etc.), text will be sent to those services
- Always review LLM API privacy policies if using external services

## 🌐 Web Application Security

### Current Settings (Development)

⚠️ **For Production Deployment:**

1. **CORS**: Currently allows all origins (`allow_origins=["*"]`)
   - **Fix**: Restrict to your domain: `allow_origins=["https://yourdomain.com"]`
   - See `web_app.py` line 72

2. **No Authentication**: API endpoints are publicly accessible
   - **Fix**: Add authentication middleware for production use
   - Consider API keys, OAuth, or basic auth

3. **No Rate Limiting**: API can be abused
   - **Fix**: Add rate limiting middleware
   - Consider using `slowapi` or similar

4. **Host Binding**: Defaults to `0.0.0.0` (all interfaces)
   - **Fix**: Use `127.0.0.1` for local-only access
   - Or use reverse proxy (nginx) for production

### Browser Permissions

- **Camera Access**: Requires explicit user permission
- **Clipboard**: Used only when you click "Copy" button
- **No persistent storage**: No cookies, localStorage, or IndexedDB

## 🔐 Security Best Practices

### For Users

1. **Run locally**: Best privacy - everything stays on your machine
2. **Review LLM settings**: If using external LLM APIs, check their privacy policies
3. **Check logs**: Review what's being logged if privacy is critical
4. **Use HTTPS**: If deploying, always use HTTPS (not HTTP)

### For Developers

1. **Review CORS settings** before deploying
2. **Add authentication** for production deployments
3. **Implement rate limiting** to prevent abuse
4. **Audit logging** - remove sensitive data from logs
5. **Use environment variables** for sensitive config (API keys, etc.)

## 📋 Compliance Considerations

### GDPR

- No personal data collection
- No user tracking
- Data processed locally
- Users control all data (can delete videos immediately)

### HIPAA

⚠️ **Not HIPAA compliant** - This tool processes video/audio which may contain PHI
- Do not use for medical/healthcare applications without proper safeguards
- Consider additional encryption and access controls

### COPPA

- No user accounts or persistent data
- Suitable for all ages
- Parental supervision recommended for camera access

## 🛡️ Threat Model

### What This Tool Protects Against

- ✅ No data exfiltration (by default)
- ✅ No persistent tracking
- ✅ Local processing only

### What This Tool Does NOT Protect Against

- ❌ Malicious code injection (if you modify code)
- ❌ Network interception (use HTTPS in production)
- ❌ Server compromise (if deployed publicly without auth)
- ❌ Log file access (if logs are readable by others)

## 🔧 Privacy Configuration

### Reduce Logging

Edit `chaplin_ui/core/logging_config.py`:

```python
# Change log level to WARNING to hide transcription text
setup_logging(level=logging.WARNING)
```

### Disable Transcription Logging

Modify `web_app.py` to remove sensitive logs:

```python
# Instead of:
logger.info(f"📝 Raw VSR output: {output}")

# Use:
logger.debug(f"📝 Raw VSR output: {output}")  # Only logs in DEBUG mode
```

### Secure Production Deployment

See `CONTRIBUTING.md` for production deployment guidelines.

## 📞 Privacy Questions?

- **Found a privacy issue?** Open an issue on GitHub
- **Have concerns?** Review the code - it's all open source!
- **Want to audit?** All data flows are visible in the codebase

## 📝 Summary

**Chaplin-UI is privacy-friendly because:**
- ✅ Everything runs locally
- ✅ No data collection
- ✅ No external tracking
- ✅ Temporary files auto-delete
- ✅ Open source (you can verify)

**But remember:**
- ⚠️ Logs contain transcription text
- ⚠️ Configure CORS/auth for production
- ⚠️ Review LLM API privacy if using external services

---

**Last Updated**: 2025-02-10
