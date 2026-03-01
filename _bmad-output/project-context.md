# DX Terminal Monitor - Project Context

---
title: DX Terminal Monitor 项目上下文
version: 1.0
lastUpdated: 2026-03-01
status: active
---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | >=3.12 | 主要开发语言 |
| python-telegram-bot | >=21.0 | Telegram Bot API 封装 |
| aiohttp | >=3.9.3 | 异步 HTTP 请求 |
| web3.py | >=6.0.0 | 智能合约交互 |
| python-dotenv | >=1.0.0 | 环境变量管理 |
| pytest | >=8.0 | 测试框架 |

---

## 关键实现规则

### Python 编码规范

```
规则: 使用异步函数处理所有 I/O 操作
示例: async def cmd_balance(update, context):
原因: python-telegram-bot 21.x 要求异步处理器

规则: 使用 f-string 格式化字符串
示例: f"余额: {balance} ETH"
原因: 更清晰、性能更好

规则: 使用类型注解
示例: def format_percent(value: str) -> str:
原因: 提高代码可读性和 IDE 支持
```

### Telegram Bot 命令结构

```python
# 标准命令处理器模式
async def cmd_<name>(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. 权限检查
    if not authorized(update):
        await update.message.reply_text("未授权")
        return

    # 2. 参数解析
    args = context.args or []

    # 3. 业务逻辑
    result = await api_or_contract_call()

    # 4. 格式化响应
    await update.message.reply_text(formatted_response)
```

### 权限检查模式

```python
# 双层权限检查
def authorized(update: Update) -> bool:
    """检查用户是否在允许列表中"""
    user_id = update.effective_user.id
    allowed = config.ALLOWED_USERS
    return not allowed or user_id in allowed

def is_admin(update: Update) -> bool:
    """检查用户是否为管理员（用于高风险操作）"""
    user_id = update.effective_user.id
    return user_id in config.ADMIN_USERS
```

### 错误处理模式

```python
# API 调用错误处理
result = await api.get_positions()
if "error" in result:
    await update.message.reply_text(f"错误: {result['error']}")
    return

# 合约调用错误处理
result = await contract.disable_strategy(strategy_id)
if not result.get("success"):
    await update.message.reply_text(f"交易失败: {result.get('error')}")
    return
```

### 格式化函数

```python
# 金额格式化
def format_eth(wei: int) -> str:
    """将 Wei 转换为 ETH 字符串"""
    return f"{Web3.from_wei(wei, 'ether'):.4f} ETH"

# 百分比格式化
def format_percent(value: str) -> str:
    """格式化百分比，带正负号"""
    num = float(value)
    sign = "+" if num > 0 else ""
    return f"{sign}{num:.2f}%"
```

---

## 架构模式

### 双模式架构

```
┌─────────────────────────────────────────┐
│           DX Terminal Monitor           │
├─────────────────────────────────────────┤
│  main.py     - Bot 命令处理             │
│  api.py      - REST API 客户端 (只读)   │
│  contract.py - Web3 合约交互 (写入)     │
│  config.py   - 配置管理                 │
└─────────────────────────────────────────┘
```

### 命令分类

| 类型 | 数据源 | 示例命令 |
|------|--------|----------|
| 只读 | REST API | /balance, /pnl, /positions, /strategies |
| 写入 | Contract | /disable_strategy, /add_strategy, /pause |

### 数据流

```
只读命令 → api.py → Terminal Markets REST API
写入命令 → contract.py → Ethereum Network → AgentVault Contract
```

---

## 安全规则

### 私钥管理

```
规则: 私钥永远不能硬编码在代码中
实现: 使用环境变量 PRIVATE_KEY
存储: .env 文件 (不提交到 Git)

规则: 高风险操作需要管理员权限
实现: 使用 is_admin() 检查
范围: /withdraw, /update_settings, /add_strategy
```

### 访问控制分级

| 级别 | 操作 | 权限要求 |
|------|------|----------|
| 🟢 低风险 | 查询命令 | ALLOWED_USERS |
| 🟡 中风险 | 策略管理 | ALLOWED_USERS + 二次确认 |
| 🔴 高风险 | 资金操作 | ADMIN_USERS |

---

## 测试规则

### 测试结构

```
tests/
├── conftest.py          # 共享 fixtures
├── unit/                # 单元测试 (Mock)
│   ├── test_command_handlers.py
│   ├── test_command_handlers_p1.py
│   ├── test_edge_cases.py
│   └── test_utils.py
├── integration/         # 集成测试
└── api/                 # API 测试 (真实调用)
```

### 测试模式

```python
# Given-When-Then 结构
async def test_cmd_balance_success(mock_api, mock_update):
    # Given
    mock_api.get_balance.return_value = {"balance": "1.5"}

    # When
    await cmd_balance(mock_update, Mock())

    # Then
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "1.5" in call_args
```

### Mock 使用

```python
# Mock API 响应
@pytest.fixture
def mock_api(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr("main.api", mock)
    return mock

# Mock Telegram Update
@pytest.fixture
def mock_update():
    update = MagicMock()
    update.effective_user.id = TEST_USER_ID
    update.message.reply_text = AsyncMock()
    return update
```

---

## 文件结构

```
dx-terminal-monitor/
├── main.py              # Bot 命令处理
├── api.py               # REST API 客户端
├── contract.py          # 智能合约交互 (待实现)
├── config.py            # 配置管理
├── abi/                 # 合约 ABI 文件 (待实现)
│   └── AgentVault.json
├── tests/               # 测试目录
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── api/
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量模板
└── docs/
    ├── architecture.md
    └── project-overview.md
```

---

## 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| TELEGRAM_BOT_TOKEN | ✅ | Bot 令牌 |
| VAULT_ADDRESS | ✅ | Vault 合约地址 |
| RPC_URL | ✅ | Ethereum RPC 端点 |
| PRIVATE_KEY | ✅ | 钱包私钥 (敏感) |
| CHAIN_ID | ✅ | 链 ID (1=mainnet) |
| ALLOWED_USERS | ❌ | 授权用户 ID 列表 |
| ADMIN_USERS | ❌ | 管理员用户 ID 列表 |
| API_BASE_URL | ❌ | REST API 基础 URL |

---

## Git 工作流

### 提交信息格式

```
<type>: <description>

[optional body]

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 分支策略

- main: 主分支，稳定代码
- feature/*: 功能分支
- fix/*: 修复分支

---

## 依赖关系

```
main.py
  ├── api.py (REST 客户端)
  ├── contract.py (Web3 客户端)
  └── config.py (配置)

config.py
  └── 环境变量 (.env)

contract.py
  ├── web3.py
  └── abi/AgentVault.json
```

---

## API 参考文档

### Terminal Markets 官方文档

| 文档 | URL | 用途 |
|------|-----|------|
| Agent Vault Contract API | https://docs.terminal.markets/resources/agent-vault-contract-api | 合约函数说明、权限模型 |
| REST API Swagger | https://api.terminal.markets/swagger/doc.json | 完整 API 端点定义 |

### AgentVault 合约函数速查

**Owner-only 函数（需要私钥签名）：**

| 函数 | 参数 | 用途 |
|------|------|------|
| `updateSettings(settings_)` | AgentSettings tuple | 更新交易偏好设置 |
| `addStrategy(strategy, expiry, prio)` | string, uint64, uint8 | 添加策略（最多8个） |
| `disableStrategy(id)` | uint256 | 禁用单个策略 |
| `disableAllActiveStrategies()` | - | 禁用所有活跃策略 |
| `depositETH()` | payable | 存入 ETH（转为 WETH） |
| `withdrawETH(amount_)` | uint256 | 提取 ETH（从 WETH 转回） |
| `recoverEth(amount_)` | uint256 | 提取强制转入的原始 ETH |
| `pauseVault(paused_)` | bool | 暂停/恢复 operator 交换执行 |

**AgentSettings 字段约束：**

| 字段 | 类型 | 范围 | 说明 |
|------|------|------|------|
| maxTradeAmount | uint256 | 500-10000 | BPS (5%-100%) |
| slippageBps | uint256 | 10-5000 | BPS (0.1%-50%) |
| tradingActivity | uint8 | 1-5 | 滑块值 |
| assetRiskPreference | uint8 | 1-5 | 滑块值 |
| tradeSize | uint8 | 1-5 | 滑块值 |
| holdingStyle | uint8 | 1-5 | 滑块值 |
| diversification | uint8 | 1-5 | 滑块值 |

**策略优先级枚举：**
- `0 = Low`
- `1 = Med`
- `2 = High`

**VaultOperator 权限限制：**
- ✅ 可调用 `swapV4(...)`
- ✅ 可在 owner 发起后调用 `finalizeVaultClosure()`
- ❌ 不能调用资金管理函数
- ❌ 不能提取 ETH/WETH/tokens
- ❌ 不能调用 `xcall(...)`
- ❌ 不能更改设置、策略或所有权

---

## 当前开发状态

### 已完成 ✅

- REST API 客户端 (api.py)
- 查询命令 (/balance, /pnl, /positions 等)
- 测试框架 (pytest, 96% 覆盖率)
- CI/CD 管道 (GitHub Actions)

### 进行中 🔄

- Web3 基础设施搭建 (Story 1.0)
- 策略禁用命令 (Story 1.1, 1.2)

### 计划中 📋

- 策略添加命令 (Epic 2)
- 资金操作命令 (Epic 3)
