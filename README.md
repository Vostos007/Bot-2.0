# Bot 2.0 - Notion Task Manager

Telegram Bot integrated with Notion for task management.

## Features

- Task management through Telegram
- Notion integration
- Status tracking
- Priority management
- Tag support

## Installation

1. Clone the repository
```bash
git clone https://github.com/Vostos007/Bot-2.0.git
cd Bot-2.0
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
Create `.env` file with:
```ini
TELEGRAM_TOKEN=your_telegram_token
NOTION_TOKEN=your_notion_token
DATABASE_ID=your_notion_database_id
ADMIN_ID=your_telegram_id
```

5. Run the bot
```bash
python main.py
```

## Usage

Start bot in Telegram:
1. Send `/start` to initialize
2. Use inline keyboard to manage tasks
3. Create new tasks with priority and tags
4. Monitor task status