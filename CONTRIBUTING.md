# Contributing to Chaplin-UI

First off, thank you for considering contributing to Chaplin-UI! 🎉 We're excited to have you here.

This document provides guidelines and instructions for contributing. Feel free to suggest improvements!

## 🎯 How Can I Contribute?

### Reporting Bugs

Found a bug? Great! Here's how to report it:

1. **Check existing issues** - Someone might have already reported it
2. **Create a new issue** with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, browser)
   - Screenshots if applicable

### Suggesting Features

Have an idea? We'd love to hear it!

1. **Check existing discussions** - See if it's been discussed
2. **Start a discussion** or **open an issue** with:
   - Clear description of the feature
   - Use case / problem it solves
   - Potential implementation approach (if you have ideas)

### Code Contributions

Ready to write code? Awesome! Here's the process:

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/chaplin-ui.git
cd chaplin-ui
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development tools (optional but recommended)
pip install black ruff mypy
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

## 📝 Code Style Guidelines

### Python Code

- **Type hints**: Use type hints on all function parameters and return types
- **Docstrings**: Use Google-style docstrings for all public functions
- **Naming**: 
  - Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Line length**: Keep lines under 100 characters when possible
- **Imports**: Group imports: stdlib, third-party, local (separated by blank lines)

### Example:

```python
from typing import Optional

def process_video(
    video_path: str,
    output_format: str = "mp4",
) -> Optional[str]:
    """Process a video file and return output path.
    
    Args:
        video_path: Path to input video file.
        output_format: Desired output format (default: mp4).
        
    Returns:
        Path to processed video, or None if processing failed.
    """
    # Implementation here
    pass
```

### Frontend Code (JavaScript/CSS)

- **JavaScript**: Use modern ES6+ syntax, meaningful variable names
- **CSS**: Use CSS variables for colors, follow Apple HIG guidelines
- **Comments**: Add comments for complex logic

## 🔍 Code Structure

### Where to Put Your Code

- **New shared utilities** → `chaplin_ui/core/`
- **Web app changes** → `web_app.py` or `web/`
- **CLI changes** → `chaplin.py` or `main.py`
- **VSR pipeline changes** → `pipelines/`
- **Configuration** → `chaplin_ui/core/constants.py` or `configs/`

### Key Principles

1. **DRY (Don't Repeat Yourself)**: Use shared modules in `chaplin_ui/core/`
2. **Single Responsibility**: Each function should do one thing well
3. **Clear Naming**: Function names should describe what they do
4. **Error Handling**: Always handle errors gracefully with logging

## 🧪 Testing Your Changes

### Before Submitting

1. **Test your changes:**
   ```bash
   # Test imports
   python -c "from chaplin_ui.core import *"
   
   # Test web app starts
   python web_app.py &
   curl http://localhost:8000/api/health
   ```

2. **Check for obvious issues:**
   - No syntax errors
   - Imports work correctly
   - No obvious bugs

### Manual Testing Checklist

- [ ] Web app starts without errors
- [ ] Camera access works
- [ ] Video upload works
- [ ] Recording works
- [ ] Transcription appears
- [ ] Copy button works

## 📤 Submitting Changes

### Commit Messages

Write clear, descriptive commit messages:

```bash
# Good
git commit -m "Add support for MP4 video upload"
git commit -m "Fix camera initialization error on macOS"
git commit -m "Improve error messages in LLM client"

# Avoid
git commit -m "fix stuff"
git commit -m "updates"
```

### Pull Request Process

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub with:
   - Clear title and description
   - What changed and why
   - How to test
   - Screenshots (if UI changes)

3. **Wait for review** - We'll review and provide feedback

4. **Make requested changes** - We'll work together to get it merged!

## 🎨 UI/UX Contributions

### Design Principles

- Follow **Apple Human Interface Guidelines** for colors and styling
- Keep it **simple and intuitive**
- Ensure **accessibility** (keyboard navigation, screen readers)
- Make it **responsive** (works on different screen sizes)

### UI Components

- Colors: Use CSS variables from `style.css`
- Buttons: No borders, use Apple system colors
- Typography: System fonts (`-apple-system`, etc.)
- Spacing: Consistent padding/margins

## 🐛 Debugging Tips

### Common Issues

**Import errors:**
```bash
# Make sure you're in the project root
cd /path/to/chaplin-ui
source .venv/bin/activate
python -c "import sys; print(sys.path)"
```

**Model not loading:**
- Check that `setup.sh` ran successfully
- Verify model files exist in `benchmarks/LRS3/`
- Check config file path in `configs/`

**LLM errors:**
- **Ollama**: Verify `ollama serve` is running, try `ollama list` and `curl http://localhost:11434/v1/models`
- **LM Studio**: Verify Local Server is enabled (port 1234), try `curl http://localhost:1234/v1/models`

## 📚 Learning Resources

### Understanding the Codebase

- **Start here**: `web_app.py` - Main web server entry point
- **Core modules**: `chaplin_ui/core/` - Shared utilities
- **VSR pipeline**: `pipelines/pipeline.py` - Model inference
- **Frontend**: `web/app.js` - Browser-side logic

### Key Concepts

- **VSR (Visual Speech Recognition)**: Converting lip movements to text
- **MediaPipe**: Face detection and tracking
- **FastAPI**: Web framework for the backend
- **AsyncIO**: Handling async operations (LLM calls)

## ❓ FAQ

**Q: Do I need to understand ML to contribute?**  
A: Not at all! There's plenty to do: UI improvements, bug fixes, documentation, testing, etc.

**Q: How do I test without Ollama or LM Studio?**  
A: The app will fall back to local text formatting if the LLM is unavailable. Pick your provider in the web UI (Ollama or LM Studio) before processing.

**Q: Can I work on multiple features at once?**  
A: It's better to focus on one feature per PR for easier review.

**Q: What if my PR needs changes?**  
A: That's totally normal! We'll provide feedback and work together to improve it.

## 💡 Ideas for Contributions

### Good First Issues

- Add keyboard shortcuts (e.g., Space to record, Ctrl/Cmd+C to copy)
- Enhance error messages (more specific, actionable feedback)
- Export transcriptions (save to file, download as text/JSON)
- Transcription history (save previous transcriptions)
- Performance optimizations (faster model loading, caching)
- Add unit tests (test core functions, API endpoints)
- Improve documentation (add examples, tutorials, API docs)
- Accessibility improvements (ARIA labels, keyboard navigation)

### Advanced Contributions

- Add real-time streaming transcription (process video chunks as they're recorded)
- Support for multiple languages (detect language, translate output)
- Custom model training pipeline (fine-tune VSR model for specific use cases)
- Desktop app (Electron/Tauri wrapper for native feel)
- Batch processing (process multiple videos at once)
- Video editing integration (export transcriptions as subtitles)

## 🎉 Recognition

We believe in giving credit where credit is due! Contributors will be:
- **Listed in our README** (with your permission)
- **Credited in release notes** for significant contributions
- **Mentioned in commit messages** and PR descriptions
- **Appreciated by the community!** 🙏

All contributors are valued, whether you're fixing a typo, adding a feature, or improving documentation. Your work makes this project better for everyone!

## 📞 Getting Help

- **Questions?** Open a [discussion](https://github.com/loganngarcia/chaplin-ui/discussions)
- **Stuck?** Check existing issues or ask in discussions
- **Found a bug?** Open an issue

---

**Thank you for contributing to Chaplin-UI!** Every contribution, no matter how small, makes a difference. 🚀
