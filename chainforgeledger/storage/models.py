"""
ChainForgeLedger Data Models

Data models for blockchain entities.
"""

import json
import time
from typing import Dict
from chainforgeledger.utils.logger import get_logger


class BlockStorage:
    """
    Block storage model.
    
    Represents a blockchain block for storage purposes.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize block storage.
        
        Args:
            **kwargs: Block attributes
        """
        self.block_index = kwargs.get('block_index', 0)
        self.previous_hash = kwargs.get('previous_hash', '')
        self.block_hash = kwargs.get('block_hash', '')
        self.merkle_root = kwargs.get('merkle_root', '')
        self.timestamp = kwargs.get('timestamp', self._get_current_timestamp())
        self.difficulty = kwargs.get('difficulty', 1)
        self.nonce = kwargs.get('nonce', 0)
        self.transactions = kwargs.get('transactions', [])
        self.miner_address = kwargs.get('miner_address', '')
        self.hash = kwargs.get('block_hash', '')
        self.logger = get_logger(__name__)
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp."""
        return time.time()
    
    def validate(self) -> bool:
        """
        Validate block structure.
        
        Returns:
            True if block is valid, False otherwise
        """
        if not isinstance(self.block_index, int) or self.block_index < 0:
            return False
        
        if not isinstance(self.previous_hash, str) or len(self.previous_hash) != 64:
            return False
        
        if not isinstance(self.block_hash, str) or len(self.block_hash) != 64:
            return False
        
        if not isinstance(self.merkle_root, str) or len(self.merkle_root) != 64:
            return False
        
        if not isinstance(self.timestamp, (int, float)) or self.timestamp <= 0:
            return False
        
        if not isinstance(self.difficulty, (int, float)) or self.difficulty <= 0:
            return False
        
        if not isinstance(self.nonce, int) or self.nonce < 0:
            return False
        
        if not isinstance(self.transactions, list):
            return False
        
        return True
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            Block as dictionary
        """
        return {
            'block_index': self.block_index,
            'previous_hash': self.previous_hash,
            'block_hash': self.block_hash,
            'merkle_root': self.merkle_root,
            'timestamp': self.timestamp,
            'difficulty': self.difficulty,
            'nonce': self.nonce,
            'transactions': [tx.to_dict() if hasattr(tx, 'to_dict') else tx for tx in self.transactions],
            'miner_address': self.miner_address,
            'hash': self.hash
        }
    
    def to_json(self) -> str:
        """
        Convert to JSON string.
        
        Returns:
            Block as JSON string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BlockStorage':
        """
        Create from dictionary.
        
        Args:
            data: Block data
            
        Returns:
            BlockStorage instance
        """
        block = cls(**data)
        
        # Convert transactions to TransactionStorage objects
        if 'transactions' in data:
            block.transactions = []
            for tx_data in data['transactions']:
                block.transactions.append(TransactionStorage.from_dict(tx_data))
        
        return block
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BlockStorage':
        """
        Create from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            BlockStorage instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self):
        """String representation."""
        return f"BlockStorage(index={self.block_index}, hash={self.block_hash[:16]}...)"
    
    def __str__(self):
        """String representation for printing."""
        return self.to_json()


class TransactionStorage:
    """
    Transaction storage model.
    
    Represents a blockchain transaction for storage purposes.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize transaction storage.
        
        Args:
            **kwargs: Transaction attributes
        """
        self.transaction_id = kwargs.get('transaction_id', '')
        self.sender = kwargs.get('sender', '')
        self.recipient = kwargs.get('recipient', '')
        self.amount = kwargs.get('amount', 0.0)
        self.fee = kwargs.get('fee', 0.0)
        self.timestamp = kwargs.get('timestamp', self._get_current_timestamp())
        self.data = kwargs.get('data', {})
        self.signature = kwargs.get('signature', '')
        self.block_index = kwargs.get('block_index', None)
        self.logger = get_logger(__name__)
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp."""
        return time.time()
    
    def validate(self) -> bool:
        """
        Validate transaction structure.
        
        Returns:
            True if transaction is valid, False otherwise
        """
        if not isinstance(self.transaction_id, str) or len(self.transaction_id) != 64:
            return False
        
        if not isinstance(self.sender, str) or len(self.sender) != 40:
            return False
        
        if not isinstance(self.recipient, str) or len(self.recipient) != 40:
            return False
        
        if not isinstance(self.amount, (int, float)) or self.amount <= 0:
            return False
        
        if not isinstance(self.fee, (int, float)) or self.fee < 0:
            return False
        
        if not isinstance(self.timestamp, (int, float)) or self.timestamp <= 0:
            return False
        
        if not isinstance(self.data, dict):
            return False
        
        if not isinstance(self.signature, str) or len(self.signature) == 0:
            return False
        
        return True
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            Transaction as dictionary
        """
        return {
            'transaction_id': self.transaction_id,
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'fee': self.fee,
            'timestamp': self.timestamp,
            'data': self.data,
            'signature': self.signature,
            'block_index': self.block_index
        }
    
    def to_json(self) -> str:
        """
        Convert to JSON string.
        
        Returns:
            Transaction as JSON string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TransactionStorage':
        """
        Create from dictionary.
        
        Args:
            data: Transaction data
            
        Returns:
            TransactionStorage instance
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TransactionStorage':
        """
        Create from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            TransactionStorage instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self):
        """String representation."""
        return (f"TransactionStorage(id={self.transaction_id[:16]}..., "
                f"sender={self.sender[:8]}..., recipient={self.recipient[:8]}..., amount={self.amount})")
    
    def __str__(self):
        """String representation for printing."""
        return self.to_json()


class StateStorage:
    """
    State storage model.
    
    Represents the state of an address for storage purposes.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize state storage.
        
        Args:
            **kwargs: State attributes
        """
        self.address = kwargs.get('address', '')
        self.balance = kwargs.get('balance', 0.0)
        self.nonce = kwargs.get('nonce', 0)
        self.created_at = kwargs.get('created_at', self._get_current_timestamp())
        self.updated_at = kwargs.get('updated_at', self._get_current_timestamp())
        self.logger = get_logger(__name__)
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp."""
        return time.time()
    
    def validate(self) -> bool:
        """
        Validate state structure.
        
        Returns:
            True if state is valid, False otherwise
        """
        if not isinstance(self.address, str) or len(self.address) != 40:
            return False
        
        if not isinstance(self.balance, (int, float)) or self.balance < 0:
            return False
        
        if not isinstance(self.nonce, int) or self.nonce < 0:
            return False
        
        return True
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            State as dictionary
        """
        return {
            'address': self.address,
            'balance': self.balance,
            'nonce': self.nonce,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def to_json(self) -> str:
        """
        Convert to JSON string.
        
        Returns:
            State as JSON string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StateStorage':
        """
        Create from dictionary.
        
        Args:
            data: State data
            
        Returns:
            StateStorage instance
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'StateStorage':
        """
        Create from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            StateStorage instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self):
        """String representation."""
        return f"StateStorage(address={self.address[:8]}..., balance={self.balance}, nonce={self.nonce})"
    
    def __str__(self):
        """String representation for printing."""
        return self.to_json()


class ContractStorage:
    """
    Contract storage model.
    
    Represents a smart contract for storage purposes.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize contract storage.
        
        Args:
            **kwargs: Contract attributes
        """
        self.contract_address = kwargs.get('contract_address', '')
        self.source_code = kwargs.get('source_code', '')
        self.bytecode = kwargs.get('bytecode', '')
        self.language = kwargs.get('language', 'simple')
        self.compiler_options = kwargs.get('compiler_options', {})
        self.deployed_at = kwargs.get('deployed_at', self._get_current_timestamp())
        self.state = kwargs.get('state', 'deployed')
        self.bytecode_hash = kwargs.get('bytecode_hash', '')
        self.source_code_hash = kwargs.get('source_code_hash', '')
        self.updated_at = kwargs.get('updated_at')
        self.deactivated_at = kwargs.get('deactivated_at')
        self.activated_at = kwargs.get('activated_at')
        self.created_at = kwargs.get('created_at', self._get_current_timestamp())
        self.logger = get_logger(__name__)
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp."""
        return time.time()
    
    def validate(self) -> bool:
        """
        Validate contract structure.
        
        Returns:
            True if contract is valid, False otherwise
        """
        if not isinstance(self.contract_address, str) or len(self.contract_address) != 40:
            return False
        
        if not isinstance(self.source_code, str) or len(self.source_code) == 0:
            return False
        
        if not isinstance(self.bytecode, str) or len(self.bytecode) == 0:
            return False
        
        if not isinstance(self.language, str) or len(self.language) == 0:
            return False
        
        if not isinstance(self.compiler_options, dict):
            return False
        
        if not isinstance(self.deployed_at, (int, float)) or self.deployed_at <= 0:
            return False
        
        if not isinstance(self.state, str) or self.state not in ['deployed', 'deactivated']:
            return False
        
        if not isinstance(self.bytecode_hash, str) or len(self.bytecode_hash) != 64:
            return False
        
        if not isinstance(self.source_code_hash, str) or len(self.source_code_hash) != 64:
            return False
        
        return True
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            Contract as dictionary
        """
        return {
            'contract_address': self.contract_address,
            'source_code': self.source_code,
            'bytecode': self.bytecode,
            'language': self.language,
            'compiler_options': self.compiler_options,
            'deployed_at': self.deployed_at,
            'state': self.state,
            'bytecode_hash': self.bytecode_hash,
            'source_code_hash': self.source_code_hash,
            'updated_at': self.updated_at,
            'deactivated_at': self.deactivated_at,
            'activated_at': self.activated_at,
            'created_at': self.created_at
        }
    
    def to_json(self) -> str:
        """
        Convert to JSON string.
        
        Returns:
            Contract as JSON string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ContractStorage':
        """
        Create from dictionary.
        
        Args:
            data: Contract data
            
        Returns:
            ContractStorage instance
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ContractStorage':
        """
        Create from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            ContractStorage instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self):
        """String representation."""
        return f"ContractStorage(address={self.contract_address[:16]}..., state={self.state})"
    
    def __str__(self):
        """String representation for printing."""
        return self.to_json()


class WalletStorage:
    """
    Wallet storage model.
    
    Represents a blockchain wallet for storage purposes.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize wallet storage.
        
        Args:
            **kwargs: Wallet attributes
        """
        self.address = kwargs.get('address', '')
        self.public_key = kwargs.get('public_key', '')
        self.private_key = kwargs.get('private_key', '')
        self.created_at = kwargs.get('created_at', self._get_current_timestamp())
        self.updated_at = kwargs.get('updated_at', self._get_current_timestamp())
        self.logger = get_logger(__name__)
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp."""
        return time.time()
    
    def validate(self) -> bool:
        """
        Validate wallet structure.
        
        Returns:
            True if wallet is valid, False otherwise
        """
        if not isinstance(self.address, str) or len(self.address) != 40:
            return False
        
        if not isinstance(self.public_key, str) or len(self.public_key) == 0:
            return False
        
        if not isinstance(self.private_key, str) or len(self.private_key) == 0:
            return False
        
        return True
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            Wallet as dictionary
        """
        return {
            'address': self.address,
            'public_key': self.public_key,
            'private_key': self.private_key,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def to_json(self) -> str:
        """
        Convert to JSON string.
        
        Returns:
            Wallet as JSON string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WalletStorage':
        """
        Create from dictionary.
        
        Args:
            data: Wallet data
            
        Returns:
            WalletStorage instance
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WalletStorage':
        """
        Create from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            WalletStorage instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self):
        """String representation."""
        return f"WalletStorage(address={self.address[:8]}...)"
    
    def __str__(self):
        """String representation for printing."""
        return self.to_json()


class NodeStorage:
    """
    Node storage model.
    
    Represents a network node for storage purposes.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize node storage.
        
        Args:
            **kwargs: Node attributes
        """
        self.node_id = kwargs.get('node_id', '')
        self.address = kwargs.get('address', '')
        self.port = kwargs.get('port', 8080)
        self.last_seen = kwargs.get('last_seen', self._get_current_timestamp())
        self.is_connected = kwargs.get('is_connected', False)
        self.created_at = kwargs.get('created_at', self._get_current_timestamp())
        self.updated_at = kwargs.get('updated_at', self._get_current_timestamp())
        self.logger = get_logger(__name__)
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp."""
        return time.time()
    
    def validate(self) -> bool:
        """
        Validate node structure.
        
        Returns:
            True if node is valid, False otherwise
        """
        if not isinstance(self.node_id, str) or len(self.node_id) == 0:
            return False
        
        if not isinstance(self.address, str) or len(self.address) == 0:
            return False
        
        if not isinstance(self.port, int) or self.port < 1 or self.port > 65535:
            return False
        
        if not isinstance(self.last_seen, (int, float)) or self.last_seen <= 0:
            return False
        
        if not isinstance(self.is_connected, bool):
            return False
        
        return True
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            Node as dictionary
        """
        return {
            'node_id': self.node_id,
            'address': self.address,
            'port': self.port,
            'last_seen': self.last_seen,
            'is_connected': self.is_connected,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def to_json(self) -> str:
        """
        Convert to JSON string.
        
        Returns:
            Node as JSON string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NodeStorage':
        """
        Create from dictionary.
        
        Args:
            data: Node data
            
        Returns:
            NodeStorage instance
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'NodeStorage':
        """
        Create from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            NodeStorage instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self):
        """String representation."""
        return f"NodeStorage(id={self.node_id[:8]}..., address={self.address}:{self.port})"
    
    def __str__(self):
        """String representation for printing."""
        return self.to_json()


class StatStorage:
    """
    Statistic storage model.
    
    Represents a statistic for storage purposes.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize stat storage.
        
        Args:
            **kwargs: Stat attributes
        """
        self.key = kwargs.get('key', '')
        self.value = kwargs.get('value', '')
        self.updated_at = kwargs.get('updated_at', self._get_current_timestamp())
        self.logger = get_logger(__name__)
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp."""
        return time.time()
    
    def validate(self) -> bool:
        """
        Validate stat structure.
        
        Returns:
            True if stat is valid, False otherwise
        """
        if not isinstance(self.key, str) or len(self.key) == 0:
            return False
        
        if not isinstance(self.value, (str, int, float, bool)):
            return False
        
        if not isinstance(self.updated_at, (int, float)) or self.updated_at <= 0:
            return False
        
        return True
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            Stat as dictionary
        """
        return {
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at
        }
    
    def to_json(self) -> str:
        """
        Convert to JSON string.
        
        Returns:
            Stat as JSON string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StatStorage':
        """
        Create from dictionary.
        
        Args:
            data: Stat data
            
        Returns:
            StatStorage instance
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'StatStorage':
        """
        Create from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            StatStorage instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self):
        """String representation."""
        return f"StatStorage(key={self.key}, value={self.value})"
    
    def __str__(self):
        """String representation for printing."""
        return self.to_json()
