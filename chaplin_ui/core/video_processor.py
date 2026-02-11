"""
Video processing utilities for Chaplin-UI.

This module provides shared functions for video frame compression, recording,
and file management used across CLI and Web interfaces.
"""

import logging
import time
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np

from chaplin_ui.core.config import VideoConfig
from chaplin_ui.core.constants import MIN_RECORDING_DURATION_SECONDS

logger = logging.getLogger(__name__)

# Video codec constant
VIDEO_CODEC = 'mp4v'


def compress_frame(frame: np.ndarray, compression_quality: int) -> np.ndarray:
    """Compress a frame using JPEG encoding/decoding to grayscale.
    
    This function compresses a color frame to grayscale using JPEG compression,
    which is used for recording to reduce file size while maintaining quality
    for VSR processing.
    
    Args:
        frame: Input BGR frame from camera.
        compression_quality: JPEG quality (0-100).
        
    Returns:
        Compressed grayscale frame.
    """
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), compression_quality]
    _, buffer = cv2.imencode('.jpg', frame, encode_param)
    compressed_frame = cv2.imdecode(buffer, cv2.IMREAD_GRAYSCALE)
    return compressed_frame


def create_video_writer(
    output_path: str,
    width: int,
    height: int,
    fps: int,
) -> cv2.VideoWriter:
    """Create a VideoWriter for recording grayscale video.
    
    Args:
        output_path: Path to output video file.
        width: Frame width in pixels.
        height: Frame height in pixels.
        fps: Frames per second.
        
    Returns:
        Configured VideoWriter instance.
    """
    return cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*VIDEO_CODEC),
        fps,
        (width, height),
        False  # Grayscale
    )


def generate_video_path(output_prefix: str) -> str:
    """Generate a unique video file path.
    
    Args:
        output_prefix: Prefix for the video filename.
        
    Returns:
        Full path to video file with timestamp.
    """
    timestamp = time.time_ns() // 1_000_000
    return f"{output_prefix}{timestamp}.mp4"


def draw_recording_indicator(
    frame: np.ndarray,
    x: int,
    y: int,
    radius: int = 10,
    inner_radius: int = 8,
) -> np.ndarray:
    """Draw a recording indicator circle on a frame.
    
    Args:
        frame: Frame to draw on.
        x: X coordinate of indicator center.
        y: Y coordinate of indicator center.
        radius: Outer circle radius.
        inner_radius: Inner circle radius.
        
    Returns:
        Frame with indicator drawn (mutates input frame).
    """
    cv2.circle(frame, (x, y), radius, (0, 0, 0), -1)
    cv2.circle(frame, (x, y), inner_radius, (0, 255, 0), -1)
    return frame


def should_process_recording(frame_count: int, fps: int) -> bool:
    """Check if a recording is long enough to process.
    
    Args:
        frame_count: Number of frames recorded.
        fps: Frames per second.
        
    Returns:
        True if recording meets minimum duration requirement.
    """
    min_frames = fps * MIN_RECORDING_DURATION_SECONDS
    return frame_count >= min_frames


def cleanup_temp_videos(output_prefix: str, directory: Path = Path('.')) -> int:
    """Remove temporary video files matching the output prefix.
    
    Args:
        output_prefix: Prefix to match video files.
        directory: Directory to search in.
        
    Returns:
        Number of files removed.
    """
    removed_count = 0
    pattern = f"{output_prefix}*.mp4"
    
    for file in directory.glob(pattern):
        try:
            file.unlink()
            removed_count += 1
            logger.debug(f"Removed temp file: {file}")
        except OSError as e:
            logger.warning(f"Failed to remove {file}: {e}")
    
    return removed_count


def initialize_camera(
    camera_index: int = 0,
    res_factor: int = 3,
) -> Tuple[cv2.VideoCapture, int, int]:
    """Initialize camera with specified resolution.
    
    Args:
        camera_index: Camera device index.
        res_factor: Resolution divisor for performance.
        
    Returns:
        Tuple of (VideoCapture, width, height).
        
    Raises:
        RuntimeError: If camera cannot be opened.
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open camera {camera_index}")
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640 // res_factor)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480 // res_factor)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"Camera initialized: {width}x{height}")
    return cap, width, height


class VideoRecorder:
    """Helper class for managing video recording state and operations.
    
    This class encapsulates the logic for starting/stopping recordings,
    writing frames, and managing recording state.
    
    Attributes:
        config: Video configuration.
        writer: Current VideoWriter instance (None if not recording).
        output_path: Path to current recording file.
        frame_count: Number of frames recorded in current session.
    """
    
    def __init__(self, config: VideoConfig):
        """Initialize video recorder.
        
        Args:
            config: Video configuration.
        """
        self.config = config
        self.writer: Optional[cv2.VideoWriter] = None
        self.output_path: str = ""
        self.frame_count: int = 0
    
    def start_recording(self, width: int, height: int) -> str:
        """Start a new recording session.
        
        Args:
            width: Frame width.
            height: Frame height.
            
        Returns:
            Path to the output video file.
        """
        if self.writer is not None:
            logger.warning("Recording already in progress")
            return self.output_path
        
        self.output_path = generate_video_path(self.config.output_prefix)
        self.writer = create_video_writer(
            self.output_path,
            width,
            height,
            self.config.fps,
        )
        self.frame_count = 0
        logger.info(f"Started recording: {self.output_path}")
        return self.output_path
    
    def write_frame(self, frame: np.ndarray) -> None:
        """Write a frame to the current recording.
        
        Args:
            frame: Grayscale frame to write.
        """
        if self.writer is None:
            raise RuntimeError("No active recording")
        
        self.writer.write(frame)
        self.frame_count += 1
    
    def stop_recording(self) -> Optional[str]:
        """Stop the current recording.
        
        Returns:
            Path to recorded file if recording was active, None otherwise.
        """
        if self.writer is None:
            return None
        
        self.writer.release()
        self.writer = None
        
        output_path = self.output_path
        frame_count = self.frame_count
        
        self.output_path = ""
        self.frame_count = 0
        
        logger.info(f"Stopped recording: {output_path} ({frame_count} frames)")
        return output_path
    
    def is_recording(self) -> bool:
        """Check if currently recording.
        
        Returns:
            True if recording is active.
        """
        return self.writer is not None
    
    def should_process(self) -> bool:
        """Check if current recording meets minimum duration.
        
        Returns:
            True if recording is long enough to process.
        """
        return should_process_recording(self.frame_count, self.config.fps)
