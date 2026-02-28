---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04c-aggregate
  - step-05-validate-and-complete
lastStep: step-05-validate-and-complete
lastSaved: '2026-03-01'
workflowType: 'testarch-atdd'
inputDocuments:
  - _bmad-output/planning-artifacts/epics.md
  - _bmad/tea/testarch/knowledge/data-factories.md
  - _bmad/tea/testarch/knowledge/test-quality.md
  - _bmad/tea/testarch/knowledge/test-healing-patterns.md
  - _bmad/tea/testarch/knowledge/test-levels-framework.md
  - _bmad/tea/testarch/knowledge/test-priorities-matrix.md
  - _bmad/tea/testarch/knowledge/overview.md
  - _bmad/tea/testarch/knowledge/api-request.md
---

# ATDD Checklist - Epic 1, Story 1.0: Web3 基础设施搭建

**Date:** 2026-03-01
**Author:** Nick
**Primary Test Level:** Unit (Backend)

---

## Story Summary

作为开发者，我需要搭建 web3.py 基础设施，以便安全地与智能合约交互。

**As a** 开发者
**I want** 搭建 web3.py 基础设施
**So that** 安全地与 AgentVault 智能合约交互

---

## Acceptance Criteria

| ID | 验收标准 | 测试覆盖 |
|----|----------|----------|
| AC1 | 安装 web3.py 依赖 | 配置项，无需测试 |
| AC2 | 创建 `contract.py` 模块 | ✅ TestContractModuleExists |
| AC3 | 创建 `abi/AgentVault.json` 文件 | ✅ TestABIFileLoading |
| AC4 | 配置环境变量 (RPC_URL, PRIVATE_KEY, CHAIN_ID) | ✅ TestEnvironmentConfiguration |
| AC5 | 实现 `VaultContract` 类基础结构 | ✅ TestVaultContractClassStructure |
| AC6 | 实现 `_send_transaction()` 私有方法 | ✅ TestSendTransactionMethod |
| AC7 | 添加单元测试（Mock Web3） | ✅ 测试文件本身 |

---

## Failing Tests Created (RED Phase)

### Unit Tests (22 tests)

**File:** `tests/unit/web3/test_contract.py` (~280 lines)

| 测试类 | 测试数量 | 优先级 | 状态 |
|--------|----------|--------|------|
| TestContractModuleExists | 2 | P1 | 🔴 RED - 模块不存在 |
| TestABIFileLoading | 3 | P0 | 🔴 RED - ABI 文件不存在 |
| TestEnvironmentConfiguration | 4 | P0 | 🔴 RED - 配置模块不存在 |
| TestVaultContractClassStructure | 6 | P0 | 🔴 RED - 类不存在 |
| TestSendTransactionMethod | 5 | P0 | 🔴 RED - 方法不存在 |
| TestSendTransactionErrorHandling | 3 | P1 | 🔴 RED - 错误处理不存在 |

**所有测试使用 `@pytest.mark.skip` 标记 - TDD RED PHASE**

---

## Data Factories Created

### Web3DataFactory

**File:** `tests/support/web3_fixtures.py`

**Exports:**

- `create_strategy(id, content, expiry, priority, active)` - 创建策略对象
- `create_transaction_hash()` - 创建模拟交易哈希
- `create_address(prefix)` - 创建模拟以太坊地址
- `create_gas_price(gwei)` - 创建 Gas 价格 (Wei)
- `create_eth_amount(eth)` - 创建 ETH 金额 (Wei)

**Example Usage:**

```python
from tests.support.web3_fixtures import Web3DataFactory

factory = Web3DataFactory()
strategy = factory.create_strategy(strategy_id=1, content="Test strategy")
tx_hash = factory.create_transaction_hash()
```

---

## Fixtures Created

### Web3 Mock Fixtures

**File:** `tests/support/web3_fixtures.py`

**Fixtures:**

- `mock_web3` - Mock Web3 实例
  - **Setup:** 创建 MagicMock 模拟 Web3
  - **Provides:** eth.gas_price, eth.chain_id, eth.get_transaction_count

- `mock_account` - Mock 以太坊账户
  - **Setup:** 创建 MagicMock 模拟账户
  - **Provides:** address, sign_transaction()

- `mock_contract` - Mock 智能合约实例
  - **Setup:** 创建 MagicMock 模拟合约
  - **Provides:** functions.disableStrategy(), functions.disableAllActiveStrategies()

- `mock_transaction_receipt` - Mock 交易收据（成功）
  - **Setup:** 创建成功交易收据字典
  - **Provides:** status=1, transactionHash, blockNumber

- `mock_failed_receipt` - Mock 交易收据（失败）
  - **Setup:** 创建失败交易收据字典
  - **Provides:** status=0, transactionHash, blockNumber

- `web3_env` - 环境变量设置/恢复
  - **Setup:** 设置 RPC_URL, PRIVATE_KEY, CHAIN_ID, VAULT_ADDRESS
  - **Cleanup:** 恢复原始环境变量

**Example Usage:**

```python
def test_with_mock(mock_web3, mock_account, web3_env):
    # mock_web3 已准备好使用
    assert mock_web3.eth.chain_id == 1
```

---

## Mock Requirements

### Web3.py Mock

**模块:** `web3`

**需要 Mock 的对象:**

- `Web3` - 主类
- `Web3.HTTPProvider` - HTTP 提供者
- `Web3.eth` - 以太坊接口
- `Web3.eth.account` - 账户管理
- `Web3.eth.contract` - 合约实例

**Success Pattern:**

```python
with patch('contract.Web3') as mock_web3:
    mock_instance = MagicMock()
    mock_web3.return_value = mock_instance
    # 测试代码...
```

---

## Required ABI Functions

合约 ABI 必须包含以下函数：

| 函数名 | 用途 | Story |
|--------|------|-------|
| `disableStrategy` | 禁用指定策略 | Story 1.1 |
| `disableAllActiveStrategies` | 禁用所有活跃策略 | Story 1.2 |
| `addStrategy` | 添加新策略 | Story 2.1 |
| `pauseVault` | 暂停/恢复 Agent 交易 | Story 2.2 |

---

## Implementation Checklist

### Test: TestContractModuleExists (2 tests)

**File:** `tests/unit/web3/test_contract.py`

**Tasks to make these tests pass:**

- [ ] 创建 `contract.py` 文件
- [ ] 定义 `VaultContract` 类
- [ ] 确保类可以被导入
- [ ] 移除 `@pytest.mark.skip` 装饰器
- [ ] 运行测试: `pytest tests/unit/web3/test_contract.py::TestContractModuleExists -v`
- [ ] ✅ 测试通过 (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: TestABIFileLoading (3 tests)

**File:** `tests/unit/web3/test_contract.py`

**Tasks to make these tests pass:**

- [ ] 创建 `abi/` 目录
- [ ] 获取 AgentVault 合约 ABI
- [ ] 创建 `abi/AgentVault.json` 文件
- [ ] 确保 ABI 包含 `disableStrategy` 函数定义
- [ ] 确保 ABI 包含 `disableAllActiveStrategies` 函数定义
- [ ] 确保 ABI 包含 `addStrategy` 函数定义
- [ ] 确保 ABI 包含 `pauseVault` 函数定义
- [ ] 移除 `@pytest.mark.skip` 装饰器
- [ ] 运行测试: `pytest tests/unit/web3/test_contract.py::TestABIFileLoading -v`
- [ ] ✅ 测试通过 (green phase)

**Estimated Effort:** 1 hour

---

### Test: TestEnvironmentConfiguration (4 tests)

**File:** `tests/unit/web3/test_contract.py`

**Tasks to make these tests pass:**

- [ ] 创建 `config.py` 模块（或在 contract.py 中包含配置函数）
- [ ] 实现 `get_rpc_url()` 函数
- [ ] 实现 `get_private_key()` 函数
- [ ] 实现 `get_chain_id()` 函数
- [ ] 添加环境变量读取逻辑
- [ ] 移除 `@pytest.mark.skip` 装饰器
- [ ] 运行测试: `pytest tests/unit/web3/test_contract.py::TestEnvironmentConfiguration -v`
- [ ] ✅ 测试通过 (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: TestVaultContractClassStructure (6 tests)

**File:** `tests/unit/web3/test_contract.py`

**Tasks to make these tests pass:**

- [ ] 在 `VaultContract.__init__()` 中初始化 `self.w3`
- [ ] 在 `VaultContract.__init__()` 中初始化 `self.account`
- [ ] 在 `VaultContract.__init__()` 中初始化 `self.contract`
- [ ] 在 `VaultContract.__init__()` 中初始化 `self.address`
- [ ] 从环境变量读取 VAULT_ADDRESS
- [ ] 使用 Web3.HTTPProvider 连接 RPC
- [ ] 使用私钥创建账户
- [ ] 加载合约 ABI 并创建合约实例
- [ ] 移除 `@pytest.mark.skip` 装饰器
- [ ] 运行测试: `pytest tests/unit/web3/test_contract.py::TestVaultContractClassStructure -v`
- [ ] ✅ 测试通过 (green phase)

**Estimated Effort:** 2 hours

---

### Test: TestSendTransactionMethod (5 tests)

**File:** `tests/unit/web3/test_contract.py`

**Tasks to make these tests pass:**

- [ ] 实现 `_send_transaction(self, tx_func)` 方法
- [ ] 调用 `tx_func.estimate_gas()` 估算 Gas
- [ ] 调用 `tx_func.build_transaction()` 构建交易
- [ ] 使用 `self.account.sign_transaction()` 签名
- [ ] 使用 `self.w3.eth.send_raw_transaction()` 发送
- [ ] 使用 `self.w3.eth.wait_for_transaction_receipt()` 等待确认
- [ ] 返回包含 `transactionHash` 和 `status` 的字典
- [ ] 移除 `@pytest.mark.skip` 装饰器
- [ ] 运行测试: `pytest tests/unit/web3/test_contract.py::TestSendTransactionMethod -v`
- [ ] ✅ 测试通过 (green phase)

**Estimated Effort:** 2 hours

---

### Test: TestSendTransactionErrorHandling (3 tests)

**File:** `tests/unit/web3/test_contract.py`

**Tasks to make these tests pass:**

- [ ] 在 `_send_transaction` 中添加 Gas 估算错误处理
- [ ] 在 `_send_transaction` 中添加网络错误处理
- [ ] 在 `_send_transaction` 中添加交易失败（status=0）检测
- [ ] 抛出有意义的异常消息
- [ ] 移除 `@pytest.mark.skip` 装饰器
- [ ] 运行测试: `pytest tests/unit/web3/test_contract.py::TestSendTransactionErrorHandling -v`
- [ ] ✅ 测试通过 (green phase)

**Estimated Effort:** 1 hour

---

## Running Tests

```bash
# Run all failing tests for this story (all will be skipped)
pytest tests/unit/web3/test_contract.py -v

# Run specific test class
pytest tests/unit/web3/test_contract.py::TestVaultContractClassStructure -v

# Run with coverage
pytest tests/unit/web3/test_contract.py --cov=contract --cov-report=term-missing

# After implementation - remove @pytest.mark.skip and run again
# Expected: All tests should PASS (green phase)
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ 22 failing tests written (all with @pytest.mark.skip)
- ✅ Fixtures and factories created with auto-cleanup
- ✅ Mock requirements documented
- ✅ Implementation checklist created

**Verification:**

- All tests are skipped (not yet runnable)
- Tests define expected behavior clearly
- Tests will fail (after unskipping) due to missing implementation

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one test class** from implementation checklist (start with TestContractModuleExists)
2. **Remove @pytest.mark.skip** from that test class
3. **Implement minimal code** to make those specific tests pass
4. **Run the tests** to verify they now pass (green)
5. **Check off the tasks** in implementation checklist
6. **Move to next test class** and repeat

**Key Principles:**

- One test class at a time (don't unskip all at once)
- Minimal implementation (don't over-engineer)
- Run tests frequently (immediate feedback)
- Use implementation checklist as roadmap

**Suggested Order:**

1. TestContractModuleExists (create module)
2. TestABIFileLoading (add ABI)
3. TestEnvironmentConfiguration (add config)
4. TestVaultContractClassStructure (implement class)
5. TestSendTransactionMethod (implement method)
6. TestSendTransactionErrorHandling (add error handling)

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**

1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (readability, maintainability, performance)
3. **Extract duplications** (DRY principle)
4. **Add docstrings** to public methods
5. **Ensure tests still pass** after each refactor
6. **Update documentation** (if API contracts change)

---

## Next Steps

1. **Share this checklist** with the dev workflow (handoff)
2. **Install web3.py dependency:** `pip install web3`
3. **Start implementation** using checklist as guide
4. **Work one test class at a time** (red → green for each)
5. **When all tests pass**, refactor code for quality
6. **Update story status** to 'done' in epics.md

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns for test data generation
- **test-quality.md** - Test design principles (isolation, explicit assertions)
- **test-healing-patterns.md** - Common failure patterns and fixes
- **test-levels-framework.md** - Unit test selection for backend
- **test-priorities-matrix.md** - P0-P3 prioritization

---

## Notes

- 私钥安全：确保 PRIVATE_KEY 不被提交到 Git
- ABI 文件：需要从合约部署获取真实的 ABI
- Gas 估算：生产环境可能需要更复杂的 Gas 策略
- 测试网：建议先在 Sepolia 测试网验证

---

**Generated by BMad TEA Agent** - 2026-03-01
