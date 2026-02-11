# Chaplin-UI 🎬

<div align="center">

**Visual Speech Recognition - Read lips, transcribe speech, all locally**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

*A beautiful, open-source tool that reads your lips in real-time and transcribes silently mouthed speech using local ML models.*

[Quick Start](#-quick-start) • [Contributing](./CONTRIBUTING.md) • [Privacy](./PRIVACY.md) • [Security](./SECURITY.md) • [Documentation](#-documentation) • [License](./LICENSE.md)

</div>

---

## ✨ What is Chaplin-UI?

Chaplin-UI is a visual speech recognition (VSR) application that can transcribe speech just by watching your lips move. This project is based on [Chaplin](https://github.com/amanvirparhar/chaplin) by [Amanvir Parhar](https://amanvir.com), with added web interface and UI improvements. Perfect for:

- 🎤 **Silent communication** - Type without speaking
- 🔒 **Privacy-first** - Everything runs locally on your machine ([Privacy Policy](./PRIVACY.md))
- 🌐 **Web-based** - Works in any modern browser
- 🎨 **Beautiful UI** - Apple HIG-inspired design

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (check with `python3 --version`)
- **LM Studio** ([download here](https://lmstudio.ai/)) - For LLM text correction
- **Modern web browser** with camera access

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/loganngarcia/chaplin-ui.git
   cd chaplin-ui
   ```

2. **Set up Python environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Download model files:**
   ```bash
   ./setup.sh
   ```
   This downloads the VSR model from Hugging Face (~500MB).

4. **Start LM Studio:**
   - Open LM Studio
   - Load a model (we recommend `zai-org/glm-4.6v-flash`)
   - Go to **Developer** tab → Enable **Local Server** (port 1234)

5. **Run the web app:**
   ```bash
   ./run_web.sh
   ```
   Then open [http://localhost:8000](http://localhost:8000) in your browser!

## 📖 Documentation

### Project Structure

```
chaplin-ui/
├── chaplin_ui/              # Core shared modules
│   └── core/                # Shared utilities, models, configs
│       ├── models.py        # Pydantic data models
│       ├── constants.py     # All configuration constants
│       ├── llm_client.py    # LLM API wrapper
│       ├── video_processor.py # Video processing utilities
│       └── ...
├── web/                     # Web app frontend
│   ├── index.html          # Main HTML
│   ├── style.css           # Styles (Apple HIG)
│   └── app.js              # Frontend logic
├── web_app.py              # FastAPI backend server
├── chaplin.py              # CLI implementation
├── main.py                 # CLI entry point
└── pipelines/              # VSR model pipeline
```

### How It Works

1. **Video Capture**: Camera records video frames (or upload existing video)
2. **Face Detection**: MediaPipe detects and tracks your face
3. **VSR Inference**: LRS3 model processes lip movements → raw text (ALL CAPS)
4. **LLM Correction**: LM Studio corrects grammar, adds punctuation, formats text
5. **Display**: Shows both raw and corrected transcription

### Key Components

- **`chaplin_ui/core/`** - Shared code used by CLI and Web interfaces
- **`web_app.py`** - FastAPI server handling video uploads and processing
- **`chaplin.py`** - CLI version with keyboard typing
- **`pipelines/`** - VSR model inference pipeline

## 🛠️ Development

### Running Locally

**Web App:**
```bash
source .venv/bin/activate
python web_app.py
```

**CLI:**
```bash
source .venv/bin/activate
python main.py config_filename=./configs/LRS3_V_WER19.1.ini detector=mediapipe
```

### Code Style

We follow Python best practices:
- **Type hints** on all functions
- **Docstrings** (Google style) for all public functions
- **Logging** instead of print statements
- **Constants** centralized in `chaplin_ui/core/constants.py`

### Testing

```bash
# Test imports
python -c "from chaplin_ui.core import *; print('✓ All imports work')"

# Test web app
python web_app.py &
curl http://localhost:8000/api/health
```

## 🤝 Contributing

We love contributions! Whether it's:
- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🎨 UI/UX enhancements
- 🔧 Code refactoring

See our [Contributing Guide](./CONTRIBUTING.md) for details on:
- How to set up your development environment
- Code style guidelines
- How to submit pull requests
- Where to ask questions

**First time contributing?** Check out our [good first issues](https://github.com/loganngarcia/chaplin-ui/labels/good%20first%20issue)!

## 📝 License

This project is licensed under the MIT License - see [LICENSE.md](./LICENSE.md) for details.

## 🙏 Acknowledgments

### Original Creator

Chaplin-UI is based on [Chaplin](https://github.com/amanvirparhar/chaplin) by **[Amanvir Parhar](https://amanvir.com)**. We're grateful for the original work that made this project possible!

### Additional Credits

- **VSR Model**: Based on [Auto-AVSR](https://github.com/mpc001/auto_avsr) by mpc001
- **Dataset**: [Lip Reading Sentences 3](https://mmai.io/datasets/lip_reading/)
- **LLM**: Uses LM Studio for local text correction

## 💬 Community

- 🐛 **Found a bug?** [Open an issue](https://github.com/loganngarcia/chaplin-ui/issues)
- 💡 **Have an idea?** [Start a discussion](https://github.com/loganngarcia/chaplin-ui/discussions)
- 📧 **Questions?** Check our [FAQ](./CONTRIBUTING.md#faq) or open a discussion

---

<div align="center">

**Made with ❤️ by the open source community**

[⭐ Star us on GitHub](https://github.com/loganngarcia/chaplin-ui) • [📖 Read the docs](#-documentation) • [🤝 Contribute](./CONTRIBUTING.md)

</div>
