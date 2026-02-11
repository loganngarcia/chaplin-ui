#!/bin/bash
# Run Chaplin-UI Web App - Open http://localhost:8000 in your browser
# Server starts in ~1 second; model loads in background (~30-60 sec first time)
# Make sure Ollama or LM Studio is running with a model before processing

cd "$(dirname "$0")"
source .venv/bin/activate
echo "Starting Chaplin-UI... UI will be available at http://localhost:8000 in a few seconds"
python web_app.py
