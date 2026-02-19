"""
ChainForgeLedger Network Protocol Layer

Protocol definitions for blockchain network communication.
"""

import time
from typing import Any, Dict, List
from chainforgeledger.utils.logger import get_logger


class Protocol:
    """
    Network protocol implementation for blockchain communication.
    
    Defines the communication protocol for blockchain nodes including:
    - Message formats
    - Network commands
    - Data serialization
    - Protocol versions
    """
    
    VERSION = "1.0.0"
    SUPPORTED_VERSIONS = ["1.0.0"]
    
    MESSAGE_TYPES = {
        "block": "block",
        "transaction": "transaction",
        "ping": "ping",
        "pong": "pong",
        "get_blocks": "get_blocks",
        "blocks": "blocks",
        "get_transactions": "get_transactions",
        "transactions": "transactions",
        "new_block": "new_block",
        "new_transaction": "new_transaction"
    }
    
    COMMANDS = {
        "get_blocks": "get_blocks",
        "send_blocks": "send_blocks",
        "get_transactions": "get_transactions",
        "send_transactions": "send_transactions",
        "ping": "ping",
        "pong": "pong"
    }
    
    def __init__(self):
        """Initialize protocol instance."""
        self.logger = get_logger(__name__)
    
    def create_message(self, message_type: str, data: Any, metadata: Dict[str, Any] = None) -> Dict:
        """
        Create a protocol message.
        
        Args:
            message_type: Type of message (see MESSAGE_TYPES)
            data: Message data
            metadata: Additional metadata
            
        Returns:
            Formatted protocol message
        """
        if message_type not in self.MESSAGE_TYPES.values():
            raise ValueError(f"Unknown message type: {message_type}")
        
        message = {
            "version": self.VERSION,
            "type": message_type,
            "timestamp": time.time(),
            "data": data
        }
        
        if metadata:
            message["metadata"] = metadata
        
        return message
    
    def validate_message(self, message: Dict) -> bool:
        """
        Validate a received message.
        
        Args:
            message: Message to validate
            
        Returns:
            True if message is valid, False otherwise
        """
        # Check version
        if "version" not in message or message["version"] not in self.SUPPORTED_VERSIONS:
            self.logger.warning(f"Unsupported protocol version: {message.get('version')}")
            return False
        
        # Check type
        if "type" not in message or message["type"] not in self.MESSAGE_TYPES.values():
            self.logger.warning(f"Unknown message type: {message.get('type')}")
            return False
        
        # Check timestamp
        if "timestamp" not in message or not isinstance(message["timestamp"], (int, float)):
            self.logger.warning("Invalid timestamp")
            return False
        
        # Check data
        if "data" not in message:
            self.logger.warning("No message data")
            return False
        
        return True
    
    def serialize_message(self, message: Dict) -> str:
        """
        Serialize message for network transmission.
        
        Args:
            message: Message to serialize
            
        Returns:
            Serialized message string
        """
        import json
        return json.dumps(message)
    
    def deserialize_message(self, serialized_message: str) -> Dict:
        """
        Deserialize message from network transmission.
        
        Args:
            serialized_message: Serialized message string
            
        Returns:
            Deserialized message dictionary
        """
        import json
        return json.loads(serialized_message)
    
    def create_ping_message(self, node_id: str) -> Dict:
        """
        Create ping message.
        
        Args:
            node_id: Sender node ID
            
        Returns:
            Ping message
        """
        return self.create_message(
            self.MESSAGE_TYPES["ping"],
            {
                "node_id": node_id,
                "timestamp": time.time()
            }
        )
    
    def create_pong_message(self, node_id: str) -> Dict:
        """
        Create pong message.
        
        Args:
            node_id: Sender node ID
            
        Returns:
            Pong message
        """
        return self.create_message(
            self.MESSAGE_TYPES["pong"],
            {
                "node_id": node_id,
                "timestamp": time.time()
            }
        )
    
    def create_block_message(self, block: Dict) -> Dict:
        """
        Create block message.
        
        Args:
            block: Block data
            
        Returns:
            Block message
        """
        return self.create_message(
            self.MESSAGE_TYPES["block"],
            block
        )
    
    def create_transaction_message(self, transaction: Dict) -> Dict:
        """
        Create transaction message.
        
        Args:
            transaction: Transaction data
            
        Returns:
            Transaction message
        """
        return self.create_message(
            self.MESSAGE_TYPES["transaction"],
            transaction
        )
    
    def create_new_block_message(self, block: Dict) -> Dict:
        """
        Create new block message.
        
        Args:
            block: New block data
            
        Returns:
            New block message
        """
        return self.create_message(
            self.MESSAGE_TYPES["new_block"],
            block
        )
    
    def create_new_transaction_message(self, transaction: Dict) -> Dict:
        """
        Create new transaction message.
        
        Args:
            transaction: New transaction data
            
        Returns:
            New transaction message
        """
        return self.create_message(
            self.MESSAGE_TYPES["new_transaction"],
            transaction
        )
    
    def create_get_blocks_message(self, start_block: int = 0, end_block: int = -1) -> Dict:
        """
        Create get blocks message.
        
        Args:
            start_block: Start block height
            end_block: End block height (-1 for latest)
            
        Returns:
            Get blocks message
        """
        return self.create_message(
            self.MESSAGE_TYPES["get_blocks"],
            {
                "start_block": start_block,
                "end_block": end_block
            }
        )
    
    def create_blocks_message(self, blocks: List[Dict]) -> Dict:
        """
        Create blocks message.
        
        Args:
            blocks: List of blocks
            
        Returns:
            Blocks message
        """
        return self.create_message(
            self.MESSAGE_TYPES["blocks"],
            blocks
        )
    
    def create_get_transactions_message(self, count: int = 100) -> Dict:
        """
        Create get transactions message.
        
        Args:
            count: Number of transactions to request
            
        Returns:
            Get transactions message
        """
        return self.create_message(
            self.MESSAGE_TYPES["get_transactions"],
            {
                "count": count
            }
        )
    
    def create_transactions_message(self, transactions: List[Dict]) -> Dict:
        """
        Create transactions message.
        
        Args:
            transactions: List of transactions
            
        Returns:
            Transactions message
        """
        return self.create_message(
            self.MESSAGE_TYPES["transactions"],
            transactions
        )
    
    def get_message_type(self, message: Dict) -> str:
        """
        Get message type from message.
        
        Args:
            message: Message
            
        Returns:
            Message type
        """
        return message.get("type", "unknown")
    
    def get_message_data(self, message: Dict) -> Any:
        """
        Get message data from message.
        
        Args:
            message: Message
            
        Returns:
            Message data
        """
        return message.get("data")
    
    def get_message_timestamp(self, message: Dict) -> float:
        """
        Get message timestamp from message.
        
        Args:
            message: Message
            
        Returns:
            Message timestamp
        """
        return message.get("timestamp", 0.0)
    
    def is_block_message(self, message: Dict) -> bool:
        """Check if message is a block message."""
        return self.get_message_type(message) == self.MESSAGE_TYPES["block"]
    
    def is_transaction_message(self, message: Dict) -> bool:
        """Check if message is a transaction message."""
        return self.get_message_type(message) == self.MESSAGE_TYPES["transaction"]
    
    def is_new_block_message(self, message: Dict) -> bool:
        """Check if message is a new block message."""
        return self.get_message_type(message) == self.MESSAGE_TYPES["new_block"]
    
    def is_new_transaction_message(self, message: Dict) -> bool:
        """Check if message is a new transaction message."""
        return self.get_message_type(message) == self.MESSAGE_TYPES["new_transaction"]
    
    def is_ping_message(self, message: Dict) -> bool:
        """Check if message is a ping message."""
        return self.get_message_type(message) == self.MESSAGE_TYPES["ping"]
    
    def is_pong_message(self, message: Dict) -> bool:
        """Check if message is a pong message."""
        return self.get_message_type(message) == self.MESSAGE_TYPES["pong"]
    
    def is_get_blocks_message(self, message: Dict) -> bool:
        """Check if message is a get blocks message."""
        return self.get_message_type(message) == self.MESSAGE_TYPES["get_blocks"]
    
    def is_blocks_message(self, message: Dict) -> bool:
        """Check if message is a blocks message."""
        return self.get_message_type(message) == self.MESSAGE_TYPES["blocks"]
    
    def is_get_transactions_message(self, message: Dict) -> bool:
        """Check if message is a get transactions message."""
        return self.get_message_type(message) == self.MESSAGE_TYPES["get_transactions"]
    
    def is_transactions_message(self, message: Dict) -> bool:
        """Check if message is a transactions message."""
        return self.get_message_type(message) == self.MESSAGE_TYPES["transactions"]
    
    def get_protocol_info(self) -> Dict:
        """
        Get protocol information.
        
        Returns:
            Protocol information dictionary
        """
        return {
            "version": self.VERSION,
            "supported_versions": self.SUPPORTED_VERSIONS,
            "message_types": list(self.MESSAGE_TYPES.values()),
            "commands": list(self.COMMANDS.values())
        }
