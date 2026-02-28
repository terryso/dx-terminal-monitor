# DX Terminal Monitor

[中文](README_CN.md) | English

A Telegram bot for monitoring Terminal Markets Vault.

## Features

- Query vault balance and positions
- View PnL details
- Track recent trading activity
- View active strategies
- Real-time data refresh

## Installation

```bash
# Clone the repository
git clone https://github.com/terryso/dx-terminal-monitor.git
cd dx-terminal-monitor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy the example config file
```bash
cp .env.example .env
```

2. Edit `.env` file
```
# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Allowed Telegram user IDs (comma separated)
ALLOWED_USERS=your_telegram_user_id

# Terminal Markets Vault address
VAULT_ADDRESS=your_vault_address

# API base URL
API_BASE_URL=https://api.terminal.markets/api/v1
```

### Getting Telegram Credentials

1. **Bot Token**: Search @BotFather on Telegram, send `/newbot` to create a bot
2. **User ID**: Search @userinfobot on Telegram to get your User ID

## Usage

```bash
source venv/bin/activate
python main.py
```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Show help |
| `/balance` | View balance |
| `/pnl` | View P&L |
| `/positions` | View positions |
| `/activity` | Recent activity |
| `/swaps` | Recent swaps |
| `/strategies` | Active strategies |
| `/vault` | Vault info |
| `/refresh` | Refresh data |

## Links

- [Terminal Markets](https://terminal.markets/)
- [Terminal Markets API Docs](https://docs.terminal.markets)
