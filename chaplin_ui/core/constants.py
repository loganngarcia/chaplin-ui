"""
Shared constants for Chaplin-UI.

This module centralizes all configuration constants, magic numbers, and
shared values used across the application.

🎯 Why centralize constants?
    - Single source of truth - change once, affects everywhere
    - Easy to find and modify configuration
    - No magic numbers scattered throughout code
    - Makes it clear what can be customized

💡 Want to customize something?
    - Change colors? Look for APPLE_* constants
    - Change port? Modify WEB_APP_PORT
    - Add video format? Add to SUPPORTED_VIDEO_FORMATS
    - Adjust recording settings? Check DEFAULT_FPS, etc.
"""

from typing import List

# ============================================================================
# LLM Configuration
# ============================================================================
# These control how we connect to LM Studio (or any OpenAI-compatible API)

LLM_DEFAULT_BASE_URL: str = "http://localhost:1234/v1"  # LM Studio default port
LLM_DEFAULT_MODEL: str = "local"  # "local" means "use whatever model is loaded"
LLM_FALLBACK_MODEL: str = "zai-org/glm-4.6v-flash"  # Fallback if "local" fails
LLM_API_KEY: str = "lm-studio"  # LM Studio doesn't require a real key
LLM_TEMPERATURE: float = 0.3  # Lower = more consistent, Higher = more creative

# JSON schema for LM Studio structured output
CHAPLIN_OUTPUT_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "chaplin_output",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "list_of_changes": {"type": "string"},
                "corrected_text": {"type": "string"},
            },
            "required": ["list_of_changes", "corrected_text"],
        },
    },
}

# ============================================================================
# VSR Model Configuration
# ============================================================================
# Visual Speech Recognition model settings

DEFAULT_CONFIG_PATH: str = "./configs/LRS3_V_WER19.1.ini"  # Path to model config
DEFAULT_DETECTOR: str = "mediapipe"  # Face detector: "mediapipe" or "retinaface"
DEFAULT_DEVICE: str = "cpu"  # "cpu" or "cuda:0" for GPU (if available)

# ============================================================================
# Video Processing Configuration
# ============================================================================
# These affect video capture, recording, and processing performance

DEFAULT_FPS: int = 16  # Frames per second for recording (16 is good balance)
DEFAULT_FRAME_COMPRESSION: int = 25  # JPEG quality 0-100 (lower = smaller files, faster)
DEFAULT_RES_FACTOR: int = 3  # Divide resolution by this (3 = 640/3 = 213px width)
MIN_RECORDING_DURATION_SECONDS: int = 2  # Minimum recording length to process
DEFAULT_OUTPUT_PREFIX: str = "webcam"  # Prefix for temporary video files

# Supported video formats for upload
SUPPORTED_VIDEO_FORMATS: List[str] = [".mp4", ".webm", ".avi", ".mov", ".mkv"]

# ============================================================================
# UI Configuration (Apple HIG Dark Mode)
# ============================================================================
# These are the official Apple Human Interface Guidelines colors for dark mode
# Feel free to customize these to match your preferred theme!

APPLE_BG: str = "#000000"  # System Background (pure black)
APPLE_BG_SECONDARY: str = "#1c1c1e"  # Secondary System Background (System Gray 6)
APPLE_BG_TERTIARY: str = "#2c2c2e"  # Tertiary System Background (System Gray 5)
APPLE_LABEL: str = "#FFFFFF"  # Primary label (white text)
APPLE_SECONDARY: str = "rgba(235, 235, 245, 0.6)"  # Secondary label (60% opacity)
APPLE_TERTIARY: str = "rgba(235, 235, 245, 0.3)"  # Tertiary label (30% opacity)
APPLE_BLUE: str = "#0A84FF"  # System blue (primary actions)
APPLE_GREEN: str = "#30D158"  # System green (success states)
APPLE_RED: str = "#FF453A"  # System red (destructive actions, recording)
APPLE_ORANGE: str = "#FF9F0A"  # System orange (warnings)
APPLE_YELLOW: str = "#FFD60A"  # System yellow (processing states)
APPLE_CORNER_RADIUS: int = 28  # Border radius for rounded corners (px)
APPLE_FONT_SIZE: int = 15  # Base font size (px)

# ============================================================================
# Web App Configuration
# ============================================================================
# Server and frontend settings

# ⚠️ SECURITY WARNING: "0.0.0.0" exposes server to your network
# For local development: Use "127.0.0.1" (localhost only)
# For production: Use reverse proxy (nginx) with proper authentication
WEB_APP_HOST: str = "0.0.0.0"  # Change to "127.0.0.1" for localhost-only access
WEB_APP_PORT: int = 8000  # Port to run web server on
WEB_DIR_NAME: str = "web"  # Directory containing HTML/CSS/JS files
