# DX Terminal Monitor 测试文档

本项目使用 **pytest** 作为测试框架，配合 pytest-asyncio 支持异步测试。

---

## 目录结构

```
tests/
├── conftest.py              # 共享 fixtures 和配置
├── unit/                    # 单元测试 (快速, 无外部依赖)
├── integration/             # 集成测试 (组件间协作)
├── api/                     # API 测试 (外部服务)
└── support/                 # 测试辅助工具
    └── helpers.py           # 辅助函数
```

---

## 环境设置

### 1. 安装测试依赖

```bash
# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装测试依赖
pip install -r requirements-test.txt
```

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env.test

# 根据需要编辑 .env.test
```

---

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定类型的测试

```bash
# 单元测试 (快速)
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# API 测试 (需要网络)
pytest -m api -v
```

### 按标记运行

```bash
# 只运行单元测试
pytest -m unit

# 排除慢测试
pytest -m "not slow"

# 运行 API 测试
pytest -m api
```

### 详细输出

```bash
# 显示所有测试名称
pytest -v

# 显示测试中的 print 输出
pytest -s

# 失败时显示更多上下文
pytest --tb=long
```

### 调试模式

```bash
# 进入 pdb 调试器 (失败时)
pytest --pdb

# 在测试开始时进入 pdb
pytest --trace
```

---

## 代码覆盖率

```bash
# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html

# 查看报告
open htmlcov/index.html
```

---

## Fixtures

本项目提供了以下 fixtures (定义在 `conftest.py`):

| Fixture | 描述 | 作用域 |
|---------|------|--------|
| `event_loop` | 异步事件循环 | session |
| `test_config` | 测试配置值 | function |
| `mock_telegram_update` | 模拟 Telegram Update 对象 | function |
| `mock_telegram_context` | 模拟 Telegram Context 对象 | function |
| `mock_api_response_positions` | 示例 positions API 响应 | function |
| `mock_api_response_activity` | 示例 activity API 响应 | function |
| `mock_api_response_vault` | 示例 vault API 响应 | function |
| `mock_terminal_api` | 模拟 TerminalAPI 实例 | function |
| `position_factory` | Position 数据工厂 | function |
| `activity_factory` | Activity 数据工厂 | function |

### 使用示例

```python
@pytest.mark.asyncio
async def test_with_mock(mock_telegram_update, mock_api_response_positions):
    """使用 mock fixtures 的测试示例。"""
    update = mock_telegram_update
    update.effective_user.id = 123456789

    # 测试逻辑...
```

---

## 数据工厂

### PositionFactory

```python
def test_with_position(position_factory):
    """使用工厂创建测试数据。"""
    position = position_factory.create(
        token_symbol="ETH",
        current_value_usd="3500.00",
    )
```

### ActivityFactory

```python
def test_with_activity(activity_factory):
    """使用工厂创建活动数据。"""
    swap = activity_factory.create_swap(side="buy")
    deposit = activity_factory.create_deposit()
    withdrawal = activity_factory.create_withdrawal()
```

---

## 测试标记

使用 `@pytest.mark` 装饰器标记测试:

```python
@pytest.mark.unit
def test_fast_unit_test():
    """快速单元测试。"""
    pass

@pytest.mark.integration
def test_integration_test():
    """集成测试。"""
    pass

@pytest.mark.api
@pytest.mark.asyncio
async def test_external_api():
    """外部 API 测试。"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """慢速测试。"""
    pass
```

---

## 最佳实践

### 1. 测试命名

- 测试文件: `test_*.py`
- 测试类: `Test*`
- 测试函数: `test_*`

### 2. 测试结构 (Given-When-Then)

```python
def test_example():
    # Given (准备)
    data = {"key": "value"}

    # When (执行)
    result = process(data)

    # Then (验证)
    assert result == expected
```

### 3. 异步测试

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result is not None
```

### 4. 使用 Fixtures 隔离

```python
def test_isolated(mock_telegram_update):
    # 使用 mock 隔离外部依赖
    pass
```

### 5. 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    ("0", "0.000000"),
    ("1000000000000000000", "1.000000"),
])
def test_format_eth(input, expected):
    assert format_eth(input) == expected
```

---

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements-test.txt
      - run: pytest -m "not api" --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v4
```

---

## 常见问题

### Q: 测试找不到模块

确保从项目根目录运行 pytest:
```bash
cd /path/to/dx-terminal-monitor
pytest
```

### Q: 异步测试失败

确保测试函数有 `@pytest.mark.asyncio` 装饰器。

### Q: API 测试超时

API 测试需要网络连接，确保网络可用或使用 mock:
```bash
# 跳过 API 测试
pytest -m "not api"
```

---

## 参考资源

- [pytest 文档](https://docs.pytest.org/)
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov 文档](https://pytest-cov.readthedocs.io/)
