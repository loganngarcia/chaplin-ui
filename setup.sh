#!/bin/bash
# Setup script - downloads model files (uses curl for macOS compatibility)
mkdir -p benchmarks/LRS3/language_models/lm_en_subword/
curl -L -o benchmarks/LRS3/language_models/lm_en_subword/model.json "https://huggingface.co/Amanvir/lm_en_subword/resolve/main/model.json"
curl -L -o benchmarks/LRS3/language_models/lm_en_subword/model.pth "https://huggingface.co/Amanvir/lm_en_subword/resolve/main/model.pth"

mkdir -p benchmarks/LRS3/models/LRS3_V_WER19.1/
curl -L -o benchmarks/LRS3/models/LRS3_V_WER19.1/model.json "https://huggingface.co/Amanvir/LRS3_V_WER19.1/resolve/main/model.json"
curl -L -o benchmarks/LRS3/models/LRS3_V_WER19.1/model.pth "https://huggingface.co/Amanvir/LRS3_V_WER19.1/resolve/main/model.pth"