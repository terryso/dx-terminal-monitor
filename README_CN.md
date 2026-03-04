# DX Terminal Monitor

中文 | [English](README.md)

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-378%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-96%25-green)
[![BMAD](https://bmad-badge.vercel.app/terryso/dx-terminal-monitor.svg)](https://github.com/bmad-code-org/BMAD-METHOD)

Terminal Markets Vault 监控与管理 Telegram Bot。

## 功能

### 🤖 AI 策略顾问（核心功能）

**智能交易策略推荐** - 由 LLM (Claude/OpenAI) 驱动

- **定时自动分析** - 按可配置的间隔自动分析持仓、策略和市场数据
- **智能建议** - AI 生成可执行的交易策略建议：
  - 添加新策略（含优先级和有效期）
  - 根据市场情况识别需要禁用的策略
- **一键执行** - 通过 Telegram 查看 AI 建议后一键执行
- **交互式审批流程** - 可单独执行或批量执行所有建议
- **可配置分析频率** - 默认每 2 小时分析一次

> ⚠️ **必要条件**：使用此功能需要配置：
> - `PRIVATE_KEY` - 用于签名策略交易（添加/禁用）
> - `LLM_PROVIDER` + `ANTHROPIC_API_KEY` 或 `OPENAI_API_KEY` - 用于 AI 分析

**命令：**
| 命令 | 功能 |
|------|------|
| `/advisor_on` | 启用 AI 顾问 |
| `/advisor_off` | 禁用 AI 顾问 |
| `/advisor_status` | 查看顾问状态 |
| `/advisor_analyze` | 立即触发分析 |

### 查询命令（所有用户）
- 查询 Vault 余额和持仓
- 查看 PnL 盈亏详情
- 查看最近交易活动
- 查看活跃策略
- 实时数据刷新

### 管理员命令
- 添加/禁用策略
- 暂停/恢复 Vault 交易
- 更新交易设置（最大交易、滑点）
- 更新行为偏好（活跃度、风险、仓位、持仓风格、分散度）
- 提取 ETH

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

# 管理员用户 ID (逗号分隔)
ADMIN_USERS=your_telegram_user_id

# Terminal Markets Vault 地址
VAULT_ADDRESS=your_vault_address

# Ethereum RPC URL
RPC_URL=your_rpc_url

# 用于签名交易的私钥
PRIVATE_KEY=your_private_key

# API 基础 URL
API_BASE_URL=https://api.terminal.markets/api/v1

# AI 策略顾问（可选）
ADVISOR_ENABLED=true
ADVISOR_INTERVAL_HOURS=2
SUGGESTION_TTL_MINUTES=30

# LLM 提供商 (anthropic 或 openai)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_key
# 或使用 OpenAI:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your_openai_key
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

### 查询命令（所有用户）

| 命令 | 功能 |
|------|------|
| `/start` | 显示帮助 |
| `/balance` | 查看余额 |
| `/pnl` | 查看盈亏 |
| `/positions` | 查看持仓 |
| `/activity` | 最近活动 |
| `/swaps` | 最近交易 |
| `/strategies` | 活跃策略 |
| `/vault` | Vault 信息和设置 |

### 管理员命令

| 命令 | 功能 |
|------|------|
| `/add_strategy <文本>` | 添加新策略 |
| `/disable_strategy <id>` | 禁用策略 |
| `/disable_all` | 禁用所有策略 |
| `/pause` | 暂停 Vault 交易 |
| `/resume` | 恢复 Vault 交易 |
| `/update_settings [参数]` | 查看/更新设置 |
| `/withdraw <数量>` | 提取 ETH |
| `/monitor_status` | 监控状态 |
| `/monitor_start` | 启动监控 |
| `/monitor_stop` | 停止监控 |
| `/advisor_on` | 启用 AI 顾问 |
| `/advisor_off` | 禁用 AI 顾问 |
| `/advisor_status` | 顾问状态 |
| `/advisor_analyze` | 触发分析 |

### `/update_settings` 参数

| 参数 | 范围 | 说明 |
|------|------|------|
| `max_trade` | 500-10000 | 最大交易比例 (BPS, 如 1000=10%) |
| `slippage` | 10-5000 | 滑点 (BPS, 如 50=0.5%) |
| `activity` | 1-5 | 交易活跃度 (非常低 → 非常高) |
| `risk` | 1-5 | 风险偏好 (保守 → 激进) |
| `size` | 1-5 | 交易大小 (极小 → 巨大) |
| `holding` | 1-5 | 持仓风格 (短线客 → 钻石手) |
| `diversification` | 1-5 | 分散度 (集中 → 广泛) |

**示例:**
```
/update_settings                           # 查看当前设置
/update_settings max_trade=2000 slippage=50  # 更新交易设置
/update_settings activity=3 risk=2           # 更新行为偏好
```

## 相关链接

- [Terminal Markets](https://terminal.markets/)
- [Terminal Markets API 文档](https://docs.terminal.markets)
