"""
Finality Logic - Research-level finality mechanisms

Comprehensive finality system supporting multiple finality mechanisms.
Features:
- Proof-of-Stake finality with checkpoints
- BFT-based finality (PBFT, Tendermint-like)
- GHOST-based finality
- LMD-GHOST (Latest Message Driven GHOST)
- Justified and finalized checkpoints
- Fork choice rules
- Finality gadgets
- Slashing conditions for finality
"""

import time
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class Checkpoint:
    """Represents a checkpoint block with finality information"""
    block_number: int
    block_hash: str
    epoch: int
    timestamp: float
    validator_set: List[Any] = field(default_factory=list)
    votes: Dict[str, Any] = field(default_factory=dict)
    justification: Optional[Dict] = None
    finalized: bool = False
    difficulty: int = 0


@dataclass
class Vote:
    """Represents a validator vote for a block"""
    block_number: int
    validator_id: str
    signature: str
    timestamp: float = field(default_factory=lambda: time.time())


class FinalityManager:
    """
    Manages finality mechanisms for blockchain consensus
    """
    
    def __init__(self, options: Dict = None):
        options = options or {}
        self.chain_id = options.get('chainId', 'default')
        self.validators = options.get('validators', [])
        self.min_validators = options.get('minValidators', 4)
        self.committee_size = options.get('committeeSize', 100)
        self.finality_threshold = options.get('finalityThreshold', 0.67)  # 67% quorum
        self.justification_threshold = options.get('justificationThreshold', 0.5)  # 50% quorum
        self.checkpoint_interval = options.get('checkpointInterval', 32)  # blocks per checkpoint
        
        self.checkpoints: Dict[int, Checkpoint] = {}
        self.justified_checkpoint: Optional[Checkpoint] = None
        self.finalized_checkpoint: Optional[Checkpoint] = None
        self.validator_signatures: Dict[str, Any] = {}
        self.block_votes: Dict[int, Dict[str, Vote]] = {}
        self.fork_choices: Dict[str, Any] = {}
        
        self.fork_choice_algorithm = options.get('forkChoiceAlgorithm', 'LMD-GHOST')
        self.finality_gadget = options.get('finalityGadget', 'Casper FFG')
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize finality manager"""
        self.initialized = True
        await self.create_initial_checkpoint()
    
    async def create_initial_checkpoint(self):
        """Create initial genesis checkpoint"""
        genesis_checkpoint = Checkpoint(
            block_number=0,
            block_hash='0' * 64,
            epoch=0,
            timestamp=time.time(),
            validator_set=[],
            votes={},
            justification=None,
            finalized=True,
            difficulty=0
        )
        
        self.checkpoints[0] = genesis_checkpoint
        self.finalized_checkpoint = genesis_checkpoint
        self.justified_checkpoint = genesis_checkpoint
    
    def add_validator(self, validator):
        """Add validator to finality system"""
        self.validators.append(validator)
    
    def remove_validator(self, validator_id: str):
        """Remove validator from finality system"""
        self.validators = [v for v in self.validators if getattr(v, 'id', None) != validator_id]
    
    def get_validators(self):
        """Get current validator set"""
        return list(self.validators)
    
    async def create_checkpoint(self, block):
        """Create new checkpoint"""
        epoch = block.index // self.checkpoint_interval
        checkpoint = Checkpoint(
            block_number=block.index,
            block_hash=block.hash,
            epoch=epoch,
            timestamp=block.timestamp,
            validator_set=list(self.validators),
            votes={},
            justification=None,
            finalized=False,
            difficulty=block.difficulty
        )
        
        self.checkpoints[block.index] = checkpoint
        self.block_votes[block.index] = {}
        
        return checkpoint
    
    def should_checkpoint(self, block_number: int) -> bool:
        """Check if block should be checkpointed"""
        return block_number > 0 and block_number % self.checkpoint_interval == 0
    
    async def record_vote(self, vote: Vote):
        """Record validator vote for block"""
        if vote.block_number not in self.block_votes:
            self.block_votes[vote.block_number] = {}
        
        self.block_votes[vote.block_number][vote.validator_id] = vote
        
        await self.process_votes(vote.block_number)
    
    async def process_votes(self, block_number: int):
        """Process votes for block"""
        if block_number not in self.block_votes:
            return
        
        # Get checkpoint block
        if self.should_checkpoint(block_number):
            await self.attempt_checkpoint_justification(block_number)
        
        # Attempt finality for justified checkpoints
        if (self.justified_checkpoint and 
            self.justified_checkpoint.block_number > self.finalized_checkpoint.block_number):
            await self.attempt_finality()
    
    async def attempt_checkpoint_justification(self, block_number: int):
        """Attempt to justify checkpoint"""
        if block_number not in self.block_votes:
            return None
        
        votes = self.block_votes[block_number]
        total_validators = len(self.validators)
        required_votes = int(total_validators * self.justification_threshold) + 1
        
        if len(votes) >= required_votes:
            if block_number in self.checkpoints:
                checkpoint = self.checkpoints[block_number]
                checkpoint.justification = {
                    'votes': list(votes.values()),
                    'signatureCount': len(votes),
                    'thresholdMet': True,
                    'timestamp': time.time()
                }
                
                self.justified_checkpoint = checkpoint
                return checkpoint
        
        return None
    
    async def attempt_finality(self):
        """Attempt to finalize checkpoint"""
        # For PBFT-style finality
        if self.finality_gadget == 'PBFT':
            return await self.attempt_pbft_finality()
        
        # For Casper FFG-style finality
        if self.finality_gadget == 'Casper FFG':
            return await self.attempt_casper_ffg_finality()
        
        # Default finality via LMD-GHOST
        return await self.attempt_lmd_finality()
    
    async def attempt_pbft_finality(self):
        """Attempt PBFT-style finality"""
        current_height = self.justified_checkpoint.block_number
        if current_height not in self.block_votes:
            return None
        
        votes = self.block_votes[current_height]
        
        if len(votes) >= self.required_finality_votes():
            checkpoint = self.justified_checkpoint
            checkpoint.finalized = True
            self.finalized_checkpoint = checkpoint
            
            return checkpoint
        
        return None
    
    async def attempt_casper_ffg_finality(self):
        """Attempt Casper FFG-style finality"""
        current_epoch = self.justified_checkpoint.epoch
        previous_checkpoint = self.get_checkpoint_by_epoch(current_epoch - 1)
        
        if (previous_checkpoint and previous_checkpoint.justification and 
            not previous_checkpoint.finalized):
            
            previous_votes = self.block_votes.get(previous_checkpoint.block_number, {})
            current_votes = self.block_votes.get(self.justified_checkpoint.block_number, {})
            
            if (len(previous_votes) >= self.required_finality_votes() and
                len(current_votes) >= self.required_finality_votes()):
                
                previous_checkpoint.finalized = True
                self.finalized_checkpoint = previous_checkpoint
                
                return previous_checkpoint
        
        return None
    
    async def attempt_lmd_finality(self):
        """Attempt LMD-GHOST finality"""
        latest_justified = self.justified_checkpoint
        latest_block = await self.get_latest_block_by_chain(latest_justified.block_number)
        
        if (latest_block and 
            latest_block.index - self.finalized_checkpoint.block_number > self.checkpoint_interval):
            
            votes = self.block_votes.get(latest_block.index, {})
            
            if len(votes) >= self.required_finality_votes():
                latest_justified.finalized = True
                self.finalized_checkpoint = latest_justified
                
                return latest_justified
        
        return None
    
    def get_checkpoint_by_epoch(self, epoch: int):
        """Get checkpoint by epoch"""
        block_number = epoch * self.checkpoint_interval
        return self.checkpoints.get(block_number, None)
    
    async def get_latest_block_by_chain(self, checkpoint_number: int):
        """Get latest block in chain starting from checkpoint"""
        # In real implementation, this would traverse blockchain from checkpoint
        return None
    
    def required_finality_votes(self):
        """Calculate required votes for finality"""
        return int(len(self.validators) * self.finality_threshold) + 1
    
    def apply_fork_choice(self, chains: List[Dict]) -> Optional[Dict]:
        """Apply fork choice rule to select chain"""
        if not chains:
            return None
        
        if self.fork_choice_algorithm == 'LMD-GHOST':
            return self.lmd_ghost_fork_choice(chains)
        elif self.fork_choice_algorithm == 'GHOST':
            return self.ghost_fork_choice(chains)
        elif self.fork_choice_algorithm == 'LongestChain':
            return self.longest_chain_fork_choice(chains)
        else:
            return self.lmd_ghost_fork_choice(chains)
    
    def lmd_ghost_fork_choice(self, chains: List[Dict]) -> Optional[Dict]:
        """LMD-GHOST fork choice rule - selects chain with most recent votes"""
        chains_with_votes = []
        
        for chain in chains:
            latest_block = chain['blocks'][-1]
            votes = self.block_votes.get(latest_block.index, {})
            
            chains_with_votes.append({
                **chain,
                'voteCount': len(votes),
                'latestTimestamp': latest_block.timestamp
            })
        
        best_chain = None
        for chain in chains_with_votes:
            if not best_chain or chain['voteCount'] > best_chain['voteCount']:
                best_chain = chain
            elif chain['voteCount'] == best_chain['voteCount']:
                if chain['latestTimestamp'] > best_chain['latestTimestamp']:
                    best_chain = chain
        
        return best_chain
    
    def ghost_fork_choice(self, chains: List[Dict]) -> Optional[Dict]:
        """GHOST fork choice rule - selects chain with most blocks since fork"""
        best_chain = None
        for chain in chains:
            if not best_chain or len(chain['blocks']) > len(best_chain['blocks']):
                best_chain = chain
            elif len(chain['blocks']) == len(best_chain['blocks']):
                current_difficulty = sum(block.difficulty for block in chain['blocks'])
                best_difficulty = sum(block.difficulty for block in best_chain['blocks'])
                if current_difficulty > best_difficulty:
                    best_chain = chain
        
        return best_chain
    
    def longest_chain_fork_choice(self, chains: List[Dict]) -> Optional[Dict]:
        """Longest chain fork choice rule"""
        best_chain = None
        for chain in chains:
            if not best_chain or len(chain['blocks']) > len(best_chain['blocks']):
                best_chain = chain
        
        return best_chain
    
    def get_finalized_block(self) -> Optional[Checkpoint]:
        """Get finalized block"""
        return self.finalized_checkpoint
    
    def get_justified_block(self) -> Optional[Checkpoint]:
        """Get justified block"""
        return self.justified_checkpoint
    
    def get_checkpoints(self, options: Dict = None) -> List[Checkpoint]:
        """Get checkpoints"""
        options = options or {}
        checkpoints = list(self.checkpoints.values())
        
        if 'epoch' in options:
            checkpoints = [cp for cp in checkpoints if cp.epoch == options['epoch']]
        
        if 'finalized' in options and options['finalized']:
            checkpoints = [cp for cp in checkpoints if cp.finalized]
        
        if 'justified' in options and options['justified']:
            checkpoints = [cp for cp in checkpoints if cp.justification]
        
        return sorted(checkpoints, key=lambda x: x.block_number)
    
    def verify_finality(self, block_number: int) -> Dict:
        """Verify finality of block"""
        is_finalized = (self.finalized_checkpoint and 
                       block_number <= self.finalized_checkpoint.block_number)
        is_justified = (self.justified_checkpoint and 
                      block_number <= self.justified_checkpoint.block_number)
        
        status = 'unjustified'
        if is_finalized:
            status = 'finalized'
        elif is_justified:
            status = 'justified'
        
        return {
            'blockNumber': block_number,
            'status': status,
            'isFinalized': is_finalized,
            'isJustified': is_justified,
            'finalizedBlock': self.finalized_checkpoint.block_number if self.finalized_checkpoint else None,
            'justifiedBlock': self.justified_checkpoint.block_number if self.justified_checkpoint else None
        }
    
    async def slash_validator(self, validator_id: str, violation: Dict) -> Optional[Dict]:
        """Slash validator for finality violations"""
        validator = next((v for v in self.validators if getattr(v, 'id', None) == validator_id), None)
        if validator:
            # Apply slashing penalty
            validator.slashing_count = getattr(validator, 'slashing_count', 0) + 1
            validator.stake = max(0, validator.stake * 0.5)  # 50% slashing penalty
            
            return {
                'validatorId': validator_id,
                'violation': violation,
                'slashingAmount': validator.stake,
                'newStake': validator.stake,
                'timestamp': time.time()
            }
        
        return None
    
    async def handle_fork(self, fork_block: Any, competing_chains: List[Dict]) -> Optional[Dict]:
        """Handle fork in blockchain"""
        selected_chain = self.apply_fork_choice(competing_chains)
        
        if selected_chain:
            # Log fork resolution
            return selected_chain
        
        return None
