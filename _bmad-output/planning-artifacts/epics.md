# DX Terminal Monitor - Epics & Stories

---
title: 合约交互层
created: 2026-03-01
status: planning
inputDocuments:
  - docs/architecture.md
  - docs/project-overview.md
---

## 项目概述

本文档定义 DX Terminal Monitor 的 **合约交互层** Epics 和 Stories，用于实现 Telegram Bot 与 AgentVault 智能合约的直接交互。

---

## 需求摘要

### 功能需求 (FR)

| ID | 需求 | 优先级 |
|----|------|--------|
| FR1 | 禁用指定策略 | P0 |
| FR2 | 禁用所有活跃策略 | P0 |
| FR3 | 添加新策略 | P1 |
| FR4 | 暂停/恢复 Agent 自动交易 | P1 |
| FR5 | 查看与更新 Vault 交易设置 | P2 |
| FR6 | 提取 ETH | P2 |
| FR7 | 监控 Agent 操作活动 | P3 |
| FR8 | 推送操作日志到 TG | P3 |
| FR9 | 控制监控服务 | P3 |

> **注意**: 合约不支持恢复已禁用的策略，如需恢复需通过 `addStrategy` 重新添加。

### 非功能需求 (NFR)

| ID | 需求 |
|----|------|
| NFR1 | 私钥安全存储，不在代码中硬编码 |
| NFR2 | 交易失败时有清晰的错误提示 |
| NFR3 | 高风险操作需要管理员权限确认 |
| NFR4 | Gas 费用超限时自动中止 |

---

## 需求覆盖矩阵

| 需求 | Epic 1 | Epic 2 | Epic 3 | Epic 4 |
|------|--------|--------|--------|--------|
| FR1 - 禁用指定策略 | ✅ Story 1.1 | - | - | - |
| FR2 - 禁用所有策略 | ✅ Story 1.2 | - | - | - |
| FR3 - 添加新策略 | - | ✅ Story 2.1 | - | - |
| FR4 - 暂停/恢复交易 | - | ✅ Story 2.2 | - | - |
| FR5 - 更新设置 | - | - | ✅ Story 3.1 | - |
| FR6 - 提取 ETH | - | - | ✅ Story 3.2 | - |
| FR7 - 监控 Agent 活动 | - | - | - | ✅ Story 4.1 |
| FR8 - 推送 TG 通知 | - | - | - | ✅ Story 4.2 |
| FR9 - 控制监控服务 | - | - | - | ✅ Story 4.3 |
| NFR1 - 私钥安全 | ✅ Story 1.0 | - | - | - |
| NFR2 - 错误提示 | ✅ All | ✅ All | ✅ All | ✅ All |
| NFR3 - 权限确认 | - | ✅ Story 2.x | ✅ Story 3.x | ✅ Story 4.3 |
| NFR4 - Gas 限制 | ✅ All | ✅ All | ✅ All | - |

---

## Epic 1: Web3 基础设施与策略禁用

**目标**: 建立合约交互基础层，实现策略禁用功能

### Story 1.0: Web3 基础设施搭建

**作为开发者，我需要** 搭建 web3.py 基础设施，**以便** 安全地与智能合约交互。

**验收标准:**
- [ ] 安装 web3.py 依赖
- [ ] 创建 `contract.py` 模块
- [ ] 创建 `abi/AgentVault.json` 文件
- [ ] 配置环境变量 (RPC_URL, PRIVATE_KEY, CHAIN_ID)
- [ ] 实现 `VaultContract` 类基础结构
- [ ] 实现 `_send_transaction()` 私有方法
- [ ] 添加单元测试（Mock Web3）

**技术说明:**
```python
# contract.py
class VaultContract:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
        self.contract = self.w3.eth.contract(...)

    async def _send_transaction(self, tx_func) -> dict:
        # 签名、发送、等待确认
```

**预估复杂度**: 中等

---

### Story 1.1: 禁用指定策略命令

**作为用户，我需要** 通过 `/disable_strategy <id>` 命令禁用指定策略，**以便** 停止不需要的自动交易。

**验收标准:**
- [ ] 实现 `contract.disable_strategy(strategy_id)` 方法
- [ ] 实现 `cmd_disable_strategy` 命令处理函数
- [ ] 命令格式: `/disable_strategy 1`
- [ ] 成功时返回: "策略 #1 已禁用，交易哈希: 0x..."
- [ ] 策略不存在时返回: "策略 #1 不存在或已禁用"
- [ ] 未授权用户返回: "未授权"
- [ ] 添加单元测试

**技术说明:**
```python
# main.py
async def cmd_disable_strategy(update, ctx):
    if not authorized(update):
        return
    strategy_id = ctx.args[0] if ctx.args else None
    if not strategy_id:
        await update.message.reply_text("用法: /disable_strategy <id>")
        return
    result = await contract.disable_strategy(int(strategy_id))
    # 处理结果...
```

**预估复杂度**: 低

---

### Story 1.2: 禁用所有策略命令

**作为用户，我需要** 通过 `/disable_all` 命令一键禁用所有活跃策略，**以便** 紧急情况下快速停止所有交易。

**验收标准:**
- [ ] 实现 `contract.disable_all_strategies()` 方法
- [ ] 实现 `cmd_disable_all` 命令处理函数
- [ ] 成功时返回禁用数量和交易哈希
- [ ] 无活跃策略时返回: "没有活跃策略"
- [ ] 添加单元测试

**技术说明:**
```python
# 调用合约的 disableAllActiveStrategies()
result = await contract.disable_all_strategies()
# 返回: "已禁用 3 个策略，交易哈希: 0x..."
```

**预估复杂度**: 低

---

### Story 1.3: 更新命令菜单和帮助文档

**作为用户，我需要** 在帮助菜单中看到新命令，**以便** 知道可以使用哪些功能。

**验收标准:**
- [ ] `/start` 命令包含新命令说明
- [ ] `post_init()` 注册新命令到 Telegram 菜单
- [ ] 更新 `tests/unit/test_edge_cases.py` 中的 `test_post_init_sets_commands`

**预估复杂度**: 低

---

## Epic 2: 策略管理与交易控制

**目标**: 实现策略添加和交易暂停功能

### Story 2.1: 添加新策略命令

**作为用户，我需要** 通过 `/add_strategy <text>` 命令添加新策略，**以便** 指导 Agent 进行特定交易。

**验收标准:**
- [ ] 实现 `contract.add_strategy(content, expiry, priority)` 方法
- [ ] 实现 `cmd_add_strategy` 命令处理函数
- [ ] 命令格式: `/add_strategy 当 ETH 跌破 3000 时买入`
- [ ] 默认参数: expiry=0 (永不过期), priority=1 (中等)
- [ ] 成功时返回: "策略已添加，ID: #4"
- [ ] 策略数量达到上限(8)时返回错误提示
- [ ] 管理员权限检查
- [ ] 添加单元测试

**预估复杂度**: 中等

---

### Story 2.2: 暂停/恢复 Agent 交易命令

**作为用户，我需要** 通过 `/pause` 和 `/resume` 命令控制 Agent 自动交易，**以便** 在市场异常时保护资金。

**验收标准:**
- [ ] 实现 `contract.pause_vault(paused: bool)` 方法
- [ ] 实现 `cmd_pause` 和 `cmd_resume` 命令处理函数
- [ ] `/pause` 返回: "⏸️ Agent 已暂停，将不会执行任何交易"
- [ ] `/resume` 返回: "▶️ Agent 已恢复，将继续执行交易"
- [ ] 管理员权限检查
- [ ] 添加单元测试

**技术说明:**
```python
# 调用合约的 pauseVault(bool paused_)
# paused_ = True  → 暂停 Agent 交易
# paused_ = False → 恢复 Agent 交易
```

**预估复杂度**: 低

---

## Epic 3: 高级管理与资金操作

**目标**: 实现设置更新和资金提取功能

### Story 3.1: 查看与更新交易设置命令

**作为用户，我需要** 通过 `/update_settings` 命令查看或调整交易参数，**以便** 了解当前设置或根据市场情况优化策略。

**验收标准:**
- [ ] 实现 `contract.update_settings(settings)` 方法
- [ ] 实现 `cmd_update_settings` 命令处理函数
- [ ] **无参数调用** `/update_settings` 时显示当前设置（查看模式）
- [ ] **带参数调用** `/update_settings max_trade=1000 slippage=50` 时更新设置
- [ ] 参数验证: maxTrade (500-10000 BPS), slippage (10-5000 BPS)
- [ ] 查看时返回当前设置摘要
- [ ] 更新成功时返回新设置摘要
- [ ] **增强 `/vault` 命令**：显示完整的设置信息（与 `/update_settings` 查看模式一致）
- [ ] 管理员权限检查
- [ ] 添加单元测试

**技术说明:**
```python
# 查看模式 (无参数)
async def cmd_update_settings(update, ctx):
    if not ctx.args:
        # 显示当前设置
        data = await api.get_vault()
        await update.message.reply_text(f"""
Current Settings

Max Trade: {data.get('maxTradeAmount', 0) / 100}%
Slippage: {data.get('slippageBps', 0) / 100}%
""")
        return
    # 解析参数并更新...
```

**预估复杂度**: 中等

---

### Story 3.2: 提取 ETH 命令

**作为用户，我需要** 通过 `/withdraw <amount>` 命令提取 ETH，**以便** 将资金转移到其他地址。

**验收标准:**
- [ ] 实现 `contract.withdraw_eth(amount)` 方法
- [ ] 实现 `cmd_withdraw` 命令处理函数
- [ ] 命令格式: `/withdraw 0.5` (单位: ETH)
- [ ] 二次确认: "确认提取 0.5 ETH 到你的钱包？ [Y/N]"
- [ ] 成功时返回: "已提取 0.5 ETH，交易哈希: 0x..."
- [ ] 余额不足时返回: "余额不足，当前可用: 0.3 ETH"
- [ ] 管理员权限检查
- [ ] 添加单元测试

**预估复杂度**: 中等

---

## 实现顺序建议

| 阶段 | Epic | Stories | 优先级 |
|------|------|---------|--------|
| **Phase 1** | Epic 1 | 1.0, 1.1, 1.2, 1.3 | 🔴 P0 |
| **Phase 2** | Epic 2 | 2.1, 2.2 | 🟡 P1 |
| **Phase 3** | Epic 3 | 3.1, 3.2 | 🟢 P2 |

---

## 技术依赖

```
Epic 1 (基础设施)
    └── Story 1.0 (Web3 基础) ← 必须首先完成
        ├── Story 1.1 (禁用策略)
        ├── Story 1.2 (禁用所有)
        └── Story 1.3 (菜单更新)

Epic 2 (策略管理)
    └── 依赖 Epic 1 完成
        ├── Story 2.1 (添加策略)
        └── Story 2.2 (暂停/恢复)

Epic 3 (高级功能)
    └── 依赖 Epic 1 完成
        ├── Story 3.1 (更新设置)
        └── Story 3.2 (提取 ETH)

Epic 4 (操作监控)
    └── 依赖 Epic 1 完成 (使用 api.py)
        ├── Story 4.1 (活动监控服务)
        ├── Story 4.2 (TG 消息推送)
        └── Story 4.3 (监控控制命令)
```

---

## 测试策略

### 单元测试

- Mock `Web3` 和合约调用
- 测试所有命令处理函数
- 测试错误处理分支

### 集成测试

- 使用 Anvil/Hardhat 本地网络
- 测试真实交易流程

### API 测试

- 在测试网 (Sepolia) 上测试
- 验证交易确认

---

## Epic 4: Agent 操作监控与推送

**目标**: 实现 Agent 操作自动监控，实时推送操作日志到 Telegram

### Story 4.1: 活动监控服务

**作为用户，我需要** 系统自动监控 Agent 的交易活动，**以便** 实时了解 Agent 的操作情况。

**验收标准:**
- [ ] 创建 `monitor.py` 模块
- [ ] 实现 `ActivityMonitor` 类
- [ ] 定期轮询 `api.get_activity()` 获取最新活动
- [ ] 记录已处理的活动 ID，避免重复推送
- [ ] 支持 .env 配置轮询间隔 (默认 30 秒)
- [ ] 添加单元测试

**技术说明:**
```python
# monitor.py
class ActivityMonitor:
    def __init__(self, api: TerminalAPI, callback: Callable):
        self.api = api
        self.callback = callback  # 新活动回调
        self.seen_ids: set[str] = set()
        self.poll_interval = int(os.getenv('POLL_INTERVAL', '30'))

    async def start(self):
        while True:
            activities = await self.api.get_activity(10)
            new_items = self._filter_new(activities)
            for item in new_items:
                await self.callback(item)
            await asyncio.sleep(self.poll_interval)
```

**预估复杂度**: 中等

---

### Story 4.2: TG 消息推送

**作为用户，我需要** 当 Agent 执行操作时收到 TG 通知，**以便** 及时了解交易动态。

**验收标准:**
- [ ] 实现 `format_activity_message()` 格式化活动消息
- [ ] 支持格式化 Swap/Deposit/Withdrawal 三种类型
- [ ] 推送到 `.env` 配置的 `ADMIN_USERS` 或 `ALLOWED_USERS`
- [ ] 消息包含: 操作类型、时间、金额/数量、交易链接
- [ ] 添加单元测试

**技术说明:**
```python
# 消息格式示例
"""
🔔 Agent 操作通知

类型: Swap
方向: BUY
代币: ETH → USDC
数量: 0.5 ETH
价格: $3,000
时间: 2026-03-01 12:00:00
查看: https://etherscan.io/tx/0x...
"""
```

**预估复杂度**: 低

---

### Story 4.3: 监控控制命令

**作为用户，我需要** 通过命令控制监控服务的开启/关闭，**以便** 灵活管理推送。

**验收标准:**
- [ ] 实现 `/monitor_start` 命令启动监控
- [ ] 实现 `/monitor_stop` 命令停止监控
- [ ] 实现 `/monitor_status` 命令查看状态
- [ ] 管理员权限检查
- [ ] Bot 启动时自动开始监控 (可配置)
- [ ] 添加单元测试

**预估复杂度**: 低

---

## Epic 4 需求覆盖

| 需求 | Story 4.1 | Story 4.2 | Story 4.3 |
|------|-----------|-----------|-----------|
| 监控 Agent 活动 | ✅ | - | - |
| 推送 TG 通知 | - | ✅ | - |
| 控制监控服务 | - | - | ✅ |

---

## 实现顺序建议

| 阶段 | Epic | Stories | 优先级 |
|------|------|---------|--------|
| **Phase 1** | Epic 1 | 1.0, 1.1, 1.2, 1.3 | 🔴 P0 |
| **Phase 2** | Epic 2 | 2.1, 2.2 | 🟡 P1 |
| **Phase 3** | Epic 3 | 3.1, 3.2 | 🟢 P2 |
| **Phase 4** | Epic 4 | 4.1, 4.2, 4.3 | 🔵 P3 |

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 私钥泄露 | 环境变量存储，不提交到 Git |
| 交易失败 | 清晰的错误提示，重试机制 |
| Gas 费用过高 | 设置 Gas 上限，超限自动中止 |
| 误操作 | 高风险操作需要管理员权限 |
| API 限流 | 合理设置轮询间隔，错误重试 |
| 消息刷屏 | 支持暂停/恢复监控，可配置间隔 |

---
