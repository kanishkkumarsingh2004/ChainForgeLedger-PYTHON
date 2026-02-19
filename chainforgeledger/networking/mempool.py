"""
ChainForgeLedger Mempool Module

Transaction mempool management implementation.
"""

import time
from typing import List, Optional
from chainforgeledger.utils.logger import get_logger
from chainforgeledger.core.transaction import Transaction


class MemPool:
    """
    Manages pending transactions in the mempool.
    
    Attributes:
        transactions: List of pending transactions
        max_size: Maximum number of transactions to keep
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize a new MemPool instance.
        
        Args:
            max_size: Maximum number of transactions to keep
        """
        self.transactions = []
        self._transaction_map = {}  # For O(1) transaction lookups by ID
        self.max_size = max_size
        self.logger = get_logger(__name__)
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Add a transaction to the mempool.
        
        Args:
            transaction: Transaction to add
            
        Returns:
            True if transaction was added successfully, False otherwise
        """
        if not isinstance(transaction, Transaction):
            raise ValueError("Invalid transaction type")
        
        # Check if transaction already exists
        if transaction.transaction_id in self._transaction_map:
            self.logger.debug(f"Transaction already exists in mempool: {transaction.transaction_id}")
            return False
        
        # Check mempool size
        if len(self.transactions) >= self.max_size:
            self.logger.warning("Mempool is full")
            return False
        
        # Validate transaction before adding
        if not self._validate_transaction(transaction):
            self.logger.warning(f"Invalid transaction: {transaction.transaction_id}")
            return False
        
        self.transactions.append(transaction)
        self._transaction_map[transaction.transaction_id] = transaction
        self.logger.debug(f"Transaction added to mempool: {transaction.transaction_id}")
        return True
    
    def remove_transaction(self, transaction: Transaction) -> bool:
        """
        Remove a transaction from the mempool.
        
        Args:
            transaction: Transaction to remove
            
        Returns:
            True if transaction was removed successfully, False otherwise
        """
        if not isinstance(transaction, Transaction):
            raise ValueError("Invalid transaction type")
        
        transaction_id = transaction.transaction_id
        
        if transaction_id in self._transaction_map:
            del self._transaction_map[transaction_id]
            self.transactions = [tx for tx in self.transactions if tx.transaction_id != transaction_id]
            self.logger.debug(f"Transaction removed from mempool: {transaction_id}")
            return True
        
        self.logger.debug(f"Transaction not found in mempool: {transaction_id}")
        return False
    
    def contains_transaction(self, transaction: Transaction) -> bool:
        """
        Check if transaction exists in mempool.
        
        Args:
            transaction: Transaction to check
            
        Returns:
            True if transaction exists in mempool, False otherwise
        """
        return transaction.transaction_id in self._transaction_map
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """
        Get transaction by ID from mempool.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction if found, None otherwise
        """
        return self._transaction_map.get(transaction_id)
    
    def get_transactions(self, count: int = None) -> List[Transaction]:
        """
        Get transactions from mempool.
        
        Args:
            count: Number of transactions to return (None for all)
            
        Returns:
            List of transactions
        """
        if count is None:
            return self.transactions.copy()
        
        return self.transactions[:count]
    
    def get_transactions_by_sender(self, sender_address: str) -> List[Transaction]:
        """
        Get transactions from a specific sender.
        
        Args:
            sender_address: Sender address
            
        Returns:
            List of transactions from the specified sender
        """
        return [tx for tx in self.transactions if tx.sender == sender_address]
    
    def get_transactions_by_recipient(self, recipient_address: str) -> List[Transaction]:
        """
        Get transactions to a specific recipient.
        
        Args:
            recipient_address: Recipient address
            
        Returns:
            List of transactions to the specified recipient
        """
        return [tx for tx in self.transactions if tx.recipient == recipient_address]
    
    def get_transactions_by_amount_range(self, min_amount: float, max_amount: float) -> List[Transaction]:
        """
        Get transactions with amounts in a specific range.
        
        Args:
            min_amount: Minimum amount
            max_amount: Maximum amount
            
        Returns:
            List of transactions with amounts in the specified range
        """
        return [tx for tx in self.transactions if min_amount <= tx.amount <= max_amount]
    
    def get_transactions_by_time_range(self, start_time: float, end_time: float) -> List[Transaction]:
        """
        Get transactions created within a specific time range.
        
        Args:
            start_time: Start time (timestamp)
            end_time: End time (timestamp)
            
        Returns:
            List of transactions created within the specified time range
        """
        return [tx for tx in self.transactions if start_time <= tx.timestamp <= end_time]
    
    def get_transactions_sorted_by_fee(self, ascending: bool = False) -> List[Transaction]:
        """
        Get transactions sorted by fee.
        
        Args:
            ascending: Sort in ascending order (default: descending)
            
        Returns:
            Sorted list of transactions
        """
        return sorted(
            self.transactions,
            key=lambda tx: tx.fee,
            reverse=not ascending
        )
    
    def get_transactions_sorted_by_timestamp(self, ascending: bool = True) -> List[Transaction]:
        """
        Get transactions sorted by timestamp.
        
        Args:
            ascending: Sort in ascending order (default: True)
            
        Returns:
            Sorted list of transactions
        """
        return sorted(
            self.transactions,
            key=lambda tx: tx.timestamp,
            reverse=not ascending
        )
    
    def get_transactions_sorted_by_amount(self, ascending: bool = False) -> List[Transaction]:
        """
        Get transactions sorted by amount.
        
        Args:
            ascending: Sort in ascending order (default: descending)
            
        Returns:
            Sorted list of transactions
        """
        return sorted(
            self.transactions,
            key=lambda tx: tx.amount,
            reverse=not ascending
        )
    
    def select_transactions_for_block(self, block_size_limit: int = None, block_transaction_limit: int = None) -> List[Transaction]:
        """
        Select transactions to include in a new block.
        
        Args:
            block_size_limit: Maximum block size (in transactions)
            block_transaction_limit: Maximum number of transactions
            
        Returns:
            List of transactions to include in block
        """
        # Sort transactions by fee descending to prioritize high fee transactions
        sorted_transactions = self.get_transactions_sorted_by_fee(ascending=False)
        
        selected = []
        total_size = 0
        
        for tx in sorted_transactions:
            if block_size_limit and total_size >= block_size_limit:
                break
                
            if block_transaction_limit and len(selected) >= block_transaction_limit:
                break
                
            # Check if transaction is still valid
            if self._validate_transaction(tx):
                selected.append(tx)
                total_size += 1
        
        return selected
    
    def clear(self):
        """Clear all transactions from mempool."""
        self.transactions.clear()
        self.logger.debug("Mempool cleared")
    
    def _validate_transaction(self, transaction: Transaction) -> bool:
        """
        Validate a transaction before adding to mempool.

        Args:
            transaction: Transaction to validate
            
        Returns:
            True if transaction is valid, False otherwise
        """
        # Check basic transaction structure
        if not transaction.validate_transaction():
            self.logger.debug(f"Transaction invalid: {transaction.transaction_id}")
            return False
        
        # Check transaction fee
        if transaction.fee < 0:
            self.logger.debug(f"Negative fee transaction: {transaction.transaction_id}")
            return False
        
        # Check transaction age
        age = time.time() - transaction.timestamp
        if age > 3600:  # 1 hour
            self.logger.debug(f"Stale transaction: {transaction.transaction_id}")
            return False
        
        return True
    
    def get_mempool_info(self) -> dict:
        """
        Get mempool information.
        
        Returns:
            Mempool information dictionary
        """
        fee_sorted = self.get_transactions_sorted_by_fee()
        fee_ranges = self._calculate_fee_ranges()
        
        return {
            "size": len(self.transactions),
            "max_size": self.max_size,
            "utilization": len(self.transactions) / self.max_size,
            "transaction_count": len(self.transactions),
            "average_fee": sum(tx.fee for tx in self.transactions) / len(self.transactions) if self.transactions else 0,
            "min_fee": min(tx.fee for tx in self.transactions) if self.transactions else 0,
            "max_fee": max(tx.fee for tx in self.transactions) if self.transactions else 0,
            "fee_ranges": fee_ranges,
            "top_fees": fee_sorted[:10],
            "total_amount": sum(tx.amount for tx in self.transactions) if self.transactions else 0,
            "time_range": self._get_time_range()
        }
    
    def _calculate_fee_ranges(self) -> dict:
        """
        Calculate fee distribution ranges.
        
        Returns:
            Fee ranges dictionary
        """
        ranges = {
            "very_low": 0,
            "low": 0,
            "medium": 0,
            "high": 0,
            "very_high": 0
        }
        
        for tx in self.transactions:
            fee = tx.fee
            
            if fee < 0.001:
                ranges["very_low"] += 1
            elif fee < 0.01:
                ranges["low"] += 1
            elif fee < 0.1:
                ranges["medium"] += 1
            elif fee < 1.0:
                ranges["high"] += 1
            else:
                ranges["very_high"] += 1
        
        return ranges
    
    def _get_time_range(self) -> dict:
        """
        Get time range of transactions.
        
        Returns:
            Time range dictionary
        """
        if not self.transactions:
            return {
                "earliest": None,
                "latest": None,
                "range": 0
            }
        
        timestamps = [tx.timestamp for tx in self.transactions]
        earliest = min(timestamps)
        latest = max(timestamps)
        
        return {
            "earliest": earliest,
            "latest": latest,
            "range": latest - earliest
        }
    
    def to_dict(self) -> dict:
        """
        Convert mempool to dictionary.
        
        Returns:
            Dictionary representation of mempool
        """
        return {
            "transactions": [tx.to_dict() for tx in self.transactions],
            "max_size": self.max_size
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MemPool":
        """
        Create mempool from dictionary.
        
        Args:
            data: Mempool data
            
        Returns:
            MemPool instance
        """
        mempool = cls(data.get("max_size", 1000))
        
        for tx_data in data.get("transactions", []):
            tx = Transaction.from_dict(tx_data)
            mempool.add_transaction(tx)
            
        return mempool
    
    def __len__(self) -> int:
        """Get number of transactions in mempool."""
        return len(self.transactions)
    
    def __repr__(self):
        """String representation of mempool."""
        return f"MemPool(size={len(self)}, max_size={self.max_size})"
    
    def __str__(self):
        """String representation for printing."""
        info = self.get_mempool_info()
        return (
            f"Mempool\n"
            f"=======\n"
            f"Size: {info['size']}/{info['max_size']}\n"
            f"Utilization: {info['utilization']:.2%}\n"
            f"Transactions: {info['transaction_count']}\n"
            f"Average Fee: {info['average_fee']:.6f}\n"
            f"Min Fee: {info['min_fee']:.6f}\n"
            f"Max Fee: {info['max_fee']:.6f}\n"
            f"Total Amount: {info['total_amount']:.6f}"
        )
