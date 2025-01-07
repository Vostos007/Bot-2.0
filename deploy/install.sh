#!/bin/bash

# Create directory for the bot
sudo mkdir -p /opt/telegram-bot

# Clone repository
cd /opt/telegram-bot
[ ! -d "Bot-2.0" ] && git clone https://github.com/Vostos007/Bot-2.0.git
cd Bot-2.0

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup systemd service
sudo cp deploy/telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

echo "Bot installed and started!"
echo "Check status with: sudo systemctl status telegram-bot"