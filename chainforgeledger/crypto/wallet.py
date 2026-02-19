"""
ChainForgeLedger Wallet Module

Wallet implementation for managing keys and transactions.
"""

from typing import List
from chainforgeledger.crypto.keys import generate_keys, KeyPair
from chainforgeledger.crypto.signature import sign, verify, Signature


class Wallet:
    """
    Wallet for managing keys and transactions.
    
    Attributes:
        key_pair: Key pair
        address: Wallet address (hash of public key)
    """
    
    def __init__(self):
        """Initialize a new Wallet instance."""
        self.key_pair, self.address = generate_keys()
        self.balance = 0.0
        self.transaction_history = []
    
    @staticmethod
    def from_key_pair(key_pair: KeyPair) -> "Wallet":
        """
        Create wallet from key pair.
        
        Args:
            key_pair: Key pair
            
        Returns:
            Wallet instance
        """
        wallet = Wallet.__new__(Wallet)
        wallet.key_pair = key_pair
        wallet.address = ""
        wallet.balance = 0.0
        wallet.transaction_history = []
        
        return wallet
    
    def sign_transaction(self, transaction_data: str) -> Signature:
        """
        Sign transaction data.
        
        Args:
            transaction_data: Data to sign
            
        Returns:
            Signature instance
        """
        signature_value = sign(transaction_data, self.key_pair.private_key)
        return Signature(signature_value, self.key_pair.public_key)
    
    def verify_transaction(self, transaction_data: str, signature: Signature) -> bool:
        """
        Verify transaction signature.
        
        Args:
            transaction_data: Data to verify
            signature: Signature to verify
            
        Returns:
            True if signature is valid
        """
        return verify(signature, transaction_data, self.key_pair.private_key)
    
    def add_transaction(self, transaction: dict):
        """
        Add transaction to history.
        
        Args:
            transaction: Transaction to add
        """
        self.transaction_history.append(transaction)
    
    def update_balance(self, amount: float):
        """
        Update wallet balance.
        
        Args:
            amount: Amount to add (can be negative)
        """
        self.balance = max(0.0, self.balance + amount)
    
    def get_transaction_count(self) -> int:
        """
        Get number of transactions.
        
        Returns:
            Transaction count
        """
        return len(self.transaction_history)
    
    def get_transaction_history(self) -> List[dict]:
        """
        Get transaction history.
        
        Returns:
            List of transactions
        """
        return self.transaction_history
    
    def to_dict(self) -> dict:
        """
        Convert wallet to dictionary.
        
        Returns:
            Dictionary representation of wallet
        """
        return {
            "address": self.address,
            "public_key": self.key_pair.public_key,
            "private_key": self.key_pair.private_key,
            "balance": self.balance,
            "transaction_count": self.get_transaction_count(),
            "transaction_history": self.get_transaction_history()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Wallet":
        """
        Create wallet from dictionary.
        
        Args:
            data: Wallet data
            
        Returns:
            Wallet instance
        """
        key_pair = KeyPair(data.get("public_key", ""), data.get("private_key", ""))
        wallet = cls.from_key_pair(key_pair)
        wallet.address = data.get("address", "")
        wallet.balance = data.get("balance", 0.0)
        wallet.transaction_history = data.get("transaction_history", [])
        
        return wallet
    
    def __repr__(self):
        """String representation of wallet."""
        return f"Wallet(address={self.address[:16]}..., balance={self.balance:.2f})"
    
    def __str__(self):
        """String representation for printing."""
        return (
            f"Wallet: {self.address}\n"
            f"Balance: {self.balance:.2f}\n"
            f"Transactions: {self.get_transaction_count()}"
        )
