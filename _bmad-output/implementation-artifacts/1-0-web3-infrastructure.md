# Story 1.0: Web3 基础设施搭建

Status: done

## Story

作为**开发者**，我需要**搭建 web3.py 基础设施**，以便**安全地与 AgentVault 智能合约交互**。

## Acceptance Criteria

1. 安装 web3.py 依赖 (requirements.txt)
2. 创建 `contract.py` 模块，实现 `VaultContract` 类
3. 创建 `abi/AgentVault.json` 文件 (包含合约 ABI)
4. 配置环境变量: `RPC_URL`, `PRIVATE_KEY`, `CHAIN_ID`, `ADMIN_USERS`
5. 实现 `_send_transaction()` 私有方法用于签名和发送交易
6. 添加单元测试 (Mock Web3)
7. 代码通过 `pytest` 和 `ruff check`

## Tasks / Subtasks

- [x] **Task 1: 配置环境变量** (AC: #4)
  - [x] 在 `config.py` 添加 `RPC_URL`, `PRIVATE_KEY`, `CHAIN_ID`, `ADMIN_USERS`
  - [x] 更新 `.env.example` 添加新变量模板
  - [x] 添加 `is_admin()` 函数用于管理员权限检查

- [x] **Task 2: 创建合约 ABI 文件** (AC: #3)
  - [x] 创建 `abi/` 目录
  - [x] 创建 `abi/AgentVault.json` 包含核心方法 ABI:
    - `disableStrategy(uint256)`
    - `disableAllActiveStrategies()`
    - `addStrategy(bytes32,uint256,uint8)`
    - `pauseVault(bool)`
    - `updateSettings(tuple)`
    - `withdraw(uint256)`

- [x] **Task 3: 实现 VaultContract 类** (AC: #2, #5)
  - [x] 创建 `contract.py` 模块
  - [x] 实现 `__init__()` 初始化 Web3 连接和合约实例
  - [x] 实现 `_send_transaction(tx_func)` 私有方法:
    - 构建交易
    - 签名交易
    - 发送并等待确认
    - 返回交易哈希或错误
  - [x] 实现基本的错误处理和日志

- [x] **Task 4: 添加单元测试** (AC: #6, #7)
  - [x] 创建 `tests/unit/web3/test_contract.py`
  - [x] Mock `Web3` 和合约调用
  - [x] 测试 `VaultContract` 初始化
  - [x] 测试 `_send_transaction()` 成功和失败场景

## Dev Notes

### 技术栈要求

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | >=3.12 | 主要开发语言 |
| web3.py | >=6.0.0 | 智能合约交互 (已在 requirements.txt) |
| python-dotenv | >=1.0.0 | 环境变量管理 |

### 代码模式

**遵循现有代码风格 (参考 api.py):**

```python
# contract.py 结构
from web3 import Web3
from config import RPC_URL, PRIVATE_KEY, CHAIN_ID, VAULT_ADDRESS
import json
import logging

logger = logging.getLogger(__name__)

class VaultContract:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
        self.contract = self._load_contract()

    def _load_contract(self):
        with open("abi/AgentVault.json") as f:
            abi = json.load(f)
        return self.w3.eth.contract(
            address=Web3.to_checksum_address(VAULT_ADDRESS),
            abi=abi
        )

    async def _send_transaction(self, tx_func) -> dict:
        """签名、发送并等待交易确认"""
        try:
            # 构建交易
            tx = tx_func()
            tx.update({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
                "chainId": CHAIN_ID,
            })
            # 签名
            signed = self.account.sign_transaction(tx)
            # 发送
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            # 等待确认
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return {"success": True, "tx_hash": tx_hash.hex()}
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            return {"success": False, "error": str(e)}
```

**config.py 扩展:**

```python
# 新增环境变量
RPC_URL = os.getenv('RPC_URL', '')
PRIVATE_KEY = os.getenv('PRIVATE_KEY', '')
CHAIN_ID = int(os.getenv('CHAIN_ID', '1'))
ADMIN_USERS = [
    int(x) for x in os.getenv('ADMIN_USERS', '').split(',')
    if x.strip().isdigit()
]

def is_admin(user_id: int) -> bool:
    """检查用户是否为管理员"""
    if not ADMIN_USERS:
        return True  # 未配置时允许所有
    return user_id in ADMIN_USERS
```

### 安全规则

```
🚨 私钥管理:
- 私钥永远不能硬编码在代码中
- 使用环境变量 PRIVATE_KEY
- .env 文件不提交到 Git

🚨 权限分级:
- 低风险(查询): ALLOWED_USERS
- 高风险(资金/策略): ADMIN_USERS
```

### 测试模式

```python
# tests/unit/test_contract.py
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

class TestVaultContract:
    @pytest.mark.asyncio
    async def test_init_success(self):
        """测试 VaultContract 初始化成功"""
        with patch("contract.Web3") as mock_web3:
            mock_w3 = MagicMock()
            mock_web3.HTTPProvider.return_value = mock_w3
            mock_web3.return_value.eth.account.from_key.return_value = MagicMock(address="0xTest")

            from contract import VaultContract
            vc = VaultContract()

            assert vc.w3 is not None

    @pytest.mark.asyncio
    async def test_send_transaction_success(self):
        """测试 _send_transaction 成功场景"""
        # Mock Web3 和交易流程
        pass
```

### Project Structure Notes

**新增文件:**
```
dx-terminal-monitor/
├── contract.py          # 新增 - Web3 合约交互
├── abi/                 # 新增目录
│   └── AgentVault.json  # 新增 - 合约 ABI
├── config.py            # 修改 - 添加新环境变量
├── .env.example         # 修改 - 添加新变量模板
└── tests/
    └── unit/
        └── test_contract.py  # 新增 - 合约单元测试
```

**文件位置遵循现有结构:**
- `contract.py` 与 `api.py`, `main.py` 同级
- ABI 文件放在 `abi/` 目录
- 测试放在 `tests/unit/` 目录

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic1-Story1.0]
- [Source: _bmad-output/project-context.md#技术栈]
- [Source: _bmad-output/project-context.md#安全规则]
- [Source: api.py - TerminalAPI 类模式参考]
- [Source: config.py - 环境变量模式参考]
- [Source: tests/conftest.py - 测试 fixture 模式参考]

## Dev Agent Record

### Agent Model Used

GLM-5

### Debug Log References

无

### Completion Notes List

- **Task 1 完成**: 在 `config.py` 添加了 `RPC_URL`, `PRIVATE_KEY`, `CHAIN_ID`, `ADMIN_USERS` 环境变量和 `is_admin()` 函数
- **Task 2 完成**: 创建了 `abi/` 目录和 `abi/AgentVault.json` 文件，包含 6 个核心合约方法的 ABI
- **Task 3 完成**: 创建了 `contract.py` 模块，实现了 `VaultContract` 类:
  - `__init__()`: 初始化 Web3 连接、账户和合约实例
  - `_load_contract()`: 加载 ABI 文件并创建合约实例
  - `_send_transaction()`: 签名、发送并等待交易确认，返回结果字典
  - 完整的错误处理和日志记录
- **Task 4 完成**: 创建了 `tests/unit/web3/test_contract.py`:
  - 26 个测试用例，覆盖模块导入、ABI 加载、环境配置、类结构、交易方法和错误处理
  - 所有测试通过 (98 个单元测试全部通过)
  - ruff check 通过

### Code Review Fixes (2026-03-01)

**修复的 HIGH 问题:**
1. `_send_transaction` 改为 async 方法 (contract.py:74) - 避免阻塞 asyncio 事件循环
2. 创建 `tests/unit/web3/__init__.py` - 修复 Story File List 声明
3. `_send_transaction` 返回错误字典而非抛出异常 - 符合 Dev Notes 规范

**修复的 MEDIUM 问题:**
4. `is_admin()` 未配置时返回 False (安全默认值) - 防止未配置时所有用户都是管理员
5. 修正 File List: `tests/support/web3_fixtures.py` 是新增文件，非修改文件
6. 修复 `rawTransaction` -> `raw_transaction` (web3.py snake_case)

### File List

**新增文件:**
- `abi/AgentVault.json` - AgentVault 智能合约 ABI
- `contract.py` - Web3 合约交互模块
- `tests/unit/web3/__init__.py` - Web3 测试包初始化文件
- `tests/unit/web3/test_contract.py` - 合约模块单元测试
- `tests/support/web3_fixtures.py` - Web3 mock fixtures

**修改文件:**
- `config.py` - 添加 Web3 配置变量、logger 和 is_admin() 函数

**依赖更新:**
- web3>=6.0.0 已安装 (web3-7.14.1)
