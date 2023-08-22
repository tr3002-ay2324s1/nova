#!/bin/bash
# Script to setup .env and start local/staging dev server
# Usage: ./run.sh [local|staging|production]

# Run Command
doppler run --command "python3 bot.py"
