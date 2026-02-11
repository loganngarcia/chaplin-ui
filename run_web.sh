#!/bin/bash
# Run Chaplin-UI Web App - Open in browser at http://localhost:8000
# Make sure LM Studio is running with a model loaded (zai-org/glm-4.6v-flash)

cd "$(dirname "$0")"
source .venv/bin/activate
python web_app.py
