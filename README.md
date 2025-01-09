# TG AI Bot

AI-powered Telegram bot generating custom cat videos on demand.

## Core Features

- AI video generation with custom actions
- Real-time status tracking
- Rate limiting & security
- Command-based interface

## Quick Start

1. Install:
```bash
pip install -r requirements.txt
```

2. Configure `.env`:
```
TELEGRAM_TOKEN=your_telegram_token
MINIMAX_API_KEY=your_minimax_api_key
```

3. Launch:
```bash
python bot.py
```

## Usage

- `/start` - Initialize bot
- `/help` - Command list
- `/cat [action] [object]` - Generate video
- `/status [taskID]` - Check generation status

## Technical Specs

- 5 concurrent generations per user
- 60s command cooldown
- 5min max video length

## Requirements

- Python 3.13+
- Telegram Bot API
- Minimax.ai API
