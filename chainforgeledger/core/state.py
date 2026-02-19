"""
ChainForgeLedger State Management Module

Blockchain state management and account balances.
"""

from typing import Optional
from chainforgeledger.core.transaction import Transaction


class State:
    """
    Manages blockchain state and account balances.
    
    Attributes:
        balances: Dictionary of account balances
    """
    
    def __init__(self):
        """Initialize state with empty balances."""
        self.balances = {}
        self.contract_code = {}
        self.contract_storage = {}
    
    def update_balance(self, address: str, amount: float):
        """
        Update account balance.
        
        Args:
            address: Account address
            amount: Amount to add (can be negative)
        """
        if address not in self.balances:
            self.balances[address] = 0.0
        
        self.balances[address] += amount
        
        # Ensure balance doesn't go negative
        if self.balances[address] < 0:
            self.balances[address] = 0.0
    
    def get_balance(self, address: str) -> float:
        """
        Get account balance.
        
        Args:
            address: Account address
            
        Returns:
            Account balance
        """
        return self.balances.get(address, 0.0)
    
    def has_enough_balance(self, address: str, amount: float) -> bool:
        """
        Check if account has enough balance.
        
        Args:
            address: Account address
            amount: Amount to check
            
        Returns:
            True if balance is sufficient
        """
        balance = self.get_balance(address)
        return balance >= amount
    
    def apply_transaction(self, transaction: Transaction):
        """
        Apply transaction to state.
        
        Args:
            transaction: Transaction to apply
        """
        # Check if transaction is valid
        if not transaction.validate_transaction():
            return False
            
        # Check sender balance
        if not self.has_enough_balance(transaction.sender, transaction.amount + transaction.fee):
            return False
            
        # Update balances
        self.update_balance(transaction.sender, -(transaction.amount + transaction.fee))
        self.update_balance(transaction.receiver, transaction.amount)
        
        return True
    
    def revert_transaction(self, transaction: Transaction):
        """
        Revert transaction effects.
        
        Args:
            transaction: Transaction to revert
        """
        self.update_balance(transaction.sender, transaction.amount + transaction.fee)
        self.update_balance(transaction.receiver, -transaction.amount)
    
    def get_total_supply(self) -> float:
        """
        Calculate total supply.
        
        Returns:
            Total supply of tokens
        """
        return sum(self.balances.values())
    
    def get_account_count(self) -> int:
        """
        Get number of accounts.
        
        Returns:
            Number of accounts
        """
        return len(self.balances)
    
    def get_contract_code(self, contract_address: str) -> Optional[str]:
        """
        Get smart contract code.
        
        Args:
            contract_address: Contract address
            
        Returns:
            Contract code if exists
        """
        return self.contract_code.get(contract_address)
    
    def set_contract_code(self, contract_address: str, code: str):
        """
        Set smart contract code.
        
        Args:
            contract_address: Contract address
            code: Contract code
        """
        self.contract_code[contract_address] = code
    
    def get_contract_storage(self, contract_address: str, key: str) -> str:
        """
        Get contract storage value.
        
        Args:
            contract_address: Contract address
            key: Storage key
            
        Returns:
            Storage value
        """
        return self.contract_storage.get(contract_address, {}).get(key, "")
    
    def set_contract_storage(self, contract_address: str, key: str, value: str):
        """
        Set contract storage value.
        
        Args:
            contract_address: Contract address
            key: Storage key
            value: Storage value
        """
        if contract_address not in self.contract_storage:
            self.contract_storage[contract_address] = {}
        
        self.contract_storage[contract_address][key] = value
    
    def to_dict(self) -> dict:
        """
        Convert state to dictionary.
        
        Returns:
            Dictionary representation of state
        """
        return {
            "balances": dict(self.balances),
            "contract_code": dict(self.contract_code),
            "contract_storage": dict(self.contract_storage),
            "total_supply": self.get_total_supply(),
            "account_count": self.get_account_count()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "State":
        """
        Create state from dictionary.
        
        Args:
            data: State data
            
        Returns:
            State instance
        """
        state = cls()
        state.balances = data.get("balances", {})
        state.contract_code = data.get("contract_code", {})
        state.contract_storage = data.get("contract_storage", {})
        
        return state
    
    def __repr__(self):
        """String representation of state."""
        return (
            f"State(accounts={self.get_account_count()}, "
            f"supply={self.get_total_supply():,.2f})"
        )
    
    def __str__(self):
        """String representation for printing."""
        return (
            f"State Information\n"
            f"=================\n"
            f"Total Accounts: {self.get_account_count()}\n"
            f"Total Supply: {self.get_total_supply():,.2f}\n"
            f"Contracts: {len(self.contract_code)}\n"
            f"Storage Entries: {sum(len(storage) for storage in self.contract_storage.values())}"
        )
