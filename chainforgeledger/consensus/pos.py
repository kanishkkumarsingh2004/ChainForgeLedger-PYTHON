"""
ChainForgeLedger Proof of Stake Consensus

Proof of Stake consensus mechanism implementation.
"""

from typing import Optional
from chainforgeledger.core.block import Block
from chainforgeledger.core.blockchain import Blockchain
from chainforgeledger.core.transaction import Transaction
from chainforgeledger.consensus.validator import ValidatorManager, Validator


class ProofOfStake:
    """
    Proof of Stake consensus mechanism.
    
    Attributes:
        blockchain: Blockchain instance
        validator_manager: Validator manager
        reward: Block reward
    """
    
    def __init__(
        self,
        blockchain: Blockchain,
        validator_manager: ValidatorManager,
        reward: float = 50.0
    ):
        """
        Initialize a new ProofOfStake instance.
        
        Args:
            blockchain: Blockchain instance
            validator_manager: Validator manager
            reward: Block reward for validators
        """
        self.blockchain = blockchain
        self.validator_manager = validator_manager
        self.reward = reward
    
    def forge_block(self, transactions: list) -> Optional[Block]:
        """
        Forge a new block.
        
        Args:
            transactions: List of transactions to include
            
        Returns:
            Forged block or None if no active validators
        """
        # Select validator
        validator = self.validator_manager.select_validator()
        
        if not validator:
            return None
        
        previous_block = self.blockchain.get_last_block()
        index = previous_block.index + 1
        previous_hash = previous_block.hash
        
        # Add staking reward transaction
        staking_reward = Transaction(
            sender="0",
            receiver=validator.address,
            amount=self.reward
        )
        transactions.append(staking_reward.to_dict())
        
        # Create block
        block = Block(
            index=index,
            previous_hash=previous_hash,
            transactions=transactions,
            validator=validator.address
        )
        
        return block
    
    def validate_block(self, block: Block) -> bool:
        """
        Validate a block against PoS requirements.
        
        Args:
            block: Block to validate
            
        Returns:
            True if valid
        """
        # Check validator exists and is active
        validator = self.validator_manager.get_validator(block.validator)
        
        if not validator or not validator.is_active():
            return False
        
        # Validate block structure
        if not self.blockchain.is_valid_block(block):
            return False
            
        # Check staking reward
        staking_rewards = [
            tx for tx in block.transactions
            if isinstance(tx, dict) and tx.get("sender") == "0"
        ]
        
        if len(staking_rewards) != 1:
            return False
            
        if staking_rewards[0].get("amount") != self.reward:
            return False
        
        return True
    
    def update_validator_rewards(self, validator: Validator, block: Block):
        """
        Update validator rewards and reputation.
        
        Args:
            validator: Validator to update
            block: Block produced by validator
        """
        validator.update_stake(self.reward)
        validator.produce_block()
    
    def punish_validator(self, validator: Validator, reason: str, amount: float):
        """
        Punish a validator for misbehavior.
        
        Args:
            validator: Validator to punish
            reason: Reason for punishment
            amount: Amount to slash
        """
        validator.update_stake(-amount)
        validator.decrease_reputation(0.5)
        
        if validator.stake <= 0:
            validator.mark_inactive()
    
    def get_consensus_statistics(self) -> dict:
        """
        Get consensus statistics.
        
        Returns:
            Dictionary with consensus statistics
        """
        return {
            "total_validators": len(self.validator_manager.validators),
            "active_validators": len(self.validator_manager.get_active_validators()),
            "total_stake": self.validator_manager.get_total_stake(),
            "block_reward": self.reward,
            "chain_length": len(self.blockchain.chain)
        }
    
    def __repr__(self):
        """String representation of PoS consensus."""
        return (
            f"ProofOfStake(validators={len(self.validator_manager.validators)}, "
            f"total_stake={self.validator_manager.get_total_stake():,.2f})"
        )
    
    def __str__(self):
        """String representation for printing."""
        stats = self.get_consensus_statistics()
        return (
            f"Proof of Stake Consensus\n"
            f"=======================\n"
            f"Total Validators: {stats['total_validators']}\n"
            f"Active Validators: {stats['active_validators']}\n"
            f"Total Stake: {stats['total_stake']:.2f}\n"
            f"Block Reward: {stats['block_reward']}\n"
            f"Chain Length: {stats['chain_length']}"
        )
