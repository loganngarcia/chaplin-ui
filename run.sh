#!/bin/bash
# Run Chaplin-UI - Visual Speech Recognition (uses LM Studio for LLM correction)
# 1. Start LM Studio, load a model, and enable "Local Server" in Developer tab
# 2. Press Option (Mac) or Alt (Windows/Linux) to start/stop recording
# 3. Press q to exit
#
# To use a specific model: python main.py ... llm_model=your-model-name

cd "$(dirname "$0")"
source .venv/bin/activate
python main.py config_filename=./configs/LRS3_V_WER19.1.ini detector=mediapipe
