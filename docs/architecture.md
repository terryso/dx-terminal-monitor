# DX Terminal Monitor - 架构文档

## 执行摘要

DX Terminal Monitor 是一个轻量级的 Telegram Bot 服务，采用简单的单体架构设计。它作为 Terminal Markets Vault 的监控客户端，提供实时账户信息查询功能。

## 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 编程语言 | Python | 3.x | 主要开发语言 |
| Bot 框架 | python-telegram-bot | >=21.0 | Telegram Bot API 封装 |
| HTTP 客户端 | aiohttp | >=3.9.3 | 异步 HTTP 请求 |
| 配置管理 | python-dotenv | >=1.0.0 | 环境变量管理 |

## 架构模式

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Platform                     │
└─────────────────────┬───────────────────────────────────┘
                      │ Bot API (Long Polling)
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   DX Terminal Monitor                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   main.py   │  │   api.py    │  │  config.py  │     │
│  │ (Bot Logic) │──│ (API Client)│──│  (Config)   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────┬───────────────────────────────────┘
                      │ REST API
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 Terminal Markets API                     │
│                   (api.terminal.markets)                 │
└─────────────────────────────────────────────────────────┘
```

### 组件结构

#### 1. 命令处理层 (main.py)

- **职责**: 处理 Telegram 命令，格式化响应
- **设计模式**: Command Pattern
- **命令列表**:
  - `/start` - 帮助信息
  - `/balance` - 余额查询
  - `/pnl` - 盈亏查询
  - `/positions` - 持仓查询
  - `/activity` - 活动记录
  - `/swaps` - 交易记录
  - `/strategies` - 策略列表
  - `/vault` - Vault 信息

#### 2. API 客户端层 (api.py)

- **职责**: 封装 Terminal Markets API 调用
- **设计模式**: Repository Pattern
- **特性**:
  - 异步 HTTP 请求
  - 统一错误处理
  - 类型注解

#### 3. 配置层 (config.py)

- **职责**: 加载和管理配置
- **配置来源**: 环境变量 (.env)
- **配置项**:
  - `TELEGRAM_BOT_TOKEN` - Bot 令牌
  - `ALLOWED_USERS` - 授权用户列表
  - `VAULT_ADDRESS` - Vault 地址
  - `API_BASE_URL` - API 基础 URL

## API 设计

### Terminal API 方法

| 方法 | 端点 | 说明 |
|------|------|------|
| `get_vault()` | `/vault` | Vault 基本信息 |
| `get_positions()` | `/positions/{vault}` | 持仓信息 |
| `get_pnl_history()` | `/pnl-history/{vault}` | 盈亏历史 |
| `get_activity()` | `/activity/{vault}` | 最近活动 |
| `get_strategies()` | `/strategies/{vault}` | 活跃策略 |
| `get_swaps()` | `/swaps` | 交易记录 |
| `get_deposits_withdrawals()` | `/deposits-withdrawals/{vault}` | 存取款记录 |

### 错误处理策略

```python
# API 层
if resp.status == 200:
    return await resp.json()
return {"error": f"HTTP {resp.status}"}

# 命令层
if "error" in data:
    await update.message.reply_text(f"Error: {data['error']}")
    return
```

## 可靠性设计

### 自动重试机制

```python
retry_count = 0
max_retries = 10
base_delay = 5

while retry_count < max_retries:
    try:
        app.run_polling(...)
    except (TimedOut, NetworkError) as e:
        delay = min(base_delay * (2 ** (retry_count - 1)), 300)
        time.sleep(delay)
```

- **指数退避**: 5s → 10s → 20s → ... → 300s (max)
- **最大重试**: 10 次
- **异常处理**: NetworkError, TimedOut, TelegramError

### 安全机制

- **用户授权**: 基于用户 ID 的访问控制
- **代理禁用**: 自动清除代理环境变量

## 部署架构

```
┌─────────────────────────────────┐
│        运行环境 (本地/VPS)        │
│                                 │
│  ┌─────────────────────────┐   │
│  │    Python 虚拟环境       │   │
│  │    (venv)               │   │
│  └───────────┬─────────────┘   │
│              │                  │
│  ┌───────────▼─────────────┐   │
│  │    DX Terminal Monitor   │   │
│  │    (python main.py)     │   │
│  └─────────────────────────┘   │
│                                 │
└─────────────────────────────────┘
```

## 扩展性考虑

### 当前限制

1. 单实例运行，无水平扩展
2. 配置更新需要重启
3. 无持久化存储

### 未来扩展方向

1. **多 Vault 支持**: 扩展配置和命令
2. **数据持久化**: 添加数据库支持
3. **推送通知**: 主动告警功能
4. **Web Dashboard**: 添加 Web 界面

## 测试策略

- **当前状态**: 无自动化测试
- **建议**:
  - 添加 API 客户端单元测试
  - 添加命令处理器集成测试
  - Mock Telegram API 进行测试
