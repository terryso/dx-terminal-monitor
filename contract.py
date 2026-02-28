"""
Web3 contract interaction module for AgentVault smart contract.

This module provides the VaultContract class for interacting with
the AgentVault smart contract on Ethereum-compatible networks.
"""

import json
import logging
from pathlib import Path
from typing import Callable, Dict, Any

from web3 import Web3
from web3.contract import Contract

from config import RPC_URL, PRIVATE_KEY, CHAIN_ID, VAULT_ADDRESS

logger = logging.getLogger(__name__)


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
            FileNotFoundError: If ABI file does not exist.
            json.JSONDecodeError: If ABI file is not valid JSON.
        """
        abi_path = Path(__file__).parent / "abi" / "AgentVault.json"

        if not abi_path.exists():
            raise FileNotFoundError(f"ABI file not found: {abi_path}")

        with open(abi_path, "r") as f:
            abi = json.load(f)

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
                - error: str - on failure
        """
        try:
            # Estimate gas
            gas_estimate = tx_func.estimate_gas({'from': self.account.address})

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
                    'error': "Transaction execution failed (status: 0)",
                }

            return {
                'success': True,
                'transactionHash': tx_hash.hex(),
                'status': receipt['status'],
                'blockNumber': receipt['blockNumber'],
            }

        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            return {
                'success': False,
                'error': str(e),
            }
