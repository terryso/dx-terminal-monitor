import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
ALLOWED_USERS = [
    int(x) for x in os.getenv('ALLOWED_USERS', '').split(',')
    if x.strip().isdigit()
]
VAULT_ADDRESS = os.getenv('VAULT_ADDRESS', '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C')
API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.terminal.markets/api/v1')
