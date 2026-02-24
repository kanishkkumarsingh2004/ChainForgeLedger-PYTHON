"""
Transaction receipt management

Comprehensive transaction receipt system that tracks:
- Transaction status
- Gas usage and fees
- Execution results
- Logs and events
- Contract creation information
- Block and timing details
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from chainforgeledger.crypto.hashing import sha256_hash


@dataclass
class LogEntry:
    """Represents a log entry from transaction execution"""
    type: str
    message: str
    timestamp: float = field(default_factory=lambda: time.time())
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransactionReceipt:
    """Transaction receipt for tracking execution results"""
    id: str = field(default_factory=lambda: sha256_hash(f"{time.time()}{hash(time.time())}")[:32])
    transaction_id: str = None
    block_hash: str = None
    block_number: int = None
    timestamp: float = field(default_factory=lambda: time.time())
    status: str = "pending"  # pending, successful, failed
    gas_used: int = 0
    gas_price: float = 0.0
    fee: float = 0.0
    logs: List[LogEntry] = field(default_factory=list)
    contract_address: str = None
    root: str = None
    cumulative_gas_used: int = 0
    effective_gas_price: float = 0.0
    
    def set_transaction_id(self, transaction_id: str):
        """Set transaction ID"""
        self.transaction_id = transaction_id
    
    def set_block_hash(self, block_hash: str):
        """Set block hash"""
        self.block_hash = block_hash
    
    def set_block_number(self, block_number: int):
        """Set block number"""
        self.block_number = block_number
    
    def set_status(self, status: str):
        """Set transaction status"""
        if status not in ["pending", "successful", "failed"]:
            raise ValueError("Invalid status")
        self.status = status
    
    def set_gas_used(self, gas_used: int):
        """Set gas used"""
        if gas_used < 0:
            raise ValueError("Gas used cannot be negative")
        self.gas_used = gas_used
    
    def set_gas_price(self, gas_price: float):
        """Set gas price"""
        if gas_price < 0:
            raise ValueError("Gas price cannot be negative")
        self.gas_price = gas_price
    
    def set_fee(self, fee: float):
        """Set transaction fee"""
        if fee < 0:
            raise ValueError("Fee cannot be negative")
        self.fee = fee
    
    def add_log(self, log_data: Dict):
        """Add log entry"""
        log = LogEntry(
            type=log_data.get('type', 'info'),
            message=log_data.get('message', ''),
            timestamp=log_data.get('timestamp', time.time()),
            data=log_data.get('data', {})
        )
        self.logs.append(log)
    
    def set_contract_address(self, contract_address: str):
        """Set contract address (for contract creation)"""
        self.contract_address = contract_address
    
    def set_root(self, root: str):
        """Set state root after execution"""
        self.root = root
    
    def set_cumulative_gas_used(self, cumulative_gas_used: int):
        """Set cumulative gas used in block"""
        if cumulative_gas_used < 0:
            raise ValueError("Cumulative gas used cannot be negative")
        self.cumulative_gas_used = cumulative_gas_used
    
    def set_effective_gas_price(self, effective_gas_price: float):
        """Set effective gas price"""
        if effective_gas_price < 0:
            raise ValueError("Effective gas price cannot be negative")
        self.effective_gas_price = effective_gas_price
    
    def to_dict(self) -> Dict:
        """Convert receipt to dictionary"""
        return {
            'id': self.id,
            'transactionId': self.transaction_id,
            'blockHash': self.block_hash,
            'blockNumber': self.block_number,
            'timestamp': self.timestamp,
            'status': self.status,
            'gasUsed': self.gas_used,
            'gasPrice': self.gas_price,
            'fee': self.fee,
            'logs': [
                {
                    'type': log.type,
                    'message': log.message,
                    'timestamp': log.timestamp,
                    'data': log.data
                } for log in self.logs
            ],
            'contractAddress': self.contract_address,
            'root': self.root,
            'cumulativeGasUsed': self.cumulative_gas_used,
            'effectiveGasPrice': self.effective_gas_price
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TransactionReceipt':
        """Create receipt from dictionary"""
        receipt = cls()
        receipt.id = data.get('id', receipt.id)
        receipt.transaction_id = data.get('transactionId')
        receipt.block_hash = data.get('blockHash')
        receipt.block_number = data.get('blockNumber')
        receipt.timestamp = data.get('timestamp', receipt.timestamp)
        receipt.status = data.get('status', receipt.status)
        receipt.gas_used = data.get('gasUsed', receipt.gas_used)
        receipt.gas_price = data.get('gasPrice', receipt.gas_price)
        receipt.fee = data.get('fee', receipt.fee)
        
        logs = data.get('logs', [])
        for log_data in logs:
            log = LogEntry(
                type=log_data.get('type', 'info'),
                message=log_data.get('message', ''),
                timestamp=log_data.get('timestamp', time.time()),
                data=log_data.get('data', {})
            )
            receipt.logs.append(log)
        
        receipt.contract_address = data.get('contractAddress')
        receipt.root = data.get('root')
        receipt.cumulative_gas_used = data.get('cumulativeGasUsed', receipt.cumulative_gas_used)
        receipt.effective_gas_price = data.get('effectiveGasPrice', receipt.effective_gas_price)
        
        return receipt


def create_transaction_receipt(options: Dict = None) -> TransactionReceipt:
    """Create a new transaction receipt with options"""
    options = options or {}
    return TransactionReceipt(
        transaction_id=options.get('transactionId'),
        block_hash=options.get('blockHash'),
        block_number=options.get('blockNumber'),
        status=options.get('status', 'pending'),
        gas_used=options.get('gasUsed', 0),
        gas_price=options.get('gasPrice', 0.0),
        fee=options.get('fee', 0.0),
        contract_address=options.get('contractAddress')
    )
