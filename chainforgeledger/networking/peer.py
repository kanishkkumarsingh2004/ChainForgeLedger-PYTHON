"""
ChainForgeLedger Peer Module

Peer discovery and communication implementation.
"""

import time
from chainforgeledger.utils.logger import get_logger


class Peer:
    """
    Represents a peer in the blockchain network.
    
    Attributes:
        node_id: Peer node identifier
        address: Network address
        port: Network port
        last_seen: Last communication time
        is_connected: Connection status
    """
    
    def __init__(self, node_id: str, address: str = "127.0.0.1", port: int = 8333):
        """
        Initialize a new Peer instance.
        
        Args:
            node_id: Peer node identifier
            address: Network address
            port: Network port
        """
        self.node_id = node_id
        self.address = address
        self.port = port
        self.last_seen = time.time()
        self.is_connected = True
        self.logger = get_logger(__name__)
    
    def update_last_seen(self):
        """Update last seen timestamp."""
        self.last_seen = time.time()
    
    def mark_connected(self):
        """Mark peer as connected."""
        self.is_connected = True
        self.update_last_seen()
    
    def mark_disconnected(self):
        """Mark peer as disconnected."""
        self.is_connected = False
    
    def get_info(self) -> dict:
        """
        Get peer information.
        
        Returns:
            Peer information dictionary
        """
        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "last_seen": self.last_seen,
            "is_connected": self.is_connected,
            "uptime": int(time.time() - self.last_seen)
        }
    
    def to_dict(self) -> dict:
        """
        Convert peer to dictionary.
        
        Returns:
            Dictionary representation of peer
        """
        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "last_seen": self.last_seen,
            "is_connected": self.is_connected
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Peer":
        """
        Create peer from dictionary.
        
        Args:
            data: Peer data
            
        Returns:
            Peer instance
        """
        peer = cls(data.get("node_id", ""), data.get("address", "127.0.0.1"), data.get("port", 8333))
        peer.last_seen = data.get("last_seen", time.time())
        peer.is_connected = data.get("is_connected", True)
        
        return peer
    
    def __repr__(self):
        """String representation of peer."""
        return f"Peer(node_id={self.node_id}, address={self.address}:{self.port}, connected={self.is_connected})"
    
    def __str__(self):
        """String representation for printing."""
        info = self.get_info()
        return (
            f"Peer {self.node_id}\n"
            f"============\n"
            f"Address: {self.address}:{self.port}\n"
            f"Status: {'Connected' if info['is_connected'] else 'Disconnected'}\n"
            f"Last Seen: {info['last_seen']:.2f} seconds ago"
        )
    
    def __eq__(self, other):
        """Equality check based on node_id."""
        if isinstance(other, Peer):
            return self.node_id == other.node_id
        return False
    
    def __hash__(self):
        """Hash based on node_id."""
        return hash(self.node_id)
