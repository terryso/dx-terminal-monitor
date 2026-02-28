# DX Terminal Monitor - 开发指南

## 环境准备

### 系统要求

- **Python**: 3.10+ (推荐 3.12+)
- **操作系统**: macOS / Linux / Windows
- **网络**: 可访问 Telegram API 和 Terminal Markets API

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/terryso/dx-terminal-monitor.git
cd dx-terminal-monitor

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt
```

### 配置

1. 复制配置模板:
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件:
```bash
# Telegram Bot Token (从 @BotFather 获取)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# 允许的 Telegram 用户 ID (逗号分隔)
# 从 @userinfobot 获取你的用户 ID
ALLOWED_USERS=123456789,987654321

# Terminal Markets Vault 地址
VAULT_ADDRESS=0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C

# API 基础 URL (通常不需要修改)
API_BASE_URL=https://api.terminal.markets/api/v1
```

## 运行

### 开发模式

```bash
# 激活虚拟环境
source venv/bin/activate

# 直接运行
python main.py
```

### 生产模式

```bash
# 使用启动脚本
./start.sh
```

启动脚本特性:
- 自动激活虚拟环境
- 后台运行
- 输出日志到 `bot.log`
- 保存 PID 到 `bot.pid`

### 管理后台进程

```bash
# 查看进程状态
cat bot.pid

# 停止进程
kill $(cat bot.pid)
```

## 项目结构

```
dx-terminal-monitor/
├── main.py          # 主入口 - Bot 命令处理
├── api.py           # Terminal API 客户端
├── config.py        # 配置管理
├── requirements.txt # 依赖列表
├── start.sh         # 启动脚本
├── .env             # 环境变量 (不提交)
└── .env.example     # 环境变量模板
```

## 添加新命令

### 1. 定义命令处理函数

在 `main.py` 中添加:

```python
async def cmd_newcommand(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """新命令说明"""
    if not authorized(update):
        return

    # 调用 API
    data = await api.get_something()

    # 处理错误
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    # 格式化响应
    msg = f"""
    响应内容
    """
    await update.message.reply_text(msg)
```

### 2. 注册命令处理器

在 `main()` 函数中添加:

```python
app.add_handler(CommandHandler("newcommand", cmd_newcommand))
```

### 3. 添加到命令菜单

在 `post_init()` 函数中添加:

```python
commands.append(BotCommand("newcommand", "新命令说明"))
```

### 4. 更新帮助信息

更新 `cmd_start()` 中的帮助文本。

## 添加新 API 方法

### 1. 在 `api.py` 中添加方法

```python
async def get_new_data(self, param: str) -> dict:
    """获取新数据"""
    return await self._get(
        f"/new-endpoint/{self.vault}",
        {"param": param}
    )
```

### 2. 在命令中调用

```python
data = await api.get_new_data("value")
```

## 代码风格

### 格式化

- 使用 4 空格缩进
- 函数间空 2 行
- 字符串优先使用单引号

### 类型注解

```python
async def get_data(self, limit: int = 10) -> dict:
    ...
```

### 异步编程

- 所有 I/O 操作使用 `async/await`
- 使用 `aiohttp` 进行 HTTP 请求

## 调试

### 日志级别

在 `main.py` 中修改:

```python
logging.basicConfig(
    level=logging.DEBUG  # 改为 DEBUG
)
```

### 测试 API 连接

```python
import asyncio
from api import TerminalAPI

async def test():
    api = TerminalAPI()
    data = await api.get_vault()
    print(data)

asyncio.run(test())
```

## 常见问题

### Bot 无响应

1. 检查网络连接
2. 确认 Bot Token 正确
3. 查看日志 `bot.log`

### 权限错误

1. 确认用户 ID 在 `ALLOWED_USERS` 中
2. 如果 `ALLOWED_USERS` 为空，则允许所有用户

### API 错误

1. 检查 Vault 地址是否正确
2. 检查 API_BASE_URL 是否可访问
3. 检查网络代理设置

## 部署建议

### 使用 systemd (Linux)

创建服务文件 `/etc/systemd/system/dx-terminal-monitor.service`:

```ini
[Unit]
Description=DX Terminal Monitor Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/dx-terminal-monitor
ExecStart=/path/to/dx-terminal-monitor/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务:
```bash
sudo systemctl enable dx-terminal-monitor
sudo systemctl start dx-terminal-monitor
```

### 使用 Docker

创建 `Dockerfile`:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

构建和运行:
```bash
docker build -t dx-terminal-monitor .
docker run -d --name bot --env-file .env dx-terminal-monitor
```

## 扩展开发

### 添加数据库支持

推荐使用 SQLite 或 PostgreSQL 配合 SQLAlchemy。

### 添加推送通知

可以实现定期检查并在特定条件触发时主动发送消息。

### 添加 Web 界面

可以使用 Flask 或 FastAPI 添加 Web 管理界面。
