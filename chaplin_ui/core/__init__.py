"""
Core shared modules for Chaplin-UI.

This package contains shared utilities, models, and constants used across
all application interfaces (CLI, Web).
"""

from chaplin_ui.core.models import ChaplinOutput
from chaplin_ui.core.constants import (
    CHAPLIN_OUTPUT_SCHEMA,
    LLM_DEFAULT_BASE_URL,
    LLM_DEFAULT_MODEL,
    LLM_FALLBACK_MODEL,
    DEFAULT_CONFIG_PATH,
    DEFAULT_DETECTOR,
    DEFAULT_DEVICE,
    DEFAULT_FPS,
    DEFAULT_FRAME_COMPRESSION,
    DEFAULT_RES_FACTOR,
    MIN_RECORDING_DURATION_SECONDS,
    SUPPORTED_VIDEO_FORMATS,
)
from chaplin_ui.core.text_formatter import format_text_locally
from chaplin_ui.core.llm_client import LLMClient, create_llm_client
from chaplin_ui.core.config import AppConfig
from chaplin_ui.core.video_processor import (
    compress_frame,
    create_video_writer,
    generate_video_path,
    draw_recording_indicator,
    should_process_recording,
    cleanup_temp_videos,
    initialize_camera,
    VideoRecorder,
)
from chaplin_ui.core.async_utils import AsyncEventLoopManager
from chaplin_ui.core.inference_handler import run_inference

__all__ = [
    "ChaplinOutput",
    "CHAPLIN_OUTPUT_SCHEMA",
    "LLM_DEFAULT_BASE_URL",
    "LLM_DEFAULT_MODEL",
    "LLM_FALLBACK_MODEL",
    "DEFAULT_CONFIG_PATH",
    "DEFAULT_DETECTOR",
    "DEFAULT_DEVICE",
    "DEFAULT_FPS",
    "DEFAULT_FRAME_COMPRESSION",
    "DEFAULT_RES_FACTOR",
    "MIN_RECORDING_DURATION_SECONDS",
    "SUPPORTED_VIDEO_FORMATS",
    "format_text_locally",
    "LLMClient",
    "create_llm_client",
    "AppConfig",
    "compress_frame",
    "create_video_writer",
    "generate_video_path",
    "draw_recording_indicator",
    "should_process_recording",
    "cleanup_temp_videos",
    "initialize_camera",
    "VideoRecorder",
    "AsyncEventLoopManager",
    "run_inference",
]
