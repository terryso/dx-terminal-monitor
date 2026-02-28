---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04c-aggregate
  - step-05-validate-and-complete
lastStep: 'step-05-validate-and-complete'
lastSaved: '2026-03-01'
workflowType: 'testarch-atdd'
inputDocuments:
  - _bmad-output/implementation-artifacts/1-2-disable-all-strategies.md
  - _bmad-output/planning-artifacts/epics.md
  - tests/unit/test_command_handlers_p1.py
  - tests/conftest.py
detected_stack: backend
test_framework: pytest
generation_mode: ai-generation
---

# ATDD Checklist - Epic 1, Story 1-2: 禁用所有策略命令

**Date:** 2026-03-01
**Author:** Nick
**Primary Test Level:** Unit (pytest)

---

## Story Summary

作为**用户**，我需要**通过 `/disable_all` 命令一键禁用所有活跃策略**，以便**紧急情况下快速停止所有交易**。

**As a** Vault Owner
**I want** to disable all active strategies with a single `/disable_all` command
**So that** I can quickly stop all trading in emergency situations

---

## Acceptance Criteria

1. 实现 `contract.disable_all_strategies()` 方法
2. 实现 `cmd_disable_all` 命令处理函数
3. 成功时返回禁用数量和交易哈希
4. 无活跃策略时返回: "没有活跃策略"
5. 未授权用户返回: "未授权"
6. 添加单元测试

---

## Test Strategy

### Test Level Selection

| 验收标准 | 测试级别 | 优先级 | 原因 |
|----------|----------|--------|------|
| AC1: disable_all_strategies() 方法 | Unit | P0 | 纯业务逻辑，Mock Web3 |
| AC2: cmd_disable_all 处理函数 | Unit | P0 | 命令处理逻辑 |
| AC3: 成功响应格式 | Unit | P0 | 输出验证 |
| AC4: 无活跃策略响应 | Unit | P1 | 边界条件 |
| AC5: 未授权用户处理 | Unit | P0 | 安全关键 |
| AC6: 单元测试 | Unit | P0 | 测试覆盖 |

### Priority Matrix

| 优先级 | 定义 | 测试数量 |
|--------|------|----------|
| P0 | 关键路径，必须通过 | 5 |
| P1 | 重要边界条件 | 3 |

---

## Failing Tests Created (RED Phase)

### Unit Tests (8 tests)

**File:** `tests/unit/test_command_handlers_p1.py` (追加到现有文件)

**Tests for TestCmdDisableAll class:**

| 测试 | 状态 | 验证点 | 优先级 |
|------|------|--------|--------|
| `test_cmd_disable_all_success` | RED | 成功禁用多个策略 | P0 |
| `test_cmd_disable_all_no_active_strategies` | RED | 无活跃策略场景 | P1 |
| `test_cmd_disable_all_unauthorized` | RED | 未授权用户被拒绝 | P0 |
| `test_cmd_disable_all_contract_fails` | RED | 合约调用失败处理 | P1 |
| `test_cmd_disable_all_contract_method_calls_disableAllActiveStrategies` | RED | 验证合约方法调用 | P0 |
| `test_cmd_disable_all_registers_command_handler` | RED | 验证命令注册 | P1 |
| `test_cmd_disable_all_registers_bot_command` | RED | 验证菜单命令注册 | P1 |
| `test_cmd_disable_all_help_text_updated` | RED | 验证帮助文本更新 | P1 |

---

## Test Code (RED Phase - Failing Tests)

将以下测试类添加到 `tests/unit/test_command_handlers_p1.py`:

```python
# =============================================================================
# Tests for cmd_disable_all (Story 1.2 - ATDD RED PHASE)
# These tests are intentionally designed to FAIL until the feature is implemented.
# =============================================================================

class TestCmdDisableAll:
    """Tests for /disable_all command (Story 1.2)."""

    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Set up environment and isolate main module."""
        import os
        import sys

        # Set environment variables
        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        # Remove main and contract from cache if loaded
        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        yield

        # Clean up
        for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
            os.environ.pop(key, None)
        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

    @pytest.fixture
    def mock_contract_instance(self) -> MagicMock:
        """Create a mock contract instance."""
        contract_mock = MagicMock()
        contract_mock.disable_all_strategies = AsyncMock(return_value={
            'success': True,
            'transactionHash': '0xabc123...',
            'disabledCount': 3,
        })
        return contract_mock

    @pytest.mark.asyncio
    async def test_cmd_disable_all_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
        mock_contract_instance: MagicMock,
    ) -> None:
        """Test successful disable all strategies (P0)."""
        # Given
        mock_tx_hash = "0xdef456..."
        disabled_count = 3
        mock_contract_instance.disable_all_strategies.return_value = {
            'success': True,
            'transactionHash': mock_tx_hash,
            'disabledCount': disabled_count,
        }

        with patch("contract.VaultContract", return_value=mock_contract_instance):
            from main import cmd_disable_all

            with patch("main.authorized", return_value=True):
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_all(mock_telegram_update, mock_telegram_context)

                # Then
                mock_contract_instance.disable_all_strategies.assert_called_once()
                call_args = mock_telegram_update.message.reply_text.call_args[0][0]
                assert "已禁用" in call_args
                assert str(disabled_count) in call_args
                assert mock_tx_hash in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_all_no_active_strategies(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
        mock_contract_instance: MagicMock,
    ) -> None:
        """Test disable all when no active strategies (P1)."""
        # Given
        mock_contract_instance.disable_all_strategies.return_value = {
            'success': True,
            'transactionHash': '0xabc123...',
            'disabledCount': 0,
        }

        with patch("contract.VaultContract", return_value=mock_contract_instance):
            from main import cmd_disable_all

            with patch("main.authorized", return_value=True):
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_all(mock_telegram_update, mock_telegram_context)

                # Then
                call_args = mock_telegram_update.message.reply_text.call_args[0][0]
                assert "没有活跃策略" in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_all_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test disable all rejects unauthorized users (P0)."""
        # Given
        mock_contract = MagicMock()

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_all

            with patch("main.authorized", return_value=False):
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_all(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with("未授权")

    @pytest.mark.asyncio
    async def test_cmd_disable_all_contract_fails(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
        mock_contract_instance: MagicMock,
    ) -> None:
        """Test disable all with contract error (P1)."""
        # Given
        error_msg = "Gas estimation failed"
        mock_contract_instance.disable_all_strategies.return_value = {
            'success': False,
            'error': error_msg,
        }

        with patch("contract.VaultContract", return_value=mock_contract_instance):
            from main import cmd_disable_all

            with patch("main.authorized", return_value=True):
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_all(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "交易失败" in call_args
        assert error_msg in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_all_contract_method_calls_disableAllActiveStrategies(
        self,
    ) -> None:
        """Test contract.disable_all_strategies calls web3 disableAllActiveStrategies (Unit)."""
        # This test validates the contract.py method, not the command handler
        # Given
        from contract import VaultContract

        # Create a mock instance with proper setup
        mock_vault = MagicMock(spec=VaultContract)
        mock_vault._send_transaction = AsyncMock(return_value={
            'success': True,
            'transactionHash': '0xabc123...',
            'disabledCount': 3,
        })
        mock_vault.contract = MagicMock()
        mock_vault.contract.functions.disableAllActiveStrategies.return_value = "mock_tx_func"

        # When
        result = await VaultContract.disable_all_strategies(mock_vault)

        # Then
        assert result['success'] is True
        assert 'transactionHash' in result
        mock_vault._send_transaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_disable_all_registers_command_handler(
        self,
    ) -> None:
        """Test cmd_disable_all is registered as command handler (P1)."""
        import os
        import sys

        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        try:
            from main import create_app

            app = create_app()

            # Check if disable_all handler is registered
            handlers = app.handlers
            has_disable_all = any(
                'disable_all' in str(h) for h in handlers
            )

            assert has_disable_all, "Command handler for 'disable_all' not registered"
        finally:
            for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
                os.environ.pop(key, None)

    @pytest.mark.asyncio
    async def test_cmd_disable_all_registers_bot_command(
        self,
    ) -> None:
        """Test disable_all is registered in bot menu (P1)."""
        import os
        import sys

        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        try:
            from unittest.mock import MagicMock, AsyncMock, patch
            from telegram import BotCommand

            # Mock the bot
            mock_bot = MagicMock()
            mock_bot.set_my_commands = AsyncMock()

            mock_app = MagicMock()
            mock_app.bot = mock_bot

            from main import post_init
            import asyncio

            # Run post_init
            asyncio.get_event_loop().run_until_complete(post_init(mock_app))

            # Check if set_my_commands was called
            mock_bot.set_my_commands.assert_called_once()
            commands = mock_bot.set_my_commands.call_args[0][0]

            # Verify disable_all command is in the list
            command_names = [cmd.command if hasattr(cmd, 'command') else str(cmd) for cmd in commands]
            assert 'disable_all' in command_names, "'disable_all' not in bot commands"
        finally:
            for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
                os.environ.pop(key, None)

    @pytest.mark.asyncio
    async def test_cmd_disable_all_help_text_updated(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test help text includes disable_all command (P1)."""
        import os
        import sys

        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        try:
            from main import cmd_start

            with patch("main.authorized", return_value=True):
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_start(mock_telegram_update, mock_telegram_context)

                # Then
                call_args = mock_telegram_update.message.reply_text.call_args[0][0]
                assert "disable_all" in call_args.lower() or "/disable_all" in call_args
        finally:
            for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
                os.environ.pop(key, None)
```

---

## Implementation Checklist

### Test: test_cmd_disable_all_success

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 在 `contract.py` 添加 `disable_all_strategies()` 方法
- [ ] 在 `main.py` 添加 `cmd_disable_all` 异步函数
- [ ] 权限检查: 使用 `authorized()` 函数
- [ ] 调用 `contract().disable_all_strategies()`
- [ ] 格式化成功响应 (包含禁用数量和交易哈希)
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_success -v`

**Estimated Effort:** 1 hour

---

### Test: test_cmd_disable_all_no_active_strategies

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 处理 `disabledCount == 0` 的情况
- [ ] 返回 "没有活跃策略" 消息
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_no_active_strategies -v`

**Estimated Effort:** 0.25 hour

---

### Test: test_cmd_disable_all_unauthorized

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 确保权限检查在函数开头
- [ ] 未授权时返回 "未授权"
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_unauthorized -v`

**Estimated Effort:** 0.25 hour

---

### Test: test_cmd_disable_all_contract_fails

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 处理合约调用失败场景
- [ ] 返回 "交易失败: {error}" 消息
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_contract_fails -v`

**Estimated Effort:** 0.25 hour

---

### Test: test_cmd_disable_all_contract_method_calls_disableAllActiveStrategies

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 在 `VaultContract` 类实现 `disable_all_strategies()` 方法
- [ ] 调用 `self.contract.functions.disableAllActiveStrategies()`
- [ ] 使用 `await self._send_transaction(tx_func)` 发送交易
- [ ] 返回包含 success, transactionHash, disabledCount 的字典
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_contract_method_calls_disableAllActiveStrategies -v`

**Estimated Effort:** 0.5 hour

---

### Test: test_cmd_disable_all_registers_command_handler

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 在 `create_app()` 函数添加 `CommandHandler("disable_all", cmd_disable_all)`
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_registers_command_handler -v`

**Estimated Effort:** 0.25 hour

---

### Test: test_cmd_disable_all_registers_bot_command

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 在 `post_init()` 添加菜单项 `BotCommand("disable_all", "Disable all strategies")`
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_registers_bot_command -v`

**Estimated Effort:** 0.25 hour

---

### Test: test_cmd_disable_all_help_text_updated

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 在 `cmd_start` 的帮助文本添加 `/disable_all` 说明
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_help_text_updated -v`

**Estimated Effort:** 0.25 hour

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_command_handlers_p1.py::TestCmdDisableAll -v

# Run specific test file
pytest tests/unit/test_command_handlers_p1.py -v

# Run with coverage
pytest tests/unit/test_command_handlers_p1.py --cov=main --cov=contract --cov-report=term-missing

# Run all unit tests
pytest tests/unit/ -v
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete)

**TEA Agent Responsibilities:**

- [x] All tests written and designed to fail
- [x] Test fixtures use existing conftest.py patterns
- [x] Mock requirements documented
- [x] Implementation checklist created

**Verification:**

- All tests will fail until `cmd_disable_all` is implemented
- Tests assert EXPECTED behavior (not placeholders)
- Tests follow existing patterns from `TestCmdDisableStrategy`

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test** from implementation checklist (start with P0 tests)
2. **Read the test** to understand expected behavior
3. **Implement minimal code** to make that specific test pass
4. **Run the test** to verify it now passes (green)
5. **Check off the task** in implementation checklist
6. **Move to next test** and repeat

**Key Principles:**

- One test at a time (don't try to fix all at once)
- Minimal implementation (don't over-engineer)
- Run tests frequently (immediate feedback)
- Use implementation checklist as roadmap

**Recommended Implementation Order:**

1. `test_cmd_disable_all_contract_method_calls_disableAllActiveStrategies` - Implement contract method first
2. `test_cmd_disable_all_success` - Implement command handler
3. `test_cmd_disable_all_no_active_strategies` - Handle empty case
4. `test_cmd_disable_all_unauthorized` - Add auth check
5. `test_cmd_disable_all_contract_fails` - Add error handling
6. `test_cmd_disable_all_registers_command_handler` - Register handler
7. `test_cmd_disable_all_registers_bot_command` - Add to menu
8. `test_cmd_disable_all_help_text_updated` - Update help text

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**

1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (readability, maintainability, performance)
3. **Extract duplications** (DRY principle)
4. **Ensure tests still pass** after each refactor
5. **Update documentation** (if API contracts change)

---

## Next Steps

1. **Run failing tests** to confirm RED phase: `pytest tests/unit/test_command_handlers_p1.py::TestCmdDisableAll -v`
2. **Begin implementation** using implementation checklist as guide
3. **Work one test at a time** (red -> green for each)
4. **When all tests pass**, update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns using pytest fixtures with overrides support
- **test-quality.md** - Test design principles (Given-When-Then, one assertion per test, determinism, isolation)
- **test-levels-framework.md** - Test level selection framework (Unit tests for backend)
- **test-priorities-matrix.md** - P0-P3 prioritization criteria

---

## Notes

- Tests follow the same pattern as `TestCmdDisableStrategy` (Story 1-1)
- Uses existing fixtures from `conftest.py`: `mock_telegram_update`, `mock_telegram_context`
- Environment isolation handled in `setup_environment` fixture
- Contract mocking follows existing patterns from Story 1-1 tests

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/unit/test_command_handlers_p1.py::TestCmdDisableAll -v`

**Results:**
```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/nick/projects/dx-terminal-monitor
plugins: anyio-4.12.1, asyncio-1.3.0, aiohttp-1.1.0, cov-7.0.0
asyncio: mode=Mode.AUTO, debug=False

collected 8 items

tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_success FAILED [ 12%]
tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_no_active_strategies FAILED [ 25%]
tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_unauthorized FAILED [ 37%]
tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_contract_fails FAILED [ 50%]
tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_contract_method_calls_disableAllActiveStrategies FAILED [ 62%]
tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_registers_command_handler FAILED [ 75%]
tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_registers_bot_command FAILED [ 87%]
tests/unit/test_command_handlers_p1.py::TestCmdDisableAll::test_cmd_disable_all_help_text_updated FAILED [100%]

=================================== FAILURES ===================================
test_cmd_disable_all_success: ImportError: cannot import name 'cmd_disable_all' from 'main'
test_cmd_disable_all_no_active_strategies: ImportError: cannot import name 'cmd_disable_all' from 'main'
test_cmd_disable_all_unauthorized: ImportError: cannot import name 'cmd_disable_all' from 'main'
test_cmd_disable_all_contract_fails: ImportError: cannot import name 'cmd_disable_all' from 'main'
test_cmd_disable_all_contract_method_calls_disableAllActiveStrategies: AttributeError: type object 'VaultContract' has no attribute 'disable_all_strategies'
test_cmd_disable_all_registers_command_handler: AssertionError: Command handler for 'disable_all' not registered
test_cmd_disable_all_registers_bot_command: RuntimeError: This event loop is already running
test_cmd_disable_all_help_text_updated: AssertionError: 'disable_all' not in help text

============================== 8 failed in 0.53s ===============================
```

**Summary:**

- Total tests: 8
- Passing: 0 (expected)
- Failing: 8 (expected)
- Status: RED phase verified

**Expected Failure Messages:**
1. `ImportError: cannot import name 'cmd_disable_all' from 'main'` - Function not implemented yet
2. `AttributeError: type object 'VaultContract' has no attribute 'disable_all_strategies'` - Method not implemented yet
3. `AssertionError: Command handler for 'disable_all' not registered` - Handler registration needed
4. `AssertionError: 'disable_all' not in help text` - Help text update needed

---

**Generated by BMad TEA Agent** - 2026-03-01
