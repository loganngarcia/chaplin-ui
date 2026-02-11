"""
Chaplin CLI: Command-line interface for visual speech recognition.

This module provides the core CLI functionality for Chaplin-UI, including
webcam capture, video recording, VSR inference, and LLM text correction
with automatic typing.

How it works:
    1. Opens webcam and displays video feed
    2. Press Alt/Option to start/stop recording
    3. Records video frames while recording
    4. When stopped, runs VSR inference on recorded video
    5. LLM corrects the raw transcription
    6. Types the corrected text into the active window

Usage:
    python main.py config_filename=./configs/LRS3_V_WER19.1.ini detector=mediapipe
    
Want to customize?
    - Change hotkey: Modify the '<alt>' key in toggle_recording setup
    - Adjust recording: See VideoConfig in chaplin_ui/core/config.py
    - Change typing behavior: Modify _type_text method
"""

import asyncio
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Optional

import cv2
from pynput import keyboard

from chaplin_ui.core import (
    LLMClient,
    MIN_RECORDING_DURATION_SECONDS,
    AsyncEventLoopManager,
    cleanup_temp_videos,
    compress_frame,
    create_video_writer,
    draw_recording_indicator,
    generate_video_path,
    initialize_camera,
    run_inference,
    should_process_recording,
    create_llm_client,
)
from chaplin_ui.core.config import AppConfig, VideoConfig
from chaplin_ui.core.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


class Chaplin:
    """Main CLI application class for Chaplin-UI.
    
    This class manages webcam capture, video recording, VSR inference,
    and LLM text correction with automatic keyboard typing.
    
    The CLI version is great for:
        - Quick transcriptions without opening a browser
        - Automatic typing into any application
        - Testing and development
        - Scripting and automation
    
    Attributes:
        vsr_model: Loaded VSR inference pipeline (set externally).
        config: Application configuration.
        llm_client: LLM client for text correction.
        recording: Whether currently recording video.
        executor: Thread pool for async operations.
        kbd_controller: Keyboard controller for typing.
        async_manager: Manages asyncIO event loop in background thread.
        next_sequence_to_type: Sequence number for ordered typing.
        current_sequence: Current sequence counter.
        hotkey: Global hotkey listener for recording toggle.
    """
    
    def __init__(
        self,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_provider: Optional[str] = None,
        config: Optional[AppConfig] = None,
    ):
        """Initialize Chaplin CLI application.
        
        Args:
            llm_base_url: Optional LLM API base URL override.
            llm_model: Optional LLM model name override.
            llm_provider: Optional LLM provider ("ollama" or "lmstudio").
            config: Optional application configuration.
        """
        setup_logging()
        
        self.config = config or AppConfig()
        self.vsr_model = None  # Set externally after initialization

        # Apply llm_provider override to config
        llm_config = self.config.llm
        if llm_provider:
            llm_config = llm_config.__class__(
                base_url=llm_config.base_url, model=llm_config.model, provider=llm_provider
            )

        # Initialize LLM client (supports Ollama and LM Studio)
        if llm_base_url:
            llm_config = llm_config.__class__(
                base_url=llm_base_url, model=llm_config.model, provider=llm_config.provider
            )
        if llm_model:
            llm_config = llm_config.__class__(
                base_url=llm_config.base_url, model=llm_model, provider=llm_config.provider
            )

        self.llm_client = create_llm_client(
            provider=llm_config.provider,
            base_url=llm_config.base_url,
            model=llm_config.model,
        )
        
        # Recording state
        self.recording = False
        
        # Threading and async setup
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.async_manager = AsyncEventLoopManager()
        
        # Sequence tracking for ordered typing
        self.next_sequence_to_type = 0
        self.current_sequence = 0
        
        # Keyboard controller for typing
        self.kbd_controller = keyboard.Controller()
        
        # Setup global hotkey for recording toggle
        self.hotkey = keyboard.GlobalHotKeys({
            '<alt>': self.toggle_recording
        })
        self.hotkey.start()
        
        logger.info("Chaplin CLI initialized")
    
    
    def toggle_recording(self) -> None:
        """Toggle recording state when Alt/Option key is pressed."""
        self.recording = not self.recording
        logger.info(f"Recording {'started' if self.recording else 'stopped'}")
    
    async def _correct_output_async(self, output: str, sequence_num: int) -> str:
        """Correct VSR output using LLM and type it in order.
        
        Args:
            output: Raw VSR transcription text.
            sequence_num: Sequence number for ordering.
            
        Returns:
            Corrected text string.
        """
        try:
            corrected_output = await self.llm_client.correct_text(output)
            corrected = corrected_output.corrected_text.strip()
            
            # Ensure proper sentence ending
            if corrected and corrected[-1] not in ['.', '?', '!']:
                corrected += '.'
            corrected += ' '  # Add space for typing
            
        except Exception as e:
            logger.error(f"LLM correction failed: {e}")
            # Fallback: use local formatting
            from chaplin_ui.core.text_formatter import format_text_locally
            corrected = format_text_locally(output)
            if corrected and corrected[-1] not in ['.', '?', '!']:
                corrected += '.'
            corrected += ' '
        
        # Wait until it's this task's turn to type (maintain order)
        async with self.async_manager.typing_condition:
            while self.next_sequence_to_type != sequence_num:
                await self.async_manager.typing_condition.wait()
            
            # Type the corrected text
            self.kbd_controller.type(corrected)
            logger.info(f"Typed corrected text (sequence {sequence_num})")
            
            # Increment sequence and notify next task
            self.next_sequence_to_type += 1
            self.async_manager.typing_condition.notify_all()
        
        return corrected
    
    def perform_inference(self, video_path: str) -> Dict[str, str]:
        """Perform VSR inference on a video file.
        
        Args:
            video_path: Path to video file for inference.
            
        Returns:
            Dictionary with 'output' (raw text) and 'video_path'.
        """
        if self.vsr_model is None:
            raise RuntimeError("VSR model not loaded")
        
        def on_result(output: str) -> None:
            """Handle inference result."""
            # Assign sequence number for ordered typing
            sequence_num = self.current_sequence
            self.current_sequence += 1
            
            # Start async LLM correction (non-blocking)
            asyncio.run_coroutine_threadsafe(
                self._correct_output_async(output, sequence_num),
                self.async_manager.loop
            )
        
        output = run_inference(
            self.vsr_model,
            video_path,
            on_result=on_result,
            cleanup_file=False,  # We'll clean up after typing
        )
        
        if output is None:
            raise RuntimeError("Inference failed")
        
        return {
            "output": output,
            "video_path": video_path,
        }
    
    def _cleanup_temp_videos(self) -> None:
        """Remove temporary video files."""
        video_config = self.config.video
        cleanup_temp_videos(video_config.output_prefix)
    
    def start_webcam(self) -> None:
        """Start webcam capture and recording loop.
        
        This method runs the main capture loop, handling video recording,
        VSR inference, and display. Press 'q' to quit.
        """
        video_config = self.config.video
        
        # Initialize webcam
        cap, frame_width, frame_height = initialize_camera(
            camera_index=0,
            res_factor=video_config.res_factor,
        )
        
        last_frame_time = time.time()
        futures = []
        output_path = ""
        out: Optional[cv2.VideoWriter] = None
        frame_count = 0
        
        try:
            while True:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("Quit key pressed")
                    break
                
                current_time = time.time()
                
                # Capture frame at correct frame rate
                if current_time - last_frame_time >= video_config.frame_interval:
                    ret, frame = cap.read()
                    if not ret:
                        logger.warning("Failed to read frame")
                        continue
                    
                    # Compress frame
                    compressed_frame = compress_frame(
                        frame,
                        video_config.frame_compression
                    )
                    
                    if self.recording:
                        # Start new recording if needed
                        if out is None:
                            output_path = generate_video_path(video_config.output_prefix)
                            out = create_video_writer(
                                output_path,
                                frame_width,
                                frame_height,
                                video_config.fps,
                            )
                            logger.info(f"Started recording: {output_path}")
                            frame_count = 0
                        
                        # Write frame
                        out.write(compressed_frame)
                        last_frame_time = current_time
                        frame_count += 1
                        
                        # Draw recording indicator (not saved to video)
                        draw_recording_indicator(compressed_frame, frame_width - 20, 20)
                    
                    # Handle stopped recording
                    elif not self.recording and frame_count > 0:
                        if out is not None:
                            out.release()
                            out = None
                        
                        # Process if recording was long enough
                        if should_process_recording(frame_count, video_config.fps):
                            logger.info(f"Processing recording ({frame_count} frames)")
                            futures.append(
                                self.executor.submit(
                                    self.perform_inference,
                                    output_path
                                )
                            )
                        else:
                            logger.warning(
                                f"Recording too short ({frame_count} frames), "
                                f"minimum: {video_config.fps * MIN_RECORDING_DURATION_SECONDS}"
                            )
                            if os.path.exists(output_path):
                                os.remove(output_path)
                        
                        frame_count = 0
                        output_path = ""
                    
                    # Display frame
                    cv2.imshow('Chaplin-UI', cv2.flip(compressed_frame, 1))
                
                # Process completed inference tasks
                for fut in futures[:]:
                    if fut.done():
                        try:
                            result = fut.result()
                            if os.path.exists(result["video_path"]):
                                os.remove(result["video_path"])
                            futures.remove(fut)
                        except Exception as e:
                            logger.error(f"Inference task failed: {e}")
                            futures.remove(fut)
                    else:
                        break  # Process in order
        
        finally:
            # Cleanup
            logger.info("Cleaning up resources")
            cap.release()
            if out:
                out.release()
            cv2.destroyAllWindows()
            
            # Stop hotkey listener
            self.hotkey.stop()
            
            # Stop async event loop
            self.async_manager.shutdown(wait=True)
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            # Clean up temp files
            self._cleanup_temp_videos()
            
            logger.info("Chaplin CLI shutdown complete")
