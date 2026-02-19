"""
ChainForgeLedger Blockchain Module

Core blockchain data structure and management.
"""

from typing import Optional
from chainforgeledger.core.block import Block



class Blockchain:
    """
    Represents the blockchain data structure.
    
    Attributes:
        chain: List of blocks
        difficulty: Current mining difficulty (for PoW)
        reward: Block reward
    """
    
    def __init__(self, difficulty: int = 3, reward: float = 50.0):
        """
        Initialize a new Blockchain instance.
        
        Args:
            difficulty: Mining difficulty level
            reward: Block reward for miners/validators
        """
        self.chain = []
        self._block_hash_map = {}  # For O(1) block lookups by hash
        self.difficulty = difficulty
        self.reward = reward
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """
        Create the first block in the chain (genesis block).
        """
        genesis_block = Block(
            index=0,
            previous_hash="0" * 64,
            transactions=[],
            difficulty=self.difficulty
        )
        self.chain.append(genesis_block)
        self._block_hash_map[genesis_block.hash] = genesis_block
    
    def get_last_block(self) -> Block:
        """
        Get the last block in the chain.
        
        Returns:
            Last block in the chain
        """
        return self.chain[-1]
    
    def add_block(self, block: Block):
        """
        Add a new block to the chain.
        
        Args:
            block: Block to add
        """
        if self.is_valid_block(block):
            self.chain.append(block)
            self._block_hash_map[block.hash] = block
        else:
            raise ValueError("Invalid block")
    
    def is_valid_block(self, block: Block) -> bool:
        """
        Validate a block before adding to the chain.
        
        Args:
            block: Block to validate
            
        Returns:
            True if block is valid
        """
        previous_block = self.get_last_block()
        
        # Check block index
        if block.index != previous_block.index + 1:
            return False
        
        # Check previous hash
        if block.previous_hash != previous_block.hash:
            return False
        
        # Check block hash
        if not block.validate_block():
            return False
        
        return True
    
    def is_chain_valid(self) -> bool:
        """
        Validate the entire blockchain.
        
        Returns:
            True if chain is valid
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check block index
            if current_block.index != previous_block.index + 1:
                return False
            
            # Check previous hash
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Check block hash
            if not current_block.validate_block():
                return False
        
        return True
    
    def get_block_by_index(self, index: int) -> Optional[Block]:
        """
        Get block by index.
        
        Args:
            index: Block index
            
        Returns:
            Block if found, None otherwise
        """
        if index < 0 or index >= len(self.chain):
            return None
        return self.chain[index]
    
    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        """
        Get block by hash.
        
        Args:
            block_hash: Block hash
            
        Returns:
            Block if found, None otherwise
        """
        return self._block_hash_map.get(block_hash)
    
    def get_blockchain_info(self) -> dict:
        """
        Get blockchain information.
        
        Returns:
            Dictionary with blockchain details
        """
        total_transactions = sum(len(block.transactions) for block in self.chain)
        
        return {
            "chain_length": len(self.chain),
            "difficulty": self.difficulty,
            "total_transactions": total_transactions,
            "last_block_hash": self.get_last_block().hash,
            "is_valid": self.is_chain_valid()
        }
    
    def __repr__(self):
        """String representation of the blockchain."""
        return f"Blockchain(length={len(self.chain)}, difficulty={self.difficulty})"
    
    def __str__(self):
        """String representation for printing."""
        info = self.get_blockchain_info()
        return (
            f"Blockchain Information\n"
            f"======================\n"
            f"Chain Length: {info['chain_length']}\n"
            f"Difficulty: {info['difficulty']}\n"
            f"Total Transactions: {info['total_transactions']}\n"
            f"Last Block Hash: {info['last_block_hash']}\n"
            f"Chain Valid: {info['is_valid']}"
        )
