# DX Terminal Monitor - 文档索引

## 项目概览

- **类型**: 单体应用 (Monolith)
- **主要语言**: Python 3
- **架构**: Bot 服务 / API 客户端

## 快速参考

| 项目 | 信息 |
|------|------|
| **语言** | Python 3.x |
| **框架** | python-telegram-bot >=21.0 |
| **入口点** | main.py → main() |
| **架构模式** | Bot 服务 |

## 生成的文档

### 核心文档

- [项目概述](./project-overview.md) - 项目简介、技术栈、快速开始
- [架构文档](./architecture.md) - 技术架构、组件设计、API 设计
- [源码树分析](./source-tree-analysis.md) - 目录结构、文件说明、依赖关系
- [API 合约](./api-contracts.md) - Telegram 命令、Terminal API 端点
- [开发指南](./development-guide.md) - 环境配置、开发流程、部署指南

### 状态文件

- [project-scan-report.json](./project-scan-report.json) - 扫描状态和元数据

## 现有文档

- [README.md](../README.md) - 英文说明
- [README_CN.md](../README_CN.md) - 中文说明
- [LICENSE](../LICENSE) - MIT 许可证

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
# 编辑 .env 填入配置

# 启动
python main.py
```

## Bot 命令

| 命令 | 说明 |
|------|------|
| `/start` | 帮助信息 |
| `/balance` | 余额查询 |
| `/pnl` | 盈亏查询 |
| `/positions` | 持仓查询 |
| `/activity` | 活动记录 |
| `/swaps` | 交易记录 |
| `/strategies` | 策略列表 |
| `/vault` | Vault 信息 |

## AI 辅助开发

当使用 AI 工具进行开发时，请提供以下上下文：

1. **入口点**: `main.py` 是主入口
2. **API 客户端**: `api.py` 封装了 Terminal Markets API
3. **配置**: `config.py` 管理环境变量
4. **主要功能**: Telegram Bot 监控 Vault 状态

## 相关链接

- [Terminal Markets](https://terminal.markets/)
- [Terminal Markets API Docs](https://docs.terminal.markets)
- [python-telegram-bot 文档](https://docs.python-telegram-bot.org/)

---

*文档生成时间: 2026-02-28*
*BMAD Workflow: document-project v1.2.0*
