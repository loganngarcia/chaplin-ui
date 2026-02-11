"""
Main entry point for Chaplin-UI CLI.

This module provides the CLI entry point using Hydra for configuration management.

Usage:
    python main.py config_filename=./configs/LRS3_V_WER19.1.ini detector=mediapipe
    
    Or use the run script:
    ./run.sh

Configuration:
    - Uses Hydra for flexible config management
    - Falls back to defaults if Hydra config fails
    - Supports command-line overrides (see Hydra docs)
    
Want to customize?
    - Change defaults: Modify the fallback config dict below
    - Add new options: Update hydra_configs/default.yaml
    - GPU support: Set gpu_idx=0 in config or command line
"""

import logging
import torch
from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra

from chaplin import Chaplin
from chaplin_ui.core.config import AppConfig
from chaplin_ui.core.logging_config import setup_logging
from pipelines.pipeline import InferencePipeline

logger = logging.getLogger(__name__)


def main():
    """Main entry point for Chaplin-UI CLI.
    
    This function:
    1. Sets up logging
    2. Loads configuration (Hydra or defaults)
    3. Determines device (CPU/GPU)
    4. Creates Chaplin instance
    5. Loads VSR model
    6. Starts webcam capture loop
    """
    setup_logging()
    
    # ========================================================================
    # Load Configuration
    # ========================================================================
    # Hydra allows flexible config management via YAML files and CLI overrides
    # If Hydra fails, we fall back to sensible defaults
    try:
        with initialize(config_path="hydra_configs", version_base=None):
            cfg = compose(config_name="default")
    except Exception as e:
        logger.error(f"Failed to load Hydra config: {e}")
        logger.info("Using default configuration")
        # Fallback config if Hydra isn't available
        cfg = type('obj', (object,), {
            'llm_base_url': 'http://localhost:1234/v1',
            'llm_model': 'local',
            'config_filename': './configs/LRS3_V_WER19.1.ini',
            'detector': 'mediapipe',  # or 'retinaface'
            'gpu_idx': -1,  # -1 = CPU, 0+ = GPU index
        })()
    
    # ========================================================================
    # Device Selection
    # ========================================================================
    # Determine whether to use CPU or GPU
    # GPU is much faster but requires CUDA and a compatible GPU
    device = "cpu"
    if torch.cuda.is_available() and cfg.gpu_idx >= 0:
        device = f"cuda:{cfg.gpu_idx}"
        logger.info(f"Using GPU: {device}")
    else:
        logger.info("Using CPU (GPU not available or disabled)")
    
    # ========================================================================
    # Application Setup
    # ========================================================================
    # Create application configuration from Hydra config
    app_config = AppConfig.from_args(
        config_path=cfg.config_filename,
        detector=cfg.detector,
        device=device,
        llm_base_url=getattr(cfg, "llm_base_url", None),
        llm_model=getattr(cfg, "llm_model", None),
        llm_provider=getattr(cfg, "llm_provider", None),
    )
    
    # Initialize Chaplin CLI application
    chaplin = Chaplin(
        llm_base_url=getattr(cfg, "llm_base_url", None),
        llm_model=getattr(cfg, "llm_model", None),
        llm_provider=getattr(cfg, "llm_provider", None),
        config=app_config,
    )
    
    # ========================================================================
    # Load VSR Model
    # ========================================================================
    # This is the "brain" that reads lips - it's large (~500MB) so loading
    # takes a minute or two. Be patient!
    logger.info(f"Loading VSR model from {cfg.config_filename}")
    logger.info("⏳ This may take a minute - the model is large")
    try:
        chaplin.vsr_model = InferencePipeline(
            config_filename=cfg.config_filename,
            device=torch.device(device),
            detector=cfg.detector,
            face_track=True,  # Track face across frames for better accuracy
        )
        logger.info("✅ VSR model loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to load VSR model: {e}")
        logger.error("💡 Make sure you ran ./setup.sh to download model files")
        raise
    
    # ========================================================================
    # Start Application
    # ========================================================================
    # This starts the webcam capture loop
    # Press Alt/Option to start/stop recording
    # Press 'q' to quit
    try:
        logger.info("🎬 Starting webcam capture...")
        logger.info("💡 Press Alt/Option to start/stop recording, 'q' to quit")
        chaplin.start_webcam()
    except KeyboardInterrupt:
        logger.info("👋 Interrupted by user - shutting down gracefully")
    except Exception as e:
        logger.error(f"❌ Error during execution: {e}")
        raise
    finally:
        # Cleanup Hydra (important for proper shutdown)
        if GlobalHydra.instance().is_initialized():
            GlobalHydra.instance().clear()


if __name__ == '__main__':
    main()
