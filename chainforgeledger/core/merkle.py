"""
ChainForgeLedger Merkle Tree Module

Merkle tree implementation for blockchain transaction verification.
"""

from typing import List
from chainforgeledger.crypto.hashing import sha256_hash


class MerkleTree:
    """
    Merkle tree implementation for transaction verification.
    
    Attributes:
        transactions: List of transactions
        root: Root hash of the merkle tree
        levels: Tree levels
    """
    
    def __init__(self, transactions: List[str]):
        """
        Initialize a new MerkleTree instance.
        
        Args:
            transactions: List of transactions
        """
        self.transactions = transactions
        self.root = None
        self.levels = []
        self.build_tree()
    
    def build_tree(self):
        """Build the Merkle tree from transactions."""
        if not self.transactions:
            self.root = sha256_hash("")
            return
        
        # Initialize leaves
        leaves = [sha256_hash(str(tx)) for tx in self.transactions]
        self.levels.append(leaves)
        
        # Build tree
        while len(leaves) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(leaves), 2):
                left_hash = leaves[i]
                
                # If odd number of leaves, duplicate the last one
                right_hash = leaves[i + 1] if (i + 1) < len(leaves) else left_hash
                
                # Combine and hash
                combined_hash = sha256_hash(left_hash + right_hash)
                next_level.append(combined_hash)
            
            leaves = next_level
            self.levels.append(leaves)
        
        self.root = self.levels[-1][0]
    
    def get_root_hash(self) -> str:
        """
        Get root hash of the merkle tree.
        
        Returns:
            Root hash
        """
        return self.root
    
    def get_proof(self, transaction: str) -> List[str]:
        """
        Get merkle proof for a specific transaction.
        
        Args:
            transaction: Transaction to get proof for
            
        Returns:
            List of hashes forming the merkle proof
        """
        if transaction not in self.transactions:
            return []
            
        index = self.transactions.index(transaction)
        proof = []
        
        # Traverse levels
        for level in self.levels:
            if len(level) == 1:
                break
                
            sibling_index = index + 1 if index % 2 == 0 else index - 1
            sibling_hash = level[sibling_index]
            proof.append(sibling_hash)
            
            index = index // 2
        
        return proof
    
    def verify_proof(self, transaction: str, proof: List[str], root: str) -> bool:
        """
        Verify a merkle proof for a transaction.
        
        Args:
            transaction: Transaction to verify
            proof: Merkle proof
            root: Root hash to verify against
            
        Returns:
            True if proof is valid
        """
        if not transaction or not proof:
            return False
            
        current_hash = sha256_hash(str(transaction))
        
        for sibling_hash in proof:
            # Determine if current hash should be left or right
            current_hash = sha256_hash(current_hash + sibling_hash)
        
        return current_hash == root
    
    def verify_tree(self) -> bool:
        """
        Verify the entire merkle tree.
        
        Returns:
            True if tree is valid
        """
        # Recompute root and compare
        original_root = self.root
        self.build_tree()
        
        return original_root == self.root
    
    def add_transaction(self, transaction: str):
        """
        Add a new transaction to the merkle tree.
        
        Args:
            transaction: Transaction to add
        """
        self.transactions.append(transaction)
        self.build_tree()
    
    def remove_transaction(self, transaction: str):
        """
        Remove a transaction from the merkle tree.
        
        Args:
            transaction: Transaction to remove
        """
        if transaction in self.transactions:
            self.transactions.remove(transaction)
            self.build_tree()
    
    def get_level_count(self) -> int:
        """
        Get number of levels in the tree.
        
        Returns:
            Number of levels
        """
        return len(self.levels)
    
    def __repr__(self):
        """String representation of merkle tree."""
        return (
            f"MerkleTree(transactions={len(self.transactions)}, "
            f"root={self.root[:16]}..., levels={self.get_level_count()})"
        )
    
    def __str__(self):
        """String representation for printing."""
        return (
            f"Merkle Tree\n"
            f"==========\n"
            f"Root Hash: {self.root}\n"
            f"Transactions: {len(self.transactions)}\n"
            f"Tree Levels: {self.get_level_count()}"
        )
