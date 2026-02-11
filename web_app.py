#!/usr/bin/env python3
"""
Chaplin-UI Web App: FastAPI backend for browser-based visual speech recognition.

This module provides a FastAPI web server for Chaplin-UI, allowing users to
upload videos or record from their browser camera for VSR transcription.

Quick Start:
    python web_app.py
    # Then open http://localhost:8000 in your browser

Architecture:
    - FastAPI handles HTTP requests
    - VSR model processes video → raw text
    - LLM client corrects text → formatted output
    - Frontend (web/) handles UI and camera

Want to extend this? Check out:
    - Add new endpoints: Just add @app.get() or @app.post() functions
    - Change port: Modify WEB_APP_PORT in chaplin_ui/core/constants.py
    - Add auth: Add middleware before routes
"""

import asyncio
import logging
import os
import subprocess
import sys
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from chaplin_ui.core import (
    LLMClient,
    SUPPORTED_VIDEO_FORMATS,
    create_llm_client,
)
from chaplin_ui.core.constants import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_DETECTOR,
    DEFAULT_DEVICE,
    LLM_PROVIDER_OLLAMA,
    LLM_PROVIDER_LMSTUDIO,
    OLLAMA_DEFAULT_MODEL,
    LMSTUDIO_DEFAULT_MODEL,
    WEB_APP_HOST,
    WEB_APP_PORT,
    WEB_DIR_NAME,
)
from chaplin_ui.core.logging_config import get_logger, setup_logging
from pipelines.pipeline import InferencePipeline

logger = get_logger(__name__)

# ============================================================================
# FastAPI Application Setup
# ============================================================================

# ============================================================================
# Lifespan: Start Server Immediately, Load Model in Background
# ============================================================================
# The VSR model is ~500MB and takes 20-60 seconds to load. Instead of blocking
# startup, we load it in a background task so the UI opens in ~1 second.


def _load_vsr_model() -> Optional[InferencePipeline]:
    """Load VSR model (blocking - runs in thread pool)."""
    try:
        return InferencePipeline(
            config_filename=CONFIG_PATH,
            detector=DETECTOR,
            face_track=True,
            device=DEVICE,
        )
    except Exception as e:
        logger.error(f"❌ Failed to load VSR model: {e}")
        logger.error("Make sure you ran ./setup.sh to download model files")
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start server immediately; load model in background."""
    global vsr_model, llm_client

    setup_logging()
    logger.info("🚀 Server starting - UI available immediately at http://localhost:8000")

    async def load_models_background() -> None:
        global vsr_model, llm_client
        logger.info("Loading VSR model in background (~30–60 sec)...")
        loop = asyncio.get_event_loop()
        vsr_model = await loop.run_in_executor(None, _load_vsr_model)
        if vsr_model:
            logger.info("✅ VSR model loaded successfully!")
        llm_client = create_llm_client(provider=LLM_PROVIDER_LMSTUDIO)
        logger.info("✅ LLM client initialized")
        logger.info("💡 Start Ollama or LM Studio with a model loaded before processing!")

    asyncio.create_task(load_models_background())
    yield
    # Shutdown (no cleanup needed for our globals)


# Initialize FastAPI app
app = FastAPI(
    title="Chaplin-UI",
    version="1.0.0",
    description="Visual Speech Recognition Web Application",
    lifespan=lifespan,
)

# CORS middleware - allows browser to make requests from any origin
# ⚠️ SECURITY: For production, restrict to specific domains!
# Current setting allows ANY website to make requests to your API
# This is fine for local development but dangerous for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ CHANGE THIS for production: ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Global Application State
# ============================================================================

# These are loaded once at startup and reused for all requests
# This is more efficient than loading the model for each request
vsr_model: Optional[InferencePipeline] = None  # VSR model for lip reading
llm_client: Optional[LLMClient] = None  # LLM client for text correction

# ============================================================================
# Configuration
# ============================================================================

# You can override these defaults by modifying constants.py or passing
# environment variables. See CONTRIBUTING.md for more details.
CONFIG_PATH = DEFAULT_CONFIG_PATH  # Path to VSR model config
DETECTOR = DEFAULT_DETECTOR  # "mediapipe" or "retinaface"
DEVICE = DEFAULT_DEVICE  # "cpu" or "cuda:0"
WEB_DIR = Path(__file__).parent / WEB_DIR_NAME  # Frontend files location


@app.get("/", response_class=HTMLResponse)
async def serve_index() -> HTMLResponse:
    """Serve the main HTML page."""
    return HTMLResponse(content=(WEB_DIR / "index.html").read_text())


@app.get("/style.css")
async def serve_css() -> FileResponse:
    """Serve CSS stylesheet."""
    return FileResponse(WEB_DIR / "style.css", media_type="text/css")


@app.get("/app.js")
async def serve_js() -> FileResponse:
    """Serve JavaScript application code."""
    return FileResponse(WEB_DIR / "app.js", media_type="application/javascript")


@app.post("/api/process-video")
async def process_video(
    video: UploadFile = File(...),
    provider: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
) -> dict:
    """Process uploaded video file for VSR transcription.
    
    Supports optional provider (ollama/lmstudio) and model selection.
    If not provided, uses LM Studio defaults.
    
    This is the main endpoint that handles video processing:
    1. Validates the video format
    2. Saves it temporarily
    3. Converts WebM to MP4 if needed (browser recordings are often WebM)
    4. Runs VSR inference to get raw text
    5. Uses LLM to correct and format the text
    6. Returns both raw and corrected versions
    
    Args:
        video: Uploaded video file from the browser.
        provider: Optional LLM provider - "ollama" or "lmstudio" (default: lmstudio).
        model: Optional model name override (e.g. "mistral" for Ollama, "local" for LM Studio).
        
    Returns:
        Dictionary with:
            - 'raw': Raw VSR output (typically ALL CAPS)
            - 'corrected': LLM-corrected and formatted text
        
    Raises:
        HTTPException: 
            - 503 if model not loaded yet
            - 400 if unsupported video format
    
    Example:
        ```python
        # From JavaScript:
        const formData = new FormData();
        formData.append('video', videoFile);
        const response = await fetch('/api/process-video', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        console.log(data.raw);  // "HELLO WORLD"
        console.log(data.corrected);  // "Hello world."
        ```
    """
    # Check if models are ready (they load in background after server starts)
    if vsr_model is None:
        raise HTTPException(
            status_code=503,
            detail="Model still loading... Please wait a moment and try again.",
        )
    
    if llm_client is None:
        raise HTTPException(
            status_code=503,
            detail="LLM client not initialized."
        )
    
    # Validate file format - we support common video formats
    ext = Path(video.filename or "video.mp4").suffix.lower()
    if ext not in SUPPORTED_VIDEO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {ext}. Supported formats: {', '.join(SUPPORTED_VIDEO_FORMATS)}"
        )
    
    # Save uploaded file temporarily
    # We use tempfile to ensure files are cleaned up even if something goes wrong
    suffix = ext
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        try:
            # Read video content from upload
            contents = await video.read()
            tmp.write(contents)
            tmp_path = tmp.name
            
            # Convert WebM to MP4 if ffmpeg is available
            # Browser recordings are often WebM, but our VSR pipeline prefers MP4
            # If conversion fails, we'll try the original format
            if ext == ".webm":
                mp4_path = tmp_path.rsplit(".", 1)[0] + ".mp4"
                try:
                    # Use ffmpeg to convert: WebM → MP4, video only (no audio)
                    subprocess.run(
                        ["ffmpeg", "-i", tmp_path, "-c:v", "libx264", "-an", "-y", mp4_path],
                        capture_output=True,
                        check=True,
                        timeout=60,  # Don't wait forever
                    )
                    os.remove(tmp_path)  # Remove original WebM
                    tmp_path = mp4_path
                    logger.info(f"✅ Converted WebM to MP4: {mp4_path}")
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
                    # ffmpeg not available or conversion failed - try original format
                    logger.warning(f"⚠️ WebM conversion failed, using original: {e}")
                    logger.info("💡 Install ffmpeg for better WebM support: brew install ffmpeg")
            
            # Step 1: Run VSR inference
            # This is where the magic happens - the model reads lips and outputs text
            logger.info(f"🎬 Processing video: {tmp_path}")
            output = vsr_model(tmp_path)
            # Privacy: Use debug level for transcription text to avoid logging sensitive data
            logger.debug(f"📝 Raw VSR output: {output}")
            
            # Step 2: LLM correction
            # The raw output is usually ALL CAPS with no punctuation
            # The LLM fixes grammar, adds punctuation, and formats it nicely
            # Use per-request provider/model if provided, else default client
            if provider and provider in (LLM_PROVIDER_OLLAMA, LLM_PROVIDER_LMSTUDIO):
                request_client = create_llm_client(provider=provider, model=model)
                corrected = await request_client.correct_text_simple(output)
            else:
                corrected = await llm_client.correct_text_simple(output)
            # Privacy: Use debug level for transcription text to avoid logging sensitive data
            logger.debug(f"✨ Corrected output: {corrected}")
            
            return {"raw": output, "corrected": corrected}
            
        finally:
            # Always clean up temporary files, even if something went wrong
            # This prevents disk space issues from accumulating temp files
            for path in [tmp_path, tmp.name]:
                if path != tmp.name and os.path.exists(path):
                    try:
                        os.remove(path)
                        logger.debug(f"🗑️ Cleaned up temp file: {path}")
                    except OSError as e:
                        logger.warning(f"Failed to cleanup {path}: {e}")


@app.get("/api/health")
async def health() -> dict:
    """Health check endpoint.
    
    Returns:
        Dictionary with status and model loading state.
    """
    return {
        "status": "ok",
        "model_loaded": vsr_model is not None,
        "llm_client_ready": llm_client is not None,
    }


@app.get("/api/llm-config")
async def get_llm_config() -> dict:
    """Get available LLM providers and their default models.
    
    Returns:
        Dictionary with provider options for the UI.
    """
    return {
        "providers": [
            {"id": LLM_PROVIDER_OLLAMA, "name": "Ollama", "default_model": OLLAMA_DEFAULT_MODEL},
            {"id": LLM_PROVIDER_LMSTUDIO, "name": "LM Studio", "default_model": LMSTUDIO_DEFAULT_MODEL},
        ],
    }


def main() -> None:
    """Main entry point for web application."""
    import uvicorn
    
    logger.info(f"Starting Chaplin-UI web server on {WEB_APP_HOST}:{WEB_APP_PORT}")
    uvicorn.run(app, host=WEB_APP_HOST, port=WEB_APP_PORT)


if __name__ == "__main__":
    main()
