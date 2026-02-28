import aiohttp
from config import API_BASE_URL, VAULT_ADDRESS


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
