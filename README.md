# Telegram Channel Aggregator Bot

App that aggregates posts from multiple Telegram channels into a single target channel. Built with Telethon library and managed through Saved Messages. The main idea is to implement a news feed like in other social networks.

If you find this project helpful, please consider giving it a star ⭐ It helps others discover the project and motivates further development.

## Table of Contents
- [Features](#features)
- [Setup and Running](#setup-and-running)
  - [Requirements](#requirements)
  - [Quick Start](#quick-start)
  - [Background Running](#background-running)
- [Usage](#usage)
  - [Initial Setup](#initial-setup)
  - [Commands](#commands)
  - [Channel Setup](#channel-setup)
- [Technical Info](#technical-info)
  - [Configuration](#configuration)
  - [Troubleshooting](#troubleshooting)

## Features
- Combines posts from multiple channels into one
- Preserves media album structure
- Management through Saved Messages
- Concurrent post processing
- Persistent settings between restarts
- Independent session management

## Setup and Running

### Requirements
- Python 3.7+
- Telegram account
- Telegram API keys (get at https://my.telegram.org/apps)

### Quick Start
1. Clone and install dependencies:
```bash
git clone https://github.com/AlestackOverglow/telegram-aggregator.git
cd telegram-aggregator
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

2. Create `.env` file:
```
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+1234567890
```

3. Run the bot:
```bash
python main.py
```

4. First launch:
   - Enter Telegram verification code
   - Enter 2FA password (if enabled)
   - ⚠️**IMPORTANT:** Send `/start` to Saved Messages to begin aggregation, you only need to use this command every time you restart the bot, the rest of the settings are saved
   - Set target channel using `/set_target` command
   - Add at least one source channel `/add_channel <channel>` or all `/add_all_channels`
   - The bot will not aggregate any messages until these steps are completed.

### Background Running

**Linux/Mac**:
```bash
source venv/bin/activate && nohup python main.py > output.log 2>&1 &
```

**Windows**:
1. Create `run_bot.bat`:
```batch
@echo off
call venv\Scripts\activate
python main.py
pause
```
2. Run the batch file

**Linux Autostart** with systemd:
```ini
[Unit]
Description=Telegram Channel Aggregator Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/bot
Environment=PYTHONUNBUFFERED=1
ExecStart=/path/to/bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Usage

### Commands
All commands are sent to Saved Messages:
- `/start` - Start the bot (required after each launch)
- `/stop` - Stop the bot
- `/set_target <channel>` - Set target channel
- `/add_channel <channel>` - Add source channel
- `/add_all_channels` - Add all subscribed channels
- `/remove_channel <channel>` - Remove channel
- `/list` - List all channels
- `/status` - Show bot status

### Channel Setup

1. **Target Channel**:
   - Create or use existing channel
   - Make bot an admin
   - Set with `/set_target @channel`

2. **Source Channels**:
   - One by one: `/add_channel @channel`
   - All at once: `/add_all_channels`
   - Formats: `@username`, `https://t.me/channel`, `username`

## Technical Info

### Configuration
- `.env` - API keys and phone
- `sessions/` - Session files
- `channels.json` - Channel settings
- `bot.log` - Logs (1MB rotation)

### Troubleshooting

1. **Import/Init Errors**:
   - Update code
   - Restart bot

2. **2FA Issues**:
   - Enter password when prompted
   - Restart if error occurs

3. **Channel Access Issues**:
   - Check channel membership
   - Verify access rights
   - Test with regular client

4. **Session Problems**:
   - Delete `sessions` folder
   - Reauthorize

Detailed logs in `bot.log` 
