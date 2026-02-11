"""
Configuration management for Chaplin-UI.

This module provides configuration classes and utilities for managing
application settings across different interfaces.
"""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from chaplin_ui.core.constants import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_DETECTOR,
    DEFAULT_DEVICE,
    DEFAULT_FPS,
    DEFAULT_FRAME_COMPRESSION,
    DEFAULT_RES_FACTOR,
    LLM_DEFAULT_BASE_URL,
    LLM_DEFAULT_MODEL,
)


@dataclass(frozen=True)
class VideoConfig:
    """Configuration for video capture and processing.
    
    Attributes:
        fps: Frames per second for video capture.
        frame_compression: JPEG compression quality (0-100).
        res_factor: Resolution divisor for performance optimization.
        output_prefix: Prefix for temporary video files.
    """
    
    fps: int = DEFAULT_FPS
    frame_compression: int = DEFAULT_FRAME_COMPRESSION
    res_factor: int = DEFAULT_RES_FACTOR
    output_prefix: str = "webcam"
    
    @property
    def frame_interval(self) -> float:
        """Calculate frame interval in seconds."""
        return 1.0 / self.fps


@dataclass(frozen=True)
class VSRConfig:
    """Configuration for Visual Speech Recognition model.
    
    Attributes:
        config_path: Path to VSR model configuration file.
        detector: Face detector to use ('mediapipe' or 'retinaface').
        device: Device to run inference on ('cpu', 'cuda:0', etc.).
    """
    
    config_path: str = DEFAULT_CONFIG_PATH
    detector: str = DEFAULT_DETECTOR
    device: str = DEFAULT_DEVICE
    
    def validate(self) -> None:
        """Validate configuration values.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        if not Path(self.config_path).exists():
            raise ValueError(f"Config file not found: {self.config_path}")
        
        if self.detector not in ["mediapipe", "retinaface"]:
            raise ValueError(f"Invalid detector: {self.detector}. Must be 'mediapipe' or 'retinaface'")


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for LLM text correction service.
    
    Attributes:
        base_url: Base URL for LLM API endpoint.
        model: Model name to use.
    """
    
    base_url: str = LLM_DEFAULT_BASE_URL
    model: str = LLM_DEFAULT_MODEL


@dataclass(frozen=True)
class AppConfig:
    """Main application configuration.
    
    Combines all configuration components into a single object.
    
    Attributes:
        video: Video capture configuration.
        vsr: VSR model configuration.
        llm: LLM service configuration.
    """
    
    video: VideoConfig = VideoConfig()
    vsr: VSRConfig = VSRConfig()
    llm: LLMConfig = LLMConfig()
    
    @classmethod
    def from_args(
        cls,
        config_path: Optional[str] = None,
        detector: Optional[str] = None,
        device: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
    ) -> "AppConfig":
        """Create configuration from command-line arguments.
        
        Args:
            config_path: Optional VSR config file path.
            detector: Optional detector name.
            device: Optional device name.
            llm_base_url: Optional LLM base URL.
            llm_model: Optional LLM model name.
            
        Returns:
            AppConfig instance with overridden values.
        """
        vsr_config = VSRConfig(
            config_path=config_path or DEFAULT_CONFIG_PATH,
            detector=detector or DEFAULT_DETECTOR,
            device=device or DEFAULT_DEVICE,
        )
        
        llm_config = LLMConfig(
            base_url=llm_base_url or LLM_DEFAULT_BASE_URL,
            model=llm_model or LLM_DEFAULT_MODEL,
        )
        
        return cls(vsr=vsr_config, llm=llm_config)
