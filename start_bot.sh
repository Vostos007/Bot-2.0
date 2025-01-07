#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create necessary directories if they don't exist
mkdir -p logs backups

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create one based on .env.example"
    exit 1
fi

# Start the bot
echo "Starting Telegram-Notion bot..."
python src/main.py