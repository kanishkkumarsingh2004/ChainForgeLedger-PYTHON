"""
ChainForgeLedger Proof of Work Consensus

Proof of Work consensus mechanism implementation.
"""

import time
from chainforgeledger.core.block import Block
from chainforgeledger.core.blockchain import Blockchain
from chainforgeledger.core.transaction import Transaction


class ProofOfWork:
    """
    Proof of Work consensus mechanism.
    
    Attributes:
        blockchain: Blockchain instance
        difficulty: Mining difficulty
        reward: Block reward
    """
    
    def __init__(self, blockchain: Blockchain, difficulty: int = 3, reward: float = 50.0):
        """
        Initialize a new ProofOfWork instance.
        
        Args:
            blockchain: Blockchain instance
            difficulty: Mining difficulty (number of leading zeros)
            reward: Block reward for miners
        """
        self.blockchain = blockchain
        self.difficulty = difficulty
        self.reward = reward
    
    def mine_block(self, transactions: list, miner_address: str) -> Block:
        """
        Mine a new block.
        
        Args:
            transactions: List of transactions to include
            miner_address: Miner's address
            
        Returns:
            Mined block
        """
        previous_block = self.blockchain.get_last_block()
        index = previous_block.index + 1
        previous_hash = previous_block.hash
        
        # Add mining reward transaction
        mining_reward = Transaction(
            sender="0",
            receiver=miner_address,
            amount=self.reward
        )
        transactions.append(mining_reward.to_dict())
        
        # Mining loop
        block = Block(
            index=index,
            previous_hash=previous_hash,
            transactions=transactions,
            difficulty=self.difficulty
        )
        
        start_time = time.time()
        
        while True:
            block_hash = self.calculate_hash_with_difficulty(block)
            
            if block_hash.startswith("0" * self.difficulty):
                block.hash = block_hash
                break
                
            block.nonce += 1
            block.timestamp = time.time()
        
        mining_time = time.time() - start_time
        
        return block
    
    def calculate_hash_with_difficulty(self, block: Block) -> str:
        """
        Calculate block hash with difficulty.
        
        Args:
            block: Block to calculate hash for
            
        Returns:
            SHA-256 hash
        """
        return block.calculate_hash()
    
    def validate_block(self, block: Block) -> bool:
        """
        Validate a block against PoW requirements.
        
        Args:
            block: Block to validate
            
        Returns:
            True if valid
        """
        # Check hash starts with required number of zeros
        if not block.hash.startswith("0" * self.difficulty):
            return False
        
        # Validate block structure
        if not self.blockchain.is_valid_block(block):
            return False
            
        # Check mining reward
        mining_rewards = [
            tx for tx in block.transactions
            if isinstance(tx, dict) and tx.get("sender") == "0"
        ]
        
        if len(mining_rewards) != 1:
            return False
            
        if mining_rewards[0].get("amount") != self.reward:
            return False
        
        return True
    
    def adjust_difficulty(self, blocks_per_adjustment: int = 10, target_time: float = 60):
        """
        Adjust difficulty based on mining speed.
        
        Args:
            blocks_per_adjustment: Number of blocks between adjustments
            target_time: Target time per block in seconds
        """
        if len(self.blockchain.chain) < blocks_per_adjustment:
            return
            
        # Calculate average block time over last adjustment period
        start_block = len(self.blockchain.chain) - blocks_per_adjustment
        total_time = 0.0
        
        for i in range(start_block, len(self.blockchain.chain) - 1):
            current_block = self.blockchain.chain[i]
            next_block = self.blockchain.chain[i + 1]
            total_time += next_block.timestamp - current_block.timestamp
            
        average_time = total_time / blocks_per_adjustment
        
        # Adjust difficulty
        if average_time < target_time * 0.5:
            self.difficulty += 1
        elif average_time > target_time * 2:
            self.difficulty = max(1, self.difficulty - 1)
    
    def get_mining_statistics(self) -> dict:
        """
        Get mining statistics.
        
        Returns:
            Dictionary with mining statistics
        """
        return {
            "difficulty": self.difficulty,
            "block_reward": self.reward,
            "chain_length": len(self.blockchain.chain),
            "transactions_per_block": sum(
                len(block.transactions) for block in self.blockchain.chain
            ) / len(self.blockchain.chain)
        }
    
    def __repr__(self):
        """String representation of PoW consensus."""
        return f"ProofOfWork(difficulty={self.difficulty}, reward={self.reward})"
    
    def __str__(self):
        """String representation for printing."""
        stats = self.get_mining_statistics()
        return (
            f"Proof of Work Consensus\n"
            f"=======================\n"
            f"Difficulty: {stats['difficulty']}\n"
            f"Block Reward: {stats['block_reward']}\n"
            f"Chain Length: {stats['chain_length']}\n"
            f"Transactions per Block: {stats['transactions_per_block']:.1f}"
        )
