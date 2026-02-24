"""
ChainForgeLedger - Light Client

A light client implementation that verifies block headers and Merkle proofs
without executing full block states, providing a lightweight way to interact
with the blockchain network.
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from chainforgeledger.crypto.hashing import sha256_hash


@dataclass
class BlockHeader:
    """Block header for light client verification"""
    index: int
    previous_hash: str
    tx_root: str
    state_root: str
    receipt_root: str
    validator: str
    timestamp: float
    hash: str


class LightClient:
    """
    Light client for blockchain verification
    """
    
    def __init__(self, options: Dict = None):
        options = options or {}
        self.network = options.get('network', 'mainnet')
        self.genesis_block = options.get('genesisBlock')
        self.block_headers: Dict[int, BlockHeader] = {}
        self.current_block_height = 0
        
        if self.genesis_block:
            self.block_headers[0] = self.genesis_block
    
    def verify_block_header(self, header: BlockHeader) -> Dict:
        """Verify block header integrity and chain consistency"""
        errors = []
        
        # Check block index
        if not isinstance(header.index, int) or header.index < 0:
            errors.append("Invalid block index")
        
        # Check previous block hash for non-genesis blocks
        if header.index > 0:
            if header.index != self.current_block_height + 1:
                errors.append(f"Block height gap detected: expected {self.current_block_height + 1}, got {header.index}")
            
            if header.index - 1 not in self.block_headers:
                errors.append(f"Previous block header not found: {header.index - 1}")
            else:
                expected_previous = self.block_headers[header.index - 1].hash
                if header.previous_hash != expected_previous:
                    errors.append(f"Invalid previous block hash: expected {expected_previous}, got {header.previous_hash}")
        
        # Check timestamp
        if header.index > 0:
            previous_timestamp = self.block_headers[header.index - 1].timestamp
            if header.timestamp <= previous_timestamp:
                errors.append(f"Invalid timestamp: block {header.index} timestamp <= block {header.index - 1} timestamp")
        
        # Check hash consistency
        calculated_hash = self._calculate_header_hash(header)
        if calculated_hash != header.hash:
            errors.append(f"Invalid block hash: expected {calculated_hash}, got {header.hash}")
        
        return {
            'isValid': len(errors) == 0,
            'errors': errors,
            'header': header
        }
    
    def _calculate_header_hash(self, header: BlockHeader) -> str:
        """Calculate hash of block header"""
        header_data = (
            f"{header.index}"
            f"{header.previous_hash}"
            f"{header.tx_root}"
            f"{header.state_root}"
            f"{header.receipt_root}"
            f"{header.validator}"
            f"{header.timestamp}"
        )
        return sha256_hash(header_data)
    
    def add_block_header(self, header: BlockHeader) -> Dict:
        """Add and verify block header"""
        verification = self.verify_block_header(header)
        
        if verification['isValid']:
            self.block_headers[header.index] = header
            if header.index > self.current_block_height:
                self.current_block_height = header.index
        
        return verification
    
    def verify_merkle_proof(self, root: str, leaf: str, proof: List[str]) -> bool:
        """
        Verify Merkle proof for a leaf in a Merkle tree
        Returns True if the proof is valid for the given root and leaf
        """
        if not proof:
            return root == leaf
        
        current_hash = leaf
        
        for step in proof:
            # Each step is a tuple (hash, position) where position is 'left' or 'right'
            if isinstance(step, tuple):
                hash_part, position = step
            else:
                # Simple case: just concatenation
                hash_part = step
                position = 'left'
            
            if position == 'left':
                current_hash = sha256_hash(f"{hash_part}{current_hash}")
            else:
                current_hash = sha256_hash(f"{current_hash}{hash_part}")
        
        return current_hash == root
    
    def verify_transaction_inclusion(self, transaction_hash: str, block_header: BlockHeader, proof: List[str]) -> bool:
        """Verify that a transaction exists in a block"""
        return self.verify_merkle_proof(block_header.tx_root, transaction_hash, proof)
    
    def verify_receipt_inclusion(self, receipt_hash: str, block_header: BlockHeader, proof: List[str]) -> bool:
        """Verify that a receipt exists in a block"""
        return self.verify_merkle_proof(block_header.receipt_root, receipt_hash, proof)
    
    def verify_account_state(self, account_data: str, state_root: str, proof: List[str]) -> bool:
        """Verify that an account's state is included in the state root"""
        return self.verify_merkle_proof(state_root, account_data, proof)
    
    def get_block_header(self, block_number: int) -> Optional[BlockHeader]:
        """Get block header by block number"""
        return self.block_headers.get(block_number)
    
    def get_current_height(self) -> int:
        """Get current blockchain height"""
        return self.current_block_height
    
    def get_block_headers(self) -> List[BlockHeader]:
        """Get all stored block headers"""
        return list(self.block_headers.values())
    
    def sync_headers(self, peer: Any) -> List[Dict]:
        """Sync block headers from peer (mock implementation)"""
        # In real implementation, this would communicate with a peer
        synced = []
        start_height = self.current_block_height + 1
        
        for height in range(start_height, start_height + 10):  # Sync 10 headers
            header = BlockHeader(
                index=height,
                previous_hash=self.block_headers.get(height - 1).hash if height > 0 else '0' * 64,
                tx_root='0' * 64,
                state_root='0' * 64,
                receipt_root='0' * 64,
                validator=f'validator{height % 5}',
                timestamp=time.time() + height * 10,
                hash=self._calculate_header_hash(BlockHeader(
                    index=height,
                    previous_hash=self.block_headers.get(height - 1).hash if height > 0 else '0' * 64,
                    tx_root='0' * 64,
                    state_root='0' * 64,
                    receipt_root='0' * 64,
                    validator=f'validator{height % 5}',
                    timestamp=time.time() + height * 10,
                    hash=''
                ))
            )
            
            synced.append(self.add_block_header(header))
        
        return synced
    
    def validate_chain(self, start_height: int = 0, end_height: int = None) -> Dict:
        """Validate block chain from start to end height"""
        end_height = end_height or self.current_block_height
        errors = []
        
        for height in range(start_height, end_height + 1):
            if height not in self.block_headers:
                errors.append(f"Block header missing: {height}")
                continue
            
            header = self.block_headers[height]
            verification = self.verify_block_header(header)
            if not verification['isValid']:
                errors.extend([f"Block {height}: {err}" for err in verification['errors']])
        
        return {
            'isValid': len(errors) == 0,
            'errors': errors,
            'blocksChecked': end_height - start_height + 1
        }
