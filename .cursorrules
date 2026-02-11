# Chaplin-UI Cursor Rules

## 🎯 Core Principle

**When implementing any feature or making changes, update ALL relevant files to maintain consistency across the entire codebase.**

## 📋 Feature Implementation Checklist

When implementing a new feature or modifying existing functionality, always:

### 1. Code Changes
- [ ] Update core logic in appropriate modules (`chaplin_ui/core/`, `web_app.py`, `chaplin.py`, etc.)
- [ ] Update constants in `chaplin_ui/core/constants.py` if adding new config values
- [ ] Update models in `chaplin_ui/core/models.py` if data structures change
- [ ] Update frontend (`web/app.js`, `web/index.html`, `web/style.css`) if UI changes
- [ ] Update backend (`web_app.py`) if API changes
- [ ] Update CLI (`chaplin.py`, `main.py`) if CLI functionality changes

### 2. Configuration
- [ ] Add new constants to `chaplin_ui/core/constants.py` (don't hardcode values)
- [ ] Update `chaplin_ui/core/config.py` if config structure changes
- [ ] Update `hydra_configs/default.yaml` if CLI config changes
- [ ] Update `.gitignore` if new file patterns need ignoring

### 3. Documentation
- [ ] Update `README.md` if:
  - New features are added
  - Setup instructions change
  - Usage changes
  - Dependencies change
- [ ] Update `CONTRIBUTING.md` if:
  - Development workflow changes
  - Code style guidelines change
  - New contribution areas added
- [ ] Update `PRIVACY.md` if:
  - Data handling changes
  - New external services are integrated
  - Logging behavior changes
- [ ] Update `SECURITY.md` if:
  - Security considerations change
  - New vulnerabilities are addressed
  - Deployment process changes
- [ ] Update inline code comments and docstrings

### 4. Dependencies
- [ ] Update `requirements.txt` if new Python packages are added
- [ ] Update setup instructions if new system dependencies are needed
- [ ] Document version requirements if compatibility matters

### 5. Examples & Tests
- [ ] Update code examples in docstrings if APIs change
- [ ] Update usage examples in README if workflow changes
- [ ] Consider adding/updating tests if testable functionality changes

## 🔄 Cross-File Consistency Rules

### Constants
- **NEVER** hardcode values that should be configurable
- **ALWAYS** add to `chaplin_ui/core/constants.py` first
- **ALWAYS** import from constants instead of duplicating values
- **ALWAYS** document what each constant does with inline comments

### UI Changes
- **ALWAYS** update both web app AND CLI if feature affects both
- **ALWAYS** use CSS variables from `style.css` for colors
- **ALWAYS** maintain Apple HIG design principles
- **ALWAYS** ensure responsive design (mobile-friendly)

### API Changes
- **ALWAYS** update both frontend (`web/app.js`) and backend (`web_app.py`)
- **ALWAYS** update API documentation in docstrings
- **ALWAYS** consider backward compatibility
- **ALWAYS** update error handling consistently

### Logging
- **ALWAYS** use `logger.debug()` for sensitive data (transcriptions)
- **ALWAYS** use `logger.info()` for important events
- **ALWAYS** use `logger.warning()` for recoverable issues
- **ALWAYS** use `logger.error()` for failures
- **ALWAYS** import logger from `chaplin_ui.core.logging_config`

## 🎨 Code Quality Standards

### Type Hints
- **ALWAYS** use type hints on function parameters and return types
- **ALWAYS** import types from `typing` module when needed
- **ALWAYS** use `Optional[T]` instead of `T | None` for Python < 3.10

### Docstrings
- **ALWAYS** write Google-style docstrings for public functions
- **ALWAYS** include Args, Returns, Raises sections
- **ALWAYS** add usage examples for complex functions
- **ALWAYS** explain "why" not just "what" in comments

### Error Handling
- **ALWAYS** handle errors gracefully with appropriate logging
- **ALWAYS** provide helpful error messages
- **ALWAYS** clean up resources in `finally` blocks
- **ALWAYS** use specific exception types, not bare `except:`

### Naming
- **ALWAYS** use `snake_case` for functions and variables
- **ALWAYS** use `PascalCase` for classes
- **ALWAYS** use `UPPER_SNAKE_CASE` for constants
- **ALWAYS** use descriptive names (avoid abbreviations)

## 🔒 Privacy & Security

### Privacy
- **NEVER** log sensitive data (transcriptions) at INFO level or above
- **ALWAYS** use `logger.debug()` for transcription text
- **ALWAYS** clean up temporary files
- **ALWAYS** document data handling in PRIVACY.md

### Security
- **ALWAYS** add security warnings for production deployments
- **ALWAYS** document CORS, authentication, rate limiting needs
- **ALWAYS** validate user input
- **ALWAYS** use environment variables for secrets

## 📝 Documentation Updates

### When to Update README.md
- New features added
- Setup process changes
- Usage examples change
- Dependencies added/removed
- Troubleshooting steps added

### When to Update CONTRIBUTING.md
- Development setup changes
- Code style guidelines change
- New contribution areas
- Testing procedures change

### When to Update PRIVACY.md
- Data collection changes
- External services added
- Logging behavior changes
- Storage behavior changes

### When to Update SECURITY.md
- Security vulnerabilities addressed
- New security measures added
- Deployment process changes
- Authentication methods change

## 🚀 Feature Implementation Workflow

1. **Understand the request** - What exactly needs to change?
2. **Identify affected files** - Which files need updates?
3. **Plan the changes** - What needs to be modified in each file?
4. **Implement systematically**:
   - Start with core logic
   - Update constants/config
   - Update UI (if applicable)
   - Update API (if applicable)
   - Update documentation
5. **Verify consistency** - Are all related files updated?
6. **Test the changes** - Does everything work together?

## 💡 Examples

### Example 1: Adding a new video format
- ✅ Update `SUPPORTED_VIDEO_FORMATS` in `constants.py`
- ✅ Update validation in `web_app.py`
- ✅ Update error messages
- ✅ Update README.md with new format
- ✅ Update PRIVACY.md if format affects privacy

### Example 2: Adding a new UI feature
- ✅ Update `web/index.html` (structure)
- ✅ Update `web/style.css` (styling)
- ✅ Update `web/app.js` (behavior)
- ✅ Update `web_app.py` (backend if needed)
- ✅ Update README.md (documentation)
- ✅ Update CONTRIBUTING.md (if affects dev workflow)

### Example 3: Changing LLM behavior
- ✅ Update `chaplin_ui/core/llm_client.py` (logic)
- ✅ Update `chaplin_ui/core/constants.py` (config)
- ✅ Update `web_app.py` (if API changes)
- ✅ Update `chaplin.py` (if CLI changes)
- ✅ Update PRIVACY.md (data handling)
- ✅ Update README.md (usage)

## ⚠️ Common Mistakes to Avoid

- ❌ **DON'T** implement a feature in only one file
- ❌ **DON'T** forget to update documentation
- ❌ **DON'T** hardcode values that should be constants
- ❌ **DON'T** forget to update both web and CLI if both affected
- ❌ **DON'T** log sensitive data at INFO level
- ❌ **DON'T** skip error handling
- ❌ **DON'T** forget to update examples in docstrings

## 🎯 Remember

**The goal is maintainability and consistency. When in doubt, update more files rather than fewer. It's better to be thorough than to leave inconsistencies.**
