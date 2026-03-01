"""
Web3 contract interaction module for AgentVault smart contract.

This module provides the VaultContract class for interacting with
the AgentVault smart contract on Ethereum-compatible networks.
"""

import json
import logging
from pathlib import Path
from typing import Callable, Dict, Any, Optional

from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError

from config import RPC_URL, PRIVATE_KEY, CHAIN_ID, VAULT_ADDRESS

logger = logging.getLogger(__name__)

# User-friendly error messages
ERROR_MESSAGES = {
    'abi_not_found': "合约配置文件缺失，请联系管理员",
    'abi_invalid': "合约配置文件格式错误，请联系管理员",
    'gas_estimation_failed': "Gas 估算失败，可能是合约条件不满足",
    'contract_reverted': "合约执行失败，请检查策略状态",
    'network_error': "网络连接失败，请稍后重试",
    'unknown': "未知错误，请稍后重试",
}


class VaultContract:
    """Interface for interacting with AgentVault smart contract."""

    def __init__(self):
        """
        Initialize Web3 connection and contract instance.

        Raises:
            ValueError: If required configuration is missing.
        """
        if not RPC_URL:
            raise ValueError("RPC_URL is not configured")
        if not PRIVATE_KEY:
            raise ValueError("PRIVATE_KEY is not configured")
        if not VAULT_ADDRESS:
            raise ValueError("VAULT_ADDRESS is not configured")

        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))

        # Load account from private key
        self.account = self.w3.eth.account.from_key(PRIVATE_KEY)

        # Store vault address as checksum address
        self.address = Web3.to_checksum_address(VAULT_ADDRESS)

        # Load contract
        self.contract: Contract = self._load_contract()

    def _load_contract(self) -> Contract:
        """
        Load contract instance from ABI file.

        Returns:
            Contract: Web3 contract instance.

        Raises:
            RuntimeError: If ABI file does not exist or is invalid (with user-friendly message).
        """
        abi_path = Path(__file__).parent / "abi" / "AgentVault.json"

        if not abi_path.exists():
            logger.error(f"ABI file not found: {abi_path}")
            raise RuntimeError(ERROR_MESSAGES['abi_not_found'])

        try:
            with open(abi_path, "r") as f:
                abi = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid ABI JSON: {e}")
            raise RuntimeError(ERROR_MESSAGES['abi_invalid'])

        return self.w3.eth.contract(
            address=self.address,
            abi=abi
        )

    async def _send_transaction(self, tx_func: Callable) -> Dict[str, Any]:
        """
        Sign, send, and wait for transaction confirmation.

        This is an async private method that handles the full transaction lifecycle:
        1. Build transaction with gas estimation
        2. Sign with account's private key
        3. Send to network
        4. Wait for confirmation

        Args:
            tx_func: Callable that returns transaction builder (e.g., contract.functions.method())

        Returns:
            Dict with keys:
                - success: bool
                - transactionHash: str (hex) - on success
                - status: int - on success
                - blockNumber: int - on success
                - error: str - on failure (user-friendly message)
        """
        try:
            # Estimate gas
            try:
                gas_estimate = tx_func.estimate_gas({'from': self.account.address})
            except ContractLogicError as e:
                logger.error(f"Contract logic error during gas estimation: {e}")
                return {
                    'success': False,
                    'error': ERROR_MESSAGES['gas_estimation_failed'],
                }

            # Build transaction
            tx = tx_func.build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': int(gas_estimate * 1.2),  # Add 20% buffer
                'gasPrice': self.w3.eth.gas_price,
                'chainId': CHAIN_ID,
            })

            # Sign transaction
            signed_tx = self.account.sign_transaction(tx)

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # Check status
            if receipt['status'] == 0:
                logger.error("Transaction execution failed (status: 0)")
                return {
                    'success': False,
                    'error': ERROR_MESSAGES['contract_reverted'],
                }

            return {
                'success': True,
                'transactionHash': tx_hash.hex(),
                'status': receipt['status'],
                'blockNumber': receipt['blockNumber'],
                'receipt': dict(receipt),
            }

        except ConnectionError as e:
            logger.error(f"Network connection error: {e}")
            return {
                'success': False,
                'error': ERROR_MESSAGES['network_error'],
            }
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            return {
                'success': False,
                'error': f"{ERROR_MESSAGES['unknown']} ({str(e)})",
            }

    async def disable_strategy(self, strategy_id: int) -> Dict[str, Any]:
        """
        Disable a specific strategy by ID.

        Args:
            strategy_id: The ID of the strategy to disable.

        Returns:
            Dict with keys:
                - success: bool
                - transactionHash: str (hex) - on success
                - status: int - on success
                - blockNumber: int - on success
                - error: str - on failure
        """
        try:
            # Get contract function
            tx_func = self.contract.functions.disableStrategy(strategy_id)

            # Send transaction
            result = await self._send_transaction(tx_func)

            return result

        except Exception as e:
            logger.error(f"Failed to disable strategy #{strategy_id}: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    async def disable_all_strategies(self, get_active_count: Optional[Callable[[], int]] = None) -> Dict[str, Any]:
        """
        Disable all active strategies.

        Calls the contract's disableAllActiveStrategies() function.
        The disabledCount is obtained via the provided get_active_count callback
        (typically from the REST API) before disabling, since Solidity non-view
        functions cannot return values directly through send_transaction.

        Args:
            get_active_count: Optional async callback to fetch active strategy count.
                             If not provided, disabledCount will be -1 (unknown).

        Returns:
            Dict with keys:
                - success: bool
                - transactionHash: str (hex) - on success
                - disabledCount: int - number of strategies disabled (from API before call),
                                      -1 if count unavailable
                - status: int - on success
                - blockNumber: int - on success
                - error: str - on failure
        """
        try:
            # Get active count before disabling (for user feedback)
            disabled_count = -1
            if get_active_count is not None:
                try:
                    disabled_count = await get_active_count()
                except Exception as e:
                    logger.warning(f"Failed to get active count: {e}")
                    disabled_count = -1

            # Pre-validation: check if there are strategies to disable
            if disabled_count == 0:
                return {
                    'success': True,
                    'disabledCount': 0,
                    'message': 'no_active_strategies',
                }

            # Get contract function
            tx_func = self.contract.functions.disableAllActiveStrategies()

            # Send transaction
            result = await self._send_transaction(tx_func)

            if result.get("success"):
                result["disabledCount"] = disabled_count

            return result

        except Exception as e:
            logger.error(f"Failed to disable all strategies: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    async def add_strategy(
        self,
        content: str,
        expiry: int = 0,
        priority: int = 1
    ) -> Dict[str, Any]:
        """
        Add a new trading strategy.

        Args:
            content: Strategy text content
            expiry: Expiration timestamp (0 = never expires)
            priority: Priority level (0=LOW, 1=MEDIUM, 2=HIGH)

        Returns:
            Dict with keys:
                - success: bool
                - transactionHash: str (hex) - on success
                - strategyId: int - on success (parsed from event logs)
                - status: int - on success
                - blockNumber: int - on success
                - error: str - on failure
        """
        try:
            tx_func = self.contract.functions.addStrategy(content, expiry, priority)
            result = await self._send_transaction(tx_func)

            # If successful, try to parse strategyId from logs
            if result.get("success"):
                result["strategyId"] = self._parse_strategy_id_from_logs(
                    result.get("receipt", {})
                )

            return result
        except Exception as e:
            logger.error(f"Failed to add strategy: {e}")
            return {"success": False, "error": str(e)}

    def _parse_strategy_id_from_logs(self, receipt: Dict) -> Optional[int]:
        """Parse the newly added strategy ID from transaction receipt logs.

        Args:
            receipt: Transaction receipt dictionary

        Returns:
            Strategy ID if found, None otherwise
        """
        try:
            # StrategyAdded event signature
            event_signature = self.w3.keccak(text="StrategyAdded(uint256,string)").hex()

            # Search through logs for the event
            for log in receipt.get("logs", []):
                if len(log.get("topics", [])) > 0 and log["topics"][0].hex() == event_signature:
                    # Parse strategyId from the first topic (indexed parameter)
                    strategy_id = int(log["topics"][1].hex(), 16)
                    return strategy_id

            logger.warning("StrategyAdded event not found in transaction logs")
            return None
        except Exception as e:
            logger.warning(f"Failed to parse strategy ID from logs: {e}")
            return None

    async def pause_vault(self, paused: bool = True) -> Dict[str, Any]:
        """
        Pause or resume Agent trading.

        Args:
            paused: True to pause, False to resume

        Returns:
            Dict with keys:
                - success: bool
                - transactionHash: str (hex) - on success
                - status: int - on success
                - blockNumber: int - on success
                - error: str - on failure
        """
        try:
            tx_func = self.contract.functions.pauseVault(paused)
            return await self._send_transaction(tx_func)
        except Exception as e:
            logger.error(f"Failed to {'pause' if paused else 'resume'} vault: {e}")
            return {"success": False, "error": str(e)}

    async def update_settings(
        self,
        max_trade_bps: int,
        slippage_bps: int
    ) -> Dict[str, Any]:
        """
        Update vault trading settings.

        Args:
            max_trade_bps: Maximum trade amount in BPS (500-10000)
            slippage_bps: Slippage tolerance in BPS (10-5000)

        Returns:
            Dict with keys:
                - success: bool
                - transactionHash: str (hex) - on success
                - status: int - on success
                - blockNumber: int - on success
                - error: str - on failure
        """
        try:
            # Validate parameters
            if not (500 <= max_trade_bps <= 10000):
                return {
                    'success': False,
                    'error': 'max_trade 必须在 500-10000 BPS 之间 (5%-100%)'
                }
            if not (10 <= slippage_bps <= 5000):
                return {
                    'success': False,
                    'error': 'slippage 必须在 10-5000 BPS 之间 (0.1%-50%)'
                }

            tx_func = self.contract.functions.updateSettings(max_trade_bps, slippage_bps)
            return await self._send_transaction(tx_func)

        except Exception as e:
            logger.error(f"Failed to update settings: {e}")
            return {"success": False, "error": str(e)}

    async def withdraw_eth(self, amount_wei: int) -> Dict[str, Any]:
        """
        Withdraw ETH from the vault to the owner address.

        Args:
            amount_wei: Amount to withdraw in Wei

        Returns:
            Dict with keys:
                - success: bool
                - transactionHash: str (hex) - on success
                - status: int - on success
                - blockNumber: int - on success
                - error: str - on failure
        """
        try:
            # Validate amount
            if amount_wei <= 0:
                return {
                    'success': False,
                    'error': '提取金额必须大于 0'
                }

            tx_func = self.contract.functions.withdrawETH(amount_wei)
            return await self._send_transaction(tx_func)

        except Exception as e:
            logger.error(f"Failed to withdraw ETH: {e}")
            return {"success": False, "error": str(e)}
