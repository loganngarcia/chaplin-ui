# Chaplin-UI 🎬
![chaplin-ui](https://github.com/user-attachments/assets/529823f7-8766-41ed-87d9-c18b178dc1e0)

<div align="center">

**Visual Speech Recognition - Read lips, transcribe speech, all locally**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

*A beautiful, open-source tool that reads your lips in real-time and transcribes silently mouthed speech using local ML models.*

[Quick Start](#-quick-start) • [Contributing](./CONTRIBUTING.md) • [Privacy](./PRIVACY.md) • [Security](./SECURITY.md) • [Documentation](#-documentation) • [License](./LICENSE)

</div>

---

## ✨ What is Chaplin-UI?

Chaplin-UI is a gentle, privacy-focused tool that reads lips and turns them into text. Simply record yourself speaking (or upload a video), and watch as your words appear on screen—all without making a sound. This project is based on [Chaplin](https://github.com/amanvirparhar/chaplin) by [Amanvir Parhar](https://amanvir.com), with added web interface and UI improvements. The VSR model achieves **19.1% word error rate (WER)** on LRS3. Perfect for:

- 🎤 **Silent communication** - Type without speaking, or transcribe existing videos
- 🔒 **Privacy-first** - Everything runs locally on your machine ([Privacy Policy](./PRIVACY.md))
- 🌐 **Web-based** - Works in any modern browser—no installation needed
- 🎨 **Beautiful UI** - Clean, calming design that adapts to your system theme

## 💙 Who It's For

I built this after a week of laryngitis—when I couldn't speak, I needed a way to communicate. If you've ever wanted to say something without making a sound, Chaplin-UI might help:

- **Public places** — Libraries, offices, late-night calls, or anywhere you want to stay quiet
- **Deaf and hard-of-hearing** — Mouth words to communicate when sign language isn't shared
- **Medical conditions** — ALS, aphonia, cerebral palsy, laryngectomy, Parkinson's, vocal cord paralysis, selective mutism 
- **Temporary voice loss** — Laryngitis, recovery from throat surgery, or vocal strain
- **Privacy** — Situations where you'd rather not speak aloud but still need to get your words out

*Apple just acquired a silent-speech company ([Q.ai](https://www.theverge.com/news/870353/apple-q-ai-acquisition-silent-speech)) for $2 billion—this space matters, and open-source tools like this keep the technology accessible.*

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (check with `python3 --version`)
- **LLM local server** – Ollama or LM Studio (the app finds one you have running):
  - **[Ollama](https://ollama.com)** – `ollama serve` + `ollama pull <model>`
  - **[LM Studio](https://lmstudio.ai/)** – load model, enable Local Server (port 1234)
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

4. **Start your LLM server** (pick one: Ollama or LM Studio):

   **Option A – Ollama**
   ```bash
   ollama serve        # usually starts automatically
   ollama pull llama3.2   # or mistral, llama2, etc.
   ```

   **Option B – LM Studio**
   - Open LM Studio
   - Load a model (we recommend `zai-org/glm-4.6v-flash`)
   - Go to **Developer** tab → Enable **Local Server** (port 1234)

5. **Run the web app:**
   ```bash
   ./run_web.sh
   ```
   The UI opens in **~1 second** at [http://localhost:8000](http://localhost:8000). The model loads in the background (~30–60 sec first time); you can use the interface right away—buttons enable when ready.

6. **Start transcribing:**
   - **Record live**: Click "Start recording" to capture video from your camera
   - **Upload a video**: Click "Upload video" to transcribe an existing video file
   - Your transcription appears in both raw and corrected formats. (You can change the LLM in settings if needed.)

   That's it! The app handles everything else for you.

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

Simply put, Chaplin-UI watches how your lips move and turns that into text. Here's what happens behind the scenes:

1. **You provide video** - Either record yourself speaking or upload an existing video file
2. **Face detection** - The app finds and tracks your face in the video
3. **Lip reading** - A trained model watches your lip movements and creates initial text
4. **Text refinement** - An AI language model cleans up the text, adds punctuation, and fixes any mistakes
5. **You see results** - Both the raw transcription and the polished version appear on screen

You can copy the corrected text with one click, or review the raw output to see what the lip-reading model detected.

### LLM Providers: Ollama vs LM Studio

Chaplin-UI supports two local LLM backends. Both use OpenAI-compatible APIs:

| Provider   | Default URL              | Default Model | Setup |
|-----------|---------------------------|---------------|-------|
| **Ollama** | `http://localhost:11434/v1` | `llama3.2`    | `ollama serve` then `ollama pull <model>` |
| **LM Studio** | `http://localhost:1234/v1` | `local`       | Load model, enable Local Server in Developer tab |

- **Web app**: Select provider in the "LLM Provider" dropdown and optionally override the model name.
- **CLI**: Use `llm_provider=ollama` or `llm_provider=lmstudio`, or run with `--config-name ollama` for Ollama defaults.

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
# With Ollama:
python main.py --config-name ollama
# Or: python main.py llm_provider=ollama llm_model=mistral
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

This project is licensed under the MIT License - see [LICENSE](./LICENSE) for details.

## 🙏 Acknowledgments

### Original Creator

Chaplin-UI is based on [Chaplin](https://github.com/amanvirparhar/chaplin) by **[Amanvir Parhar](https://amanvir.com)**. We're grateful for the original work that made this project possible!

### Additional Credits

- **VSR Model**: Based on [Auto-AVSR](https://github.com/mpc001/auto_avsr) by mpc001 (19.1% WER on LRS3)
- **Dataset**: [Lip Reading Sentences 3](https://mmai.io/datasets/lip_reading/)
- **LLM**: Uses Ollama or LM Studio for local text correction (both OpenAI-compatible)

## 💬 Community

- 🐛 **Found a bug?** [Open an issue](https://github.com/loganngarcia/chaplin-ui/issues)
- 💡 **Have an idea?** [Start a discussion](https://github.com/loganngarcia/chaplin-ui/discussions)
- 📧 **Questions?** Check our [FAQ](./CONTRIBUTING.md#faq) or open a discussion

---

<div align="center">

**Made with ❤️ by the open source community**

[⭐ Star us on GitHub](https://github.com/loganngarcia/chaplin-ui) • [📖 Read the docs](#-documentation) • [🤝 Contribute](./CONTRIBUTING.md)

</div>
