# DX Terminal Monitor - 项目概述

## 项目信息

- **项目名称**: DX Terminal Monitor
- **类型**: 单体应用 (Monolith)
- **主要语言**: Python 3
- **架构模式**: Bot 服务 / API 客户端

## 执行摘要

DX Terminal Monitor 是一个 Telegram Bot 服务，用于监控 Terminal Markets Vault 的投资组合状态。用户可以通过 Telegram 命令查询账户余额、持仓、盈亏、交易活动等信息。

## 技术栈概览

| 类别 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 语言 | Python | 3.x | 主要开发语言 |
| Bot 框架 | python-telegram-bot | >=21.0 | Telegram Bot API 封装 |
| HTTP 客户端 | aiohttp | >=3.9.3 | 异步 HTTP 请求 |
| 配置管理 | python-dotenv | >=1.0.0 | 环境变量加载 |

## 架构分类

- **架构类型**: 后端 Bot 服务
- **通信模式**: Telegram Bot API (Long Polling)
- **外部 API**: Terminal Markets API v1

## 仓库结构

```
dx-terminal-monitor/
├── main.py          # 主入口，Bot 命令处理
├── api.py           # Terminal API 客户端
├── config.py        # 配置管理
├── requirements.txt # Python 依赖
├── start.sh         # 启动脚本
├── .env             # 环境变量（不提交）
├── .env.example     # 环境变量模板
└── docs/            # 项目文档
```

## 主要功能

1. **账户监控**: 查询 Vault 余额和总价值
2. **持仓管理**: 查看当前持仓及盈亏
3. **交易记录**: 查看最近的交易活动
4. **策略跟踪**: 查看活跃的交易策略
5. **Vault 信息**: 查询 Vault 配置和状态

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/terryso/dx-terminal-monitor.git
cd dx-terminal-monitor

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 Bot Token 和用户 ID

# 启动
python main.py
```

## 相关文档

- [架构文档](./architecture.md)
- [API 合约](./api-contracts.md)
- [开发指南](./development-guide.md)
- [源码树分析](./source-tree-analysis.md)
