# QL Cat Bot

A Telegram bot that generates cat videos based on user commands.

## Features

- Generate cat videos with specific actions and objects
- Track video generation status
- User-friendly command interface
- Rate limiting and security measures

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```
TELEGRAM_TOKEN=your_telegram_token
MINIMAX_API_KEY=your_minimax_api_key
```

3. Run the bot:
```bash
python bot.py
```

## Commands

- `/start` - Start the bot
- `/help` - Show available commands
- `/cat [action] [object]` - Generate a cat video (e.g., `/cat eat noodles`)
- `/status [taskID]` - Check video generation status

## Rate Limits

- Maximum 5 pending generations per user
- 60-second cooldown between commands
- Maximum video length: 5 minutes
