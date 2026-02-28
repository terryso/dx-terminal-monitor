# DX Terminal Monitor

中文 | [English](README.md)

Terminal Markets Vault 监控 Telegram Bot。

## 功能

- 查询 Vault 余额和持仓
- 查看 PnL 盈亏详情
- 查看最近交易活动
- 查看活跃策略
- 实时数据刷新

## 安装

```bash
# 克隆仓库
git clone https://github.com/terryso/dx-terminal-monitor.git
cd dx-terminal-monitor

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 配置

1. 复制配置文件模板
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件
```
# Telegram Bot Token (从 @BotFather 获取)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# 允许使用的 Telegram 用户 ID (逗号分隔)
ALLOWED_USERS=your_telegram_user_id

# Terminal Markets Vault 地址
VAULT_ADDRESS=your_vault_address

# API 基础 URL
API_BASE_URL=https://api.terminal.markets/api/v1
```

### 获取 Telegram 凭证

1. **Bot Token**: 在 Telegram 搜索 @BotFather，发送 `/newbot` 创建机器人
2. **User ID**: 在 Telegram 搜索 @userinfobot 获取你的 User ID

## 运行

```bash
source venv/bin/activate
python main.py
```

## 命令

| 命令 | 功能 |
|------|------|
| `/start` | 显示帮助 |
| `/balance` | 查看余额 |
| `/pnl` | 查看盈亏 |
| `/positions` | 查看持仓 |
| `/activity` | 最近活动 |
| `/swaps` | 最近交易 |
| `/strategies` | 活跃策略 |
| `/vault` | Vault 信息 |

## 相关链接

- [Terminal Markets](https://terminal.markets/)
- [Terminal Markets API 文档](https://docs.terminal.markets)
