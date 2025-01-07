# Telegram Bot with Notion Integration

A Telegram bot that integrates with Notion for task management and monitoring.

## Project Structure

```
telegram-bot/
├── src/
│   ├── api/          # API endpoints
│   ├── services/     # Business logic services
│   ├── utils/        # Utility functions
│   └── main.py       # Application entry point
├── config/           # Configuration files
├── docs/            # Documentation
├── tests/           # Test files
├── scripts/         # Utility scripts
├── logs/            # Application logs
├── backups/         # Backup files
├── .env             # Environment variables
├── requirements.txt # Python dependencies
└── start_bot.sh     # Bot startup script
```

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- TELEGRAM_TOKEN
- NOTION_TOKEN
- DATABASE_ID
- ADMIN_ID

## Running the Bot

1. Start the bot:
```bash
./start_bot.sh
```

2. Monitor the bot:
- Check logs in `logs/` directory
- Use monitoring endpoints at `/monitoring`

## Development

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation as needed
- Use meaningful commit messages

## Backup

Backups are automatically created in the `backups/` directory.

## Monitoring

Access monitoring endpoints at:
- Health check: `/monitoring/health`
- Status: `/monitoring/status`

## License

MIT License