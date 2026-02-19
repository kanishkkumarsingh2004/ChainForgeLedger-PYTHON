"""
ChainForgeLedger Node Module

Node implementation for blockchain network communication.
"""

import time
import random
from chainforgeledger.networking.peer import Peer
from chainforgeledger.networking.protocol import Protocol
from chainforgeledger.networking.mempool import MemPool


class Node:
    """
    Represents a blockchain network node.
    
    Attributes:
        node_id: Node identifier
        address: Network address
        port: Network port
        peers: List of connected peers
        mempool: Transaction mempool
        protocol: Network protocol
    """
    
    def __init__(self, node_id: str, address: str = "127.0.0.1", port: int = 8333):
        """
        Initialize a new Node instance.
        
        Args:
            node_id: Node identifier
            address: Network address
            port: Network port
        """
        self.node_id = node_id
        self.address = address
        self.port = port
        self.peers = []
        self.mempool = MemPool()
        self.protocol = Protocol()
        self.is_running = False
        self.start_time = None
    
    def connect(self, peer: "Node"):
        """
        Connect to a peer node.
        
        Args:
            peer: Peer node to connect to
        """
        peer_info = Peer(peer.node_id, peer.address, peer.port)
        self.peers.append(peer_info)
        peer.peers.append(Peer(self.node_id, self.address, self.port))
    
    def disconnect(self, peer: "Node"):
        """
        Disconnect from a peer node.
        
        Args:
            peer: Peer node to disconnect from
        """
        self.peers = [p for p in self.peers if p.node_id != peer.node_id]
        peer.peers = [p for p in peer.peers if p.node_id != self.node_id]
    
    def broadcast(self, message: dict):
        """
        Broadcast a message to all connected peers.
        
        Args:
            message: Message to broadcast
        """
        for peer in self.peers:
            self.send_message(peer.node_id, message)
    
    def send_message(self, recipient_node_id: str, message: dict):
        """
        Send a message to a specific peer.
        
        Args:
            recipient_node_id: Recipient node ID
            message: Message to send
        """
        peer = next((p for p in self.peers if p.node_id == recipient_node_id), None)
        if peer:
            # Simulate network delay
            time.sleep(random.uniform(0.001, 0.01))
            # For demo purposes, just print the message
            print(f"Node {self.node_id} sent to {recipient_node_id}: {message.get('type')}")
        else:
            print(f"Node {self.node_id}: Peer {recipient_node_id} not found")
    
    def receive_message(self, sender_node_id: str, message: dict):
        """
        Receive a message from a peer.
        
        Args:
            sender_node_id: Sender node ID
            message: Received message
        """
        # Handle message based on type
        msg_type = message.get("type", "unknown")
        
        if msg_type == "block":
            self.handle_block_message(message)
        elif msg_type == "transaction":
            self.handle_transaction_message(message)
        elif msg_type == "ping":
            self.handle_ping_message(sender_node_id, message)
        else:
            print(f"Node {self.node_id}: Unknown message type {msg_type}")
    
    def handle_block_message(self, message: dict):
        """
        Handle block message.
        
        Args:
            message: Block message
        """
        print(f"Node {self.node_id}: Received block message")
    
    def handle_transaction_message(self, message: dict):
        """
        Handle transaction message.
        
        Args:
            message: Transaction message
        """
        print(f"Node {self.node_id}: Received transaction message")
        transaction = message.get("data")
        if transaction:
            self.mempool.add_transaction(transaction)
    
    def handle_ping_message(self, sender_node_id: str, message: dict):
        """
        Handle ping message.
        
        Args:
            sender_node_id: Sender node ID
            message: Ping message
        """
        # Send pong response
        response = {
            "type": "pong",
            "data": {
                "node_id": self.node_id,
                "timestamp": time.time()
            }
        }
        self.send_message(sender_node_id, response)
    
    def start(self):
        """Start node operations."""
        self.is_running = True
        self.start_time = time.time()
        print(f"Node {self.node_id} started at {self.address}:{self.port}")
    
    def stop(self):
        """Stop node operations."""
        self.is_running = False
        print(f"Node {self.node_id} stopped")
    
    def is_connected(self) -> bool:
        """Check if node is connected to network."""
        return self.is_running and len(self.peers) > 0
    
    def get_node_info(self) -> dict:
        """
        Get node information.
        
        Returns:
            Node information dictionary
        """
        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "status": "running" if self.is_running else "stopped",
            "peers": len(self.peers),
            "transactions_in_mempool": len(self.mempool.transactions),
            "uptime": int(time.time() - self.start_time) if self.start_time else 0
        }
    
    def to_dict(self) -> dict:
        """
        Convert node to dictionary.
        
        Returns:
            Dictionary representation of node
        """
        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "peers": [p.to_dict() for p in self.peers],
            "mempool": self.mempool.to_dict(),
            "is_running": self.is_running,
            "start_time": self.start_time
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Node":
        """
        Create node from dictionary.
        
        Args:
            data: Node data
            
        Returns:
            Node instance
        """
        node = cls(data.get("node_id", ""), data.get("address", "127.0.0.1"), data.get("port", 8333))
        
        for peer_data in data.get("peers", []):
            peer = Peer.from_dict(peer_data)
            node.peers.append(peer)
            
        node.is_running = data.get("is_running", False)
        node.start_time = data.get("start_time")
        
        return node
    
    def __repr__(self):
        """String representation of node."""
        return f"Node(node_id={self.node_id}, address={self.address}:{self.port}, peers={len(self.peers)})"
    
    def __str__(self):
        """String representation for printing."""
        info = self.get_node_info()
        return (
            f"Node {self.node_id}\n"
            f"============\n"
            f"Address: {self.address}:{self.port}\n"
            f"Status: {info['status']}\n"
            f"Peers: {info['peers']}\n"
            f"Transactions in Mempool: {info['transactions_in_mempool']}\n"
            f"Uptime: {info['uptime']} seconds"
        )
