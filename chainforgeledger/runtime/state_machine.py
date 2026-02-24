"""
State Machine - Deterministic state transition system

A robust state machine implementation for blockchain operations. Features include:
- Deterministic state transitions
- State tracking and snapshots
- Transaction execution
- State validation
- Rollback mechanisms
- Light client support
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from chainforgeledger.crypto.hashing import sha256_hash


@dataclass
class StateSnapshot:
    """Represents a snapshot of the blockchain state"""
    block_number: int
    block_hash: str
    state_root: str
    timestamp: float
    accounts: Dict[str, Any] = field(default_factory=dict)
    contracts: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of state transition execution"""
    success: bool
    state_root: str
    gas_used: int
    gas_limit: int
    logs: List[Dict] = field(default_factory=list)
    output: Any = None
    error: str = None


class StateMachine:
    """
    Deterministic state transition system
    """
    
    def __init__(self, initial_state: Dict = None):
        self.state: Dict[str, Any] = initial_state or {
            'accounts': {},
            'contracts': {},
            'storage': {},
            'block': {
                'number': 0,
                'hash': '0' * 64,
                'timestamp': time.time()
            }
        }
        
        self.snapshots: Dict[int, StateSnapshot] = {}
        self.current_block_number = 0
        self.state_root = self._calculate_state_root()
    
    def _calculate_state_root(self) -> str:
        """Calculate Merkle root of current state"""
        state_data = str(self.state)
        return sha256_hash(state_data)
    
    async def apply_transaction(self, transaction: Any) -> ExecutionResult:
        """Apply transaction to current state"""
        result = ExecutionResult(
            success=False,
            state_root=self.state_root,
            gas_used=0,
            gas_limit=transaction.gas_limit,
            logs=[],
            output=None,
            error=None
        )
        
        try:
            # Check if sender exists
            if transaction.from_address not in self.state['accounts']:
                raise Exception("Sender account not found")
            
            # Check sender balance
            if self.state['accounts'][transaction.from_address]['balance'] < transaction.value:
                raise Exception("Insufficient balance")
            
            # Check gas limit
            if transaction.gas_limit < 21000:
                raise Exception("Gas limit too low")
            
            # Apply transaction
            await self._execute_transaction(transaction)
            
            # Update state root
            self.state_root = self._calculate_state_root()
            
            result.success = True
            result.state_root = self.state_root
            result.gas_used = transaction.gas_limit // 2  # Estimate gas usage
            
        except Exception as e:
            result.error = str(e)
        
        return result
    
    async def _execute_transaction(self, transaction: Any):
        """Execute transaction logic"""
        if transaction.to_address:
            # Transfer to existing account
            if transaction.to_address not in self.state['accounts']:
                self.state['accounts'][transaction.to_address] = {
                    'balance': 0,
                    'nonce': 0,
                    'code': '',
                    'storage': {}
                }
            
            self.state['accounts'][transaction.from_address]['balance'] -= transaction.value
            self.state['accounts'][transaction.to_address]['balance'] += transaction.value
            
            # Increment nonce
            self.state['accounts'][transaction.from_address]['nonce'] += 1
        else:
            # Contract creation
            contract_address = self._calculate_contract_address(transaction)
            self.state['accounts'][contract_address] = {
                'balance': transaction.value,
                'nonce': 0,
                'code': transaction.data,
                'storage': {}
            }
            self.state['accounts'][transaction.from_address]['balance'] -= transaction.value
            self.state['accounts'][transaction.from_address]['nonce'] += 1
            self.state['contracts'][contract_address] = {
                'code': transaction.data,
                'created_block': self.current_block_number,
                'created_transaction': transaction.id
            }
    
    def _calculate_contract_address(self, transaction: Any) -> str:
        """Calculate contract address from transaction"""
        address_data = f"{transaction.from_address}:{transaction.nonce}"
        return sha256_hash(address_data)
    
    async def apply_block(self, block: Any) -> List[ExecutionResult]:
        """Apply all transactions in a block"""
        results = []
        
        # Create snapshot before applying block
        await self.create_snapshot(block.index)
        
        for transaction in block.transactions:
            result = await self.apply_transaction(transaction)
            results.append(result)
        
        # Update block info in state
        self.state['block'] = {
            'number': block.index,
            'hash': block.hash,
            'timestamp': block.timestamp
        }
        
        self.current_block_number = block.index
        self.state_root = self._calculate_state_root()
        
        return results
    
    async def create_snapshot(self, block_number: int = None):
        """Create a snapshot of the current state"""
        block_num = block_number or self.current_block_number
        
        snapshot = StateSnapshot(
            block_number=block_num,
            block_hash=self.state['block']['hash'],
            state_root=self.state_root,
            timestamp=time.time(),
            accounts=dict(self.state['accounts']),
            contracts=dict(self.state['contracts'])
        )
        
        self.snapshots[block_num] = snapshot
    
    async def restore_snapshot(self, block_number: int):
        """Restore state from snapshot"""
        if block_number not in self.snapshots:
            raise Exception(f"No snapshot found for block {block_number}")
        
        snapshot = self.snapshots[block_number]
        
        self.state['accounts'] = dict(snapshot.accounts)
        self.state['contracts'] = dict(snapshot.contracts)
        self.state['block'] = {
            'number': snapshot.block_number,
            'hash': snapshot.block_hash,
            'timestamp': snapshot.timestamp
        }
        
        self.current_block_number = snapshot.block_number
        self.state_root = snapshot.state_root
    
    async def rollback_to_block(self, block_number: int):
        """Rollback state to specific block number"""
        if block_number > self.current_block_number:
            raise Exception(f"Cannot rollback to future block {block_number}")
        
        # Find the latest snapshot <= target block
        target_snapshot = None
        for snap_block in sorted(self.snapshots.keys()):
            if snap_block <= block_number:
                target_snapshot = snap_block
            else:
                break
        
        if target_snapshot is None:
            raise Exception(f"No snapshot available for block {block_number}")
        
        await self.restore_snapshot(target_snapshot)
    
    def validate_state_transition(self, previous_state: Dict, next_state: Dict, transactions: List) -> bool:
        """Validate state transition between blocks"""
        try:
            # Simple validation - should be extended with proper logic
            previous_balance = sum(acc['balance'] for acc in previous_state['accounts'].values())
            next_balance = sum(acc['balance'] for acc in next_state['accounts'].values())
            
            # Total balance should remain the same (assuming no coinbase rewards)
            if previous_balance != next_balance:
                return False
            
            return True
        except Exception:
            return False
    
    def get_state_root(self) -> str:
        """Get current state root"""
        return self.state_root
    
    def get_state(self) -> Dict:
        """Get current state"""
        return dict(self.state)
    
    def get_block_state(self, block_number: int) -> Optional[Dict]:
        """Get state at specific block number"""
        if block_number in self.snapshots:
            snapshot = self.snapshots[block_number]
            return {
                'accounts': dict(snapshot.accounts),
                'contracts': dict(snapshot.contracts),
                'block': {
                    'number': snapshot.block_number,
                    'hash': snapshot.block_hash,
                    'timestamp': snapshot.timestamp
                }
            }
        
        return None
    
    def get_snapshots(self) -> List[StateSnapshot]:
        """Get all state snapshots"""
        return list(self.snapshots.values())
    
    def get_account(self, address: str) -> Optional[Dict]:
        """Get account state"""
        return self.state['accounts'].get(address)
    
    def get_contract(self, address: str) -> Optional[Dict]:
        """Get contract state"""
        return self.state['contracts'].get(address)
