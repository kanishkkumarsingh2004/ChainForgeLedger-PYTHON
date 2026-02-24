"""
Gas System - Comprehensive gas and fee management

A sophisticated gas system for managing execution costs in smart contracts and
blockchain operations. Features include configurable gas limits, dynamic pricing,
and advanced fee structures.
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class GasMetrics:
    """Metrics for gas consumption"""
    total_gas: int = 0
    used_gas: int = 0
    remaining_gas: int = 0
    gas_price: float = 0.0
    cost: float = 0.0
    execution_time: float = 0.0


@dataclass
class GasConfig:
    """Configuration for gas system"""
    block_gas_limit: int = 10_000_000
    transaction_gas_limit: int = 8_000_000
    min_gas_price: float = 1e-9
    max_gas_price: float = 1e-6
    gas_price_adjustment_factor: float = 0.1
    base_gas_price: float = 1e-9


class GasSystem:
    """
    Gas and fee management system
    """
    
    def __init__(self, config: GasConfig = None):
        self.config = config or GasConfig()
        self.gas_prices: List[float] = []
        self.current_gas_price = self.config.base_gas_price
        self.last_price_update = time.time()
    
    def calculate_transaction_cost(self, gas_used: int, gas_price: float = None) -> float:
        """Calculate transaction cost based on gas used and price"""
        effective_price = gas_price or self.current_gas_price
        return gas_used * effective_price
    
    def validate_gas_limit(self, gas_limit: int) -> bool:
        """Validate gas limit is within acceptable range"""
        return (self.config.transaction_gas_limit // 2) <= gas_limit <= self.config.transaction_gas_limit
    
    def calculate_block_gas_usage(self, transactions: List[Any]) -> int:
        """Calculate total gas usage for a block"""
        return sum(tx.gas_used for tx in transactions if hasattr(tx, 'gas_used'))
    
    def calculate_gas_refund(self, gas_used: int, gas_limit: int) -> Tuple[int, float]:
        """Calculate gas refund for unused gas"""
        unused_gas = gas_limit - gas_used
        refund_amount = unused_gas * 0.5  # 50% refund for unused gas
        return refund_amount, self.calculate_transaction_cost(refund_amount)
    
    def update_gas_price(self, block_gas_usage: int):
        """Update gas price based on block usage"""
        block_utilization = block_gas_usage / self.config.block_gas_limit
        
        # Adjust gas price based on utilization
        if block_utilization > 0.8:
            # High usage - increase gas price
            price_increase = self.current_gas_price * self.config.gas_price_adjustment_factor
            self.current_gas_price = min(
                self.current_gas_price + price_increase,
                self.config.max_gas_price
            )
        elif block_utilization < 0.2:
            # Low usage - decrease gas price
            price_decrease = self.current_gas_price * self.config.gas_price_adjustment_factor
            self.current_gas_price = max(
                self.current_gas_price - price_decrease,
                self.config.min_gas_price
            )
        
        # Record price history
        self.gas_prices.append(self.current_gas_price)
        if len(self.gas_prices) > 100:
            self.gas_prices.pop(0)
        
        self.last_price_update = time.time()
    
    def get_average_gas_price(self, window_size: int = 20) -> float:
        """Get average gas price over time window"""
        if not self.gas_prices:
            return self.config.base_gas_price
        
        window = self.gas_prices[-window_size:]
        return sum(window) / len(window)
    
    def estimate_gas(self, transaction: Any) -> int:
        """Estimate gas requirements for transaction"""
        base_gas = 21000
        
        if hasattr(transaction, 'data') and transaction.data:
            # Additional gas for data
            data_length = len(transaction.data)
            base_gas += 68 * data_length
        
        if hasattr(transaction, 'to') and not transaction.to:
            # Contract creation has higher gas cost
            base_gas += 32000
        
        return base_gas
    
    def calculate_priority_fee(self, priority_gas_price: float, gas_used: int) -> float:
        """Calculate priority fee for transactions"""
        return priority_gas_price * gas_used
    
    def validate_gas_price(self, gas_price: float) -> bool:
        """Validate gas price is within acceptable range"""
        return self.config.min_gas_price <= gas_price <= self.config.max_gas_price
    
    def get_gas_metrics(self, transactions: List[Any]) -> GasMetrics:
        """Get comprehensive gas metrics for block"""
        total_gas = sum(tx.gas_limit for tx in transactions if hasattr(tx, 'gas_limit'))
        used_gas = sum(tx.gas_used for tx in transactions if hasattr(tx, 'gas_used'))
        remaining_gas = total_gas - used_gas
        
        return GasMetrics(
            total_gas=total_gas,
            used_gas=used_gas,
            remaining_gas=remaining_gas,
            gas_price=self.current_gas_price,
            cost=self.calculate_transaction_cost(used_gas),
            execution_time=0  # Would be calculated from block timestamp
        )
    
    def get_config(self) -> GasConfig:
        """Get gas configuration"""
        return self.config
    
    def update_config(self, config: GasConfig):
        """Update gas configuration"""
        self.config = config
        # Ensure current price is within new bounds
        self.current_gas_price = max(
            min(self.current_gas_price, self.config.max_gas_price),
            self.config.min_gas_price
        )
