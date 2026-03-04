#!/bin/bash
# Terminal Monitor 后台启动脚本

# Proxy settings
export http_proxy="http://127.0.0.1:7890"
export https_proxy="http://127.0.0.1:7890"
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
export no_proxy="localhost,127.0.0.1"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/bot.pid"
LOG_FILE="$SCRIPT_DIR/bot.log"
PROCESS_NAME="main.py"

# 杀掉现有进程
kill_existing() {
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            echo "Stopping existing process (PID: $OLD_PID)..."
            kill "$OLD_PID"
            sleep 3
            # 强制杀掉如果还在运行
            if kill -0 "$OLD_PID" 2>/dev/null; then
                kill -9 "$OLD_PID"
                sleep 1
            fi
        fi
        rm -f "$PID_FILE"
    fi

    # 查找并杀掉其他同名进程
    OTHER_PIDS=$(pgrep -f "python.*$PROCESS_NAME" 2>/dev/null | grep -v $$)
    if [ -n "$OTHER_PIDS" ]; then
        echo "Killing other instances..."
        echo "$OTHER_PIDS" | xargs kill 2>/dev/null
        sleep 1
    fi
}

# 启动新进程
start() {
    echo "Starting bot..."
    cd "$SCRIPT_DIR"

    # 激活虚拟环境（如果存在）
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # 后台启动，输出到日志文件
    nohup python main.py >> "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    echo $NEW_PID > "$PID_FILE"
    echo "Bot started (PID: $NEW_PID)"
    echo "Log file: $LOG_FILE"
}

# 主逻辑
case "${1:-start}" in
    start)
        kill_existing
        start
        ;;
    stop)
        kill_existing
        echo "Bot stopped"
        ;;
    restart)
        kill_existing
        start
        ;;
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "Bot running (PID: $PID)"
            else
                echo "Bot not running (stale PID file)"
            fi
        else
            echo "Bot not running"
        fi
        ;;
    logs)
        tail -f "$LOG_FILE"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
