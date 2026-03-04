# DX Terminal Monitor

[中文](README_CN.md) | English

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-378%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-96%25-green)
[![BMAD](https://bmad-badge.vercel.app/terryso/dx-terminal-monitor.svg)](https://github.com/bmad-code-org/BMAD-METHOD)

A Telegram bot for monitoring and managing Terminal Markets Vault.

## Features

### 🤖 AI Strategy Advisor (Highlight)

**Intelligent Trading Strategy Recommendations** - Powered by LLM (Claude/OpenAI)

- **Automatic Periodic Analysis** - Analyzes your positions, strategies, and market data at configurable intervals
- **Smart Suggestions** - AI generates actionable trading strategy recommendations:
  - Add new strategies with priority and validity period
  - Identify strategies to disable based on market conditions
- **One-Click Execution** - Review AI suggestions via Telegram and execute with a single tap
- **Interactive Approval Flow** - Execute individual suggestions or all at once
- **Configurable Intervals** - Set analysis frequency (default: 2 hours)

> ⚠️ **Prerequisites**: This feature requires:
> - `PRIVATE_KEY` - for signing strategy transactions (add/disable)
> - `LLM_PROVIDER` + `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` - for AI analysis

**Commands:**
| Command | Description |
|---------|-------------|
| `/advisor_on` | Enable AI advisor |
| `/advisor_off` | Disable AI advisor |
| `/advisor_status` | Check advisor status |
| `/advisor_analyze` | Trigger immediate analysis |

### Query Commands (All Users)
- Query vault balance and positions
- View PnL details
- Track recent trading activity
- View active strategies
- Real-time data refresh

### Admin Commands
- Add/disable strategies
- Pause/resume vault trading
- Update trading settings (max trade, slippage)
- Update behavior preferences (activity, risk, size, holding style, diversification)
- Withdraw ETH

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

# Admin user IDs (comma separated)
ADMIN_USERS=your_telegram_user_id

# Terminal Markets Vault address
VAULT_ADDRESS=your_vault_address

# Ethereum RPC URL
RPC_URL=your_rpc_url

# Private key for signing transactions
PRIVATE_KEY=your_private_key

# API base URL
API_BASE_URL=https://api.terminal.markets/api/v1

# AI Strategy Advisor (optional)
ADVISOR_ENABLED=true
ADVISOR_INTERVAL_HOURS=2
SUGGESTION_TTL_MINUTES=30

# LLM Provider (anthropic or openai)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_key
# Or for OpenAI:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your_openai_key
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

### Query Commands (All Users)

| Command | Description |
|---------|-------------|
| `/start` | Show help |
| `/balance` | View balance |
| `/pnl` | View P&L |
| `/positions` | View positions |
| `/activity` | Recent activity |
| `/swaps` | Recent swaps |
| `/strategies` | Active strategies |
| `/vault` | Vault info & settings |

### Admin Commands

| Command | Description |
|---------|-------------|
| `/add_strategy <text>` | Add new strategy |
| `/disable_strategy <id>` | Disable strategy |
| `/disable_all` | Disable all strategies |
| `/pause` | Pause vault trading |
| `/resume` | Resume vault trading |
| `/update_settings [params]` | View/Update settings |
| `/withdraw <amount>` | Withdraw ETH |
| `/monitor_status` | Monitor status |
| `/monitor_start` | Start monitor |
| `/monitor_stop` | Stop monitor |
| `/advisor_on` | Enable AI advisor |
| `/advisor_off` | Disable AI advisor |
| `/advisor_status` | Advisor status |
| `/advisor_analyze` | Trigger analysis |

### `/update_settings` Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| `max_trade` | 500-10000 | Max trade (BPS, e.g. 1000=10%) |
| `slippage` | 10-5000 | Slippage (BPS, e.g. 50=0.5%) |
| `activity` | 1-5 | Trading activity (Very Low → Very High) |
| `risk` | 1-5 | Risk preference (Conservative → Aggressive) |
| `size` | 1-5 | Trade size (Tiny → Huge) |
| `holding` | 1-5 | Holding style (Scalper → HODL) |
| `diversification` | 1-5 | Diversification (Concentrated → Wide) |

**Examples:**
```
/update_settings                           # View current settings
/update_settings max_trade=2000 slippage=50  # Update trading settings
/update_settings activity=3 risk=2           # Update behavior preferences
```

## Links

- [Terminal Markets](https://terminal.markets/)
- [Terminal Markets API Docs](https://docs.terminal.markets)
