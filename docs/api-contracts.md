# DX Terminal Monitor - API 合约

## Telegram Bot 命令

### 命令列表

| 命令 | 说明 | 权限 |
|------|------|------|
| `/start` | 显示帮助信息 | 授权用户 |
| `/help` | 显示帮助信息 | 授权用户 |
| `/balance` | 查询账户余额 | 授权用户 |
| `/pnl` | 查询盈亏详情 | 授权用户 |
| `/positions` | 查询当前持仓 | 授权用户 |
| `/activity` | 查询最近活动 | 授权用户 |
| `/swaps` | 查询交易记录 | 授权用户 |
| `/strategies` | 查询活跃策略 | 授权用户 |
| `/vault` | 查询 Vault 信息 | 授权用户 |

### 命令详情

#### `/start` - 帮助信息

**请求**: 无参数

**响应**:
```
Terminal Markets Monitor

Commands:
/balance - View balance
/pnl - View PnL
/positions - View positions
/activity - Recent activity
/swaps - Recent swaps
/strategies - Active strategies
/vault - Vault info
```

---

#### `/balance` - 余额查询

**请求**: 无参数

**响应**:
```
Balance Summary

ETH: 1.234567 ETH
Total Value: $12,345.67
Total PnL: $1,234.56 (+10.00%)
```

---

#### `/pnl` - 盈亏查询

**请求**: 无参数

**响应**:
```
PnL Summary

Total: $1,234.56 (+10.00%)
ETH: 0.123456

Breakdown:

ETH:
  Total: $500.00 (+8.00%)
  Realized: $200.00
  Unrealized: $300.00

USDC:
  Total: $734.56 (+12.00%)
  Realized: $300.00
  Unrealized: $434.56
```

---

#### `/positions` - 持仓查询

**请求**: 无参数

**响应**:
```
Positions:

ETH: $5,000.00
  PnL: $500.00 (+10.00%)

USDC: $3,000.00
  PnL: $300.00 (+5.00%)
```

---

#### `/activity` - 活动记录

**请求**: 无参数 (默认返回最近 5 条)

**响应**:
```
Recent Activity:

[Swap] BUY ETH: 0.5 ETH
[Deposit] 1.0 ETH
[Withdraw] 0.2 ETH
[Swap] SELL USDC: 0.3 ETH
```

---

#### `/swaps` - 交易记录

**请求**: 无参数 (默认返回最近 5 条)

**响应**:
```
Recent Swaps:

BUY ETH
  ETH: 0.5
  Price: $2500.00

SELL USDC
  ETH: 0.3
  Price: $2480.00
```

---

#### `/strategies` - 策略列表

**请求**: 无参数

**响应**:
```
Active Strategies:

#1 [HIGH]
  Strategy content preview...

#2 [MEDIUM]
  Strategy content preview...
```

---

#### `/vault` - Vault 信息

**请求**: 无参数

**响应**:
```
Vault Info

Address: 0x933a...4997C
NFT: #123 Vault Name
Owner: 0xabcd...efgh
State: active
Paused: false

Settings:
  Max Trade: 10%
  Slippage: 0.5%
```

---

## Terminal Markets API

### 基础信息

- **Base URL**: `https://api.terminal.markets/api/v1`
- **认证**: 无 (公开端点)
- **格式**: JSON

### 端点列表

#### GET `/vault`

查询 Vault 基本信息

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| vaultAddress | string | 是 | Vault 合约地址 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| vaultAddress | string | Vault 地址 |
| nftId | number | NFT ID |
| nftName | string | NFT 名称 |
| ownerAddress | string | 所有者地址 |
| state | string | 状态 |
| paused | boolean | 是否暂停 |
| maxTradeAmount | number | 最大交易比例 |
| slippageBps | number | 滑点 (基点) |

---

#### GET `/positions/{vaultAddress}`

查询持仓信息

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| ethBalance | string | ETH 余额 (wei) |
| overallValueUsd | string | 总价值 (USD) |
| overallPnlUsd | string | 总盈亏 (USD) |
| overallPnlPercent | string | 盈亏比例 |
| overallPnlEth | string | 盈亏 (ETH) |
| positions | array | 持仓列表 |

**Position 对象**:
| 字段 | 类型 | 说明 |
|------|------|------|
| tokenSymbol | string | 代币符号 |
| currentValueUsd | string | 当前价值 (USD) |
| totalPnlUsd | string | 总盈亏 (USD) |
| totalPnlPercent | string | 盈亏比例 |
| realizedPnlUsd | string | 已实现盈亏 |
| unrealizedPnlUsd | string | 未实现盈亏 |

---

#### GET `/activity/{vaultAddress}`

查询最近活动

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | number | 否 | 返回数量 |
| order | string | 否 | 排序 (asc/desc) |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 活动列表 |

**Activity Item 类型**:
- `swap` - 交易
- `deposit` - 存款
- `withdrawal` - 取款

---

#### GET `/strategies/{vaultAddress}`

查询活跃策略

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| activeOnly | string | 否 | 仅活跃策略 |

**响应**: 策略数组

**Strategy 对象**:
| 字段 | 类型 | 说明 |
|------|------|------|
| strategyId | number | 策略 ID |
| strategyPriority | string | 优先级 |
| content | string | 策略内容 |

---

#### GET `/swaps`

查询交易记录

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| vaultAddress | string | 是 | Vault 地址 |
| limit | number | 否 | 返回数量 |
| order | string | 否 | 排序 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 交易列表 |

**Swap 对象**:
| 字段 | 类型 | 说明 |
|------|------|------|
| tokenSymbol | string | 代币符号 |
| side | string | 方向 (buy/sell) |
| ethAmount | string | ETH 数量 (wei) |
| effectivePriceUsd | string | 成交价格 |

---

## 错误处理

### API 错误格式

```json
{
  "error": "HTTP 404"
}
```

### Bot 错误响应

```
Error: HTTP 404
```

### 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
