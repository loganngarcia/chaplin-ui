"""
Inference handling utilities for Chaplin-UI.

This module provides shared functions for running VSR inference and
managing video file cleanup.
"""

import logging
import os
from pathlib import Path
from typing import Callable, Optional

from pipelines.pipeline import InferencePipeline

logger = logging.getLogger(__name__)


def run_inference(
    vsr_model: InferencePipeline,
    video_path: str,
    on_result: Optional[Callable[[str], None]] = None,
    on_error: Optional[Callable[[Exception], None]] = None,
    cleanup_file: bool = True,
) -> Optional[str]:
    """Run VSR inference on a video file.
    
    Args:
        vsr_model: Loaded VSR inference pipeline.
        video_path: Path to video file.
        on_result: Optional callback with raw output text.
        on_error: Optional callback for errors.
        cleanup_file: Whether to delete video file after processing.
        
    Returns:
        Raw transcription text, or None if error occurred.
    """
    try:
        logger.info(f"Running inference on {video_path}")
        output = vsr_model(video_path)
        # Privacy: Use debug level to avoid logging sensitive transcription data
        logger.debug(f"Raw VSR output: {output}")
        
        if on_result:
            on_result(output)
        
        return output
        
    except Exception as e:
        logger.error(f"Inference failed: {e}", exc_info=True)
        if on_error:
            on_error(e)
        return None
        
    finally:
        if cleanup_file and os.path.exists(video_path):
            try:
                os.remove(video_path)
                logger.debug(f"Cleaned up video file: {video_path}")
            except OSError as e:
                logger.warning(f"Failed to cleanup {video_path}: {e}")
