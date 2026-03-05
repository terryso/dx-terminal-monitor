import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root directory (where this file is located)
_env_path = Path(__file__).parent / '.env'
load_dotenv(_env_path)

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
ALLOWED_USERS = [
    int(x) for x in os.getenv('ALLOWED_USERS', '').split(',')
    if x.strip().isdigit()
]
VAULT_ADDRESS = os.getenv('VAULT_ADDRESS', '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C')
API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.terminal.markets/api/v1')

# Web3 Configuration
RPC_URL = os.getenv('RPC_URL', '')
PRIVATE_KEY = os.getenv('PRIVATE_KEY', '')
CHAIN_ID = int(os.getenv('CHAIN_ID', '1'))
ADMIN_USERS = [
    int(x) for x in os.getenv('ADMIN_USERS', '').split(',')
    if x.strip().isdigit()
]

# Activity Monitor Configuration
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '30'))

# Notification Configuration
NOTIFY_USERS = [
    int(x) for x in os.getenv('NOTIFY_USERS', '').split(',')
    if x.strip().isdigit()
]

# Monitor Control Configuration
AUTO_START_MONITOR = os.getenv('AUTO_START_MONITOR', 'true').lower() == 'true'

# Daily Report Configuration
REPORT_TIME = os.getenv('REPORT_TIME', '08:00')
REPORT_ENABLED = os.getenv('REPORT_ENABLED', 'true').lower() == 'true'

# Threshold Alert Configuration
PNL_ALERT_THRESHOLD = float(os.getenv('PNL_ALERT_THRESHOLD', '5'))
POSITION_ALERT_THRESHOLD = float(os.getenv('POSITION_ALERT_THRESHOLD', '10'))
ALERT_CHECK_INTERVAL = int(os.getenv('ALERT_CHECK_INTERVAL', '60'))
ALERT_ENABLED = os.getenv('ALERT_ENABLED', 'true').lower() == 'true'

# LLM Configuration (for AI Strategy Advisor - Epic 8)
LLM_API_KEY = os.getenv('LLM_API_KEY', '')
LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
LLM_MODEL = os.getenv('LLM_MODEL', 'glm-4')
LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', '60'))

# Advisor Configuration
ADVISOR_ENABLED = os.getenv('ADVISOR_ENABLED', 'true').lower() == 'true'
ADVISOR_INTERVAL_HOURS = int(os.getenv('ADVISOR_INTERVAL_HOURS', '2'))
SUGGESTION_TTL_MINUTES = int(os.getenv('SUGGESTION_TTL_MINUTES', '30'))

# AI Advisor History (Story 8-6)
ADVISOR_HISTORY_ENABLED = os.getenv('ADVISOR_HISTORY_ENABLED', 'false').lower() == 'true'
ADVISOR_HISTORY_MAX = int(os.getenv('ADVISOR_HISTORY_MAX', '30'))
ADVISOR_SURGE_DOMAIN = os.getenv('ADVISOR_SURGE_DOMAIN', 'dx-advisor.surge.sh')
SURGE_TOKEN = os.getenv('SURGE_TOKEN', '')


def is_admin(user_id: int) -> bool:
    """检查用户是否为管理员（用于高风险操作）

    安全默认值: 未配置 ADMIN_USERS 时返回 False
    """
    if not ADMIN_USERS:
        logger.warning("ADMIN_USERS not configured - admin check denied for user %s", user_id)
        return False
    return user_id in ADMIN_USERS
