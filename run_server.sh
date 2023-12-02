#!/bin/bash
# Script to setup .env and start local/staging dev server
# Usage: ./run.sh [local|staging|production]

# Run `doppler login && doppler setup` first to authenticate`

# Run Command
doppler run --command "uvicorn api.index:app --reload"
