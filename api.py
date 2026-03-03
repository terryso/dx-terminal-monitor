import time

import aiohttp

from config import API_BASE_URL, VAULT_ADDRESS

# Token symbol -> address 缓存
_token_cache: dict[str, str] = {}
_token_cache_time: float = 0
TOKEN_CACHE_TTL = 3600  # 1 hour


async def _build_token_cache(api: "TerminalAPI"):
    """构建 token symbol -> address 缓存。"""
    global _token_cache, _token_cache_time
    cache = {}
    page = 1
    while page <= 50:  # 最多50页
        data = await api._get("/tokens", {"page": page, "limit": 50})
        if isinstance(data, dict) and "error" in data:
            break
        items = data if isinstance(data, list) else data.get("items", [])
        if not items:
            break
        for token in items:
            symbol = token.get("symbol", "").upper()
            address = token.get("tokenAddress", "")
            if symbol and address:
                cache[symbol] = address
        page += 1
    _token_cache = cache
    _token_cache_time = time.time()


class TerminalAPI:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.vault = VAULT_ADDRESS

    async def _get(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}

    async def get_vault(self) -> dict:
        """获取 Vault 基本信息"""
        return await self._get("/vault", {"vaultAddress": self.vault})

    async def get_positions(self) -> dict:
        """获取持仓信息"""
        return await self._get(f"/positions/{self.vault}")

    async def get_pnl_history(self) -> list:
        """获取 PnL 历史"""
        return await self._get(f"/pnl-history/{self.vault}")

    async def get_activity(self, limit: int = 10) -> dict:
        """获取最近活动"""
        return await self._get(
            f"/activity/{self.vault}",
            {"limit": limit, "order": "desc"}
        )

    async def get_strategies(self) -> list:
        """获取活跃策略"""
        return await self._get(f"/strategies/{self.vault}", {"activeOnly": "true"})

    async def get_swaps(self, limit: int = 10) -> dict:
        """获取交易记录"""
        return await self._get(
            "/swaps",
            {"vaultAddress": self.vault, "limit": limit, "order": "desc"}
        )

    async def get_deposits_withdrawals(self, limit: int = 10) -> dict:
        """获取存取款记录"""
        return await self._get(
            f"/deposits-withdrawals/{self.vault}",
            {"limit": limit, "order": "desc"}
        )

    async def get_eth_price(self) -> dict:
        """Get ETH real-time price."""
        return await self._get("/eth-price")

    async def get_tokens(self, page: int = 1, limit: int = 10) -> dict:
        """Get tradeable tokens list."""
        return await self._get("/tokens", {"page": page, "limit": limit})

    async def get_token(self, address_or_symbol: str) -> dict:
        """Get token details by address or symbol.

        If the input looks like a contract address (starts with 0x), query directly.
        Otherwise, use cache to find matching symbol.
        """
        global _token_cache, _token_cache_time

        # If it looks like a contract address, query directly
        if address_or_symbol.startswith("0x"):
            return await self._get(f"/token/{address_or_symbol}")

        symbol = address_or_symbol.upper()

        # Check cache (refresh if expired or empty)
        now = time.time()
        if not _token_cache or (now - _token_cache_time) > TOKEN_CACHE_TTL:
            await _build_token_cache(self)

        # Lookup in cache
        token_address = _token_cache.get(symbol)
        if token_address:
            return await self._get(f"/token/{token_address}")

        return {"error": f"Token '{address_or_symbol}' not found"}

    async def get_launch_schedule(self) -> list:
        """Get upcoming token launch schedule."""
        return await self._get("/launch-schedule")

    async def get_leaderboard(self, limit: int = 10) -> list:
        """Get vault leaderboard sorted by total PnL."""
        return await self._get("/leaderboard", {"limit": limit, "sortBy": "total_pnl_usd"})
