"""
ChainForgeLedger Voting System Module

Voting system implementation for blockchain governance.
"""

import time
from typing import Dict, List, Optional
from chainforgeledger.utils.logger import get_logger
from chainforgeledger.governance.proposal import Proposal


class VotingSystem:
    """
    Voting system for blockchain governance.
    
    Handles voting process, vote counting, and governance logic.
    """
    
    def __init__(self):
        """Initialize voting system."""
        self.proposals = []
        self._proposals_dict = {}  # For O(1) proposal lookups
        self.vote_registry = {}
        self.total_staking_power = 0
        self.voting_power_by_address = {}
        self.logger = get_logger(__name__)
    
    def create_proposal(self, **kwargs) -> Proposal:
        """
        Create a new governance proposal.
        
        Args:
            **kwargs: Proposal attributes
            
        Returns:
            Created proposal instance
        """
        try:
            proposal = Proposal(**kwargs)
            
            if not proposal.validate():
                raise ValueError("Invalid proposal parameters")
            
            self.proposals.append(proposal)
            # Update the proposals dictionary for O(1) lookups
            if hasattr(self, '_proposals_dict'):
                self._proposals_dict[proposal.proposal_id] = proposal
            self.vote_registry[proposal.proposal_id] = {}
            
            self.logger.info(f"Proposal created: {proposal.proposal_id}")
            return proposal
            
        except Exception as e:
            self.logger.error(f"Failed to create proposal: {e}")
            raise
    
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """
        Get proposal by ID.
        
        Args:
            proposal_id: Proposal ID
            
        Returns:
            Proposal instance or None if not found
        """
        # Convert proposals list to dict for O(1) lookups if not already done
        if not hasattr(self, '_proposals_dict'):
            self._proposals_dict = {p.proposal_id: p for p in self.proposals}
        
        try:
            proposal = self._proposals_dict.get(proposal_id)
            if not proposal:
                self.logger.warning(f"Proposal not found: {proposal_id}")
            return proposal
            
        except Exception as e:
            self.logger.error(f"Failed to get proposal: {e}")
            return None
    
    def get_proposals(self, state: str = None, proposal_type: str = None) -> List[Proposal]:
        """
        Get all proposals.
        
        Args:
            state: Optional state filter
            proposal_type: Optional type filter
            
        Returns:
            List of proposals
        """
        try:
            filtered_proposals = self.proposals
            
            if state:
                filtered_proposals = [p for p in filtered_proposals if p.state == state]
            
            if proposal_type:
                filtered_proposals = [p for p in filtered_proposals if p.proposal_type == proposal_type]
            
            return filtered_proposals
            
        except Exception as e:
            self.logger.error(f"Failed to get proposals: {e}")
            return []
    
    def activate_proposal(self, proposal_id: str, voting_duration: int = 86400):
        """
        Activate proposal for voting.
        
        Args:
            proposal_id: Proposal ID
            voting_duration: Voting duration in seconds
        """
        try:
            proposal = self.get_proposal(proposal_id)
            
            if proposal:
                proposal.activate(voting_duration)
                self.logger.info(f"Proposal activated: {proposal_id}")
            else:
                raise ValueError(f"Proposal not found: {proposal_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to activate proposal: {e}")
            raise
    
    def deactivate_proposal(self, proposal_id: str):
        """
        Deactivate proposal.
        
        Args:
            proposal_id: Proposal ID
        """
        try:
            proposal = self.get_proposal(proposal_id)
            
            if proposal:
                proposal.deactivate()
                self.logger.info(f"Proposal deactivated: {proposal_id}")
            else:
                raise ValueError(f"Proposal not found: {proposal_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to deactivate proposal: {e}")
            raise
    
    def finalize_proposal(self, proposal_id: str):
        """
        Finalize proposal after voting period ends.
        
        Args:
            proposal_id: Proposal ID
        """
        try:
            proposal = self.get_proposal(proposal_id)
            
            if proposal:
                proposal.finalize(self.total_staking_power)
                self.logger.info(f"Proposal finalized: {proposal_id}")
            else:
                raise ValueError(f"Proposal not found: {proposal_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to finalize proposal: {e}")
            raise
    
    def execute_proposal(self, proposal_id: str):
        """
        Execute passed proposal.
        
        Args:
            proposal_id: Proposal ID
        """
        try:
            proposal = self.get_proposal(proposal_id)
            
            if proposal:
                proposal.execute()
                self.logger.info(f"Proposal executed: {proposal_id}")
            else:
                raise ValueError(f"Proposal not found: {proposal_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to execute proposal: {e}")
            raise
    
    def cast_vote(self, proposal_id: str, voter_address: str, vote: str, voting_power: float):
        """
        Cast a vote on a proposal.
        
        Args:
            proposal_id: Proposal ID
            voter_address: Voter address
            vote: Vote choice (yes/no/abstain)
            voting_power: Voter's voting power
        """
        try:
            proposal = self.get_proposal(proposal_id)
            
            if not proposal:
                raise ValueError(f"Proposal not found: {proposal_id}")
            
            # Validate vote choice
            valid_votes = ["yes", "no", "abstain"]
            if vote.lower() not in valid_votes:
                raise ValueError(f"Invalid vote choice: {vote}")
            
            # Validate voter has voting power
            if voter_address not in self.voting_power_by_address:
                raise ValueError(f"Voter {voter_address} has no voting power")
            
            if self.voting_power_by_address[voter_address] != voting_power:
                raise ValueError(f"Voting power mismatch for {voter_address}")
            
            # Check if voter has already voted
            if proposal_id in self.vote_registry and voter_address in self.vote_registry[proposal_id]:
                raise ValueError(f"Voter {voter_address} has already voted on proposal {proposal_id}")
            
            # Cast the vote
            proposal.add_vote(voter_address, vote, voting_power)
            
            # Update vote registry
            if proposal_id not in self.vote_registry:
                self.vote_registry[proposal_id] = {}
            
            self.vote_registry[proposal_id][voter_address] = vote
            
            self.logger.info(f"Vote cast: {voter_address} voted {vote} on proposal {proposal_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to cast vote: {e}")
            raise
    
    def get_vote_info(self, proposal_id: str, voter_address: str) -> Optional[Dict]:
        """
        Get vote information for a specific voter on a proposal.
        
        Args:
            proposal_id: Proposal ID
            voter_address: Voter address
            
        Returns:
            Vote information or None
        """
        try:
            if proposal_id in self.vote_registry and voter_address in self.vote_registry[proposal_id]:
                vote = self.vote_registry[proposal_id][voter_address]
                
                return {
                    "proposal_id": proposal_id,
                    "voter_address": voter_address,
                    "vote": vote
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get vote info: {e}")
            return None
    
    def get_voter_proposals(self, voter_address: str) -> List[Dict]:
        """
        Get all proposals voted on by a specific address.
        
        Args:
            voter_address: Voter address
            
        Returns:
            List of proposals with vote information
        """
        try:
            voter_proposals = []
            
            for proposal_id, votes in self.vote_registry.items():
                if voter_address in votes:
                    proposal = self.get_proposal(proposal_id)
                    if proposal:
                        voter_proposals.append({
                            "proposal_id": proposal_id,
                            "title": proposal.title,
                            "vote": votes[voter_address],
                            "state": proposal.state
                        })
            
            return voter_proposals
            
        except Exception as e:
            self.logger.error(f"Failed to get voter proposals: {e}")
            return []
    
    def update_staking_power(self, address: str, power: float):
        """
        Update staking power for an address.
        
        Args:
            address: Address
            power: New staking power
        """
        try:
            if power < 0:
                raise ValueError("Staking power cannot be negative")
            
            old_power = self.voting_power_by_address.get(address, 0)
            self.voting_power_by_address[address] = power
            self.total_staking_power += (power - old_power)
            
            self.logger.debug(f"Staking power updated for {address}: {power}")
            
        except Exception as e:
            self.logger.error(f"Failed to update staking power: {e}")
            raise
    
    def remove_staking_power(self, address: str):
        """
        Remove staking power for an address.
        
        Args:
            address: Address
        """
        try:
            if address in self.voting_power_by_address:
                self.total_staking_power -= self.voting_power_by_address[address]
                del self.voting_power_by_address[address]
                
                self.logger.debug(f"Staking power removed for {address}")
            
        except Exception as e:
            self.logger.error(f"Failed to remove staking power: {e}")
            raise
    
    def get_voting_power_distribution(self) -> Dict:
        """
        Get voting power distribution.
        
        Returns:
            Voting power distribution dictionary
        """
        try:
            return self.voting_power_by_address.copy()
            
        except Exception as e:
            self.logger.error(f"Failed to get voting power distribution: {e}")
            return {}
    
    def calculate_vote_weight(self, proposal_id: str, voter_address: str) -> float:
        """
        Calculate vote weight for a specific voter on a proposal.
        
        Args:
            proposal_id: Proposal ID
            voter_address: Voter address
            
        Returns:
            Vote weight
        """
        try:
            return self.voting_power_by_address.get(voter_address, 0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate vote weight: {e}")
            return 0
    
    def get_vote_summary(self, proposal_id: str) -> Dict:
        """
        Get vote summary for a proposal.
        
        Args:
            proposal_id: Proposal ID
            
        Returns:
            Vote summary dictionary
        """
        try:
            proposal = self.get_proposal(proposal_id)
            
            if not proposal:
                raise ValueError(f"Proposal not found: {proposal_id}")
            
            vote_count = proposal.get_vote_count()
            vote_percentages = proposal.get_vote_percentage()
            
            return {
                "proposal_id": proposal_id,
                "title": proposal.title,
                "state": proposal.state,
                "votes": vote_count,
                "percentages": vote_percentages,
                "quorum_reached": proposal.has_reached_quorum(self.total_staking_power),
                "passing": proposal.is_passing(self.total_staking_power)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get vote summary: {e}")
            return {}
    
    def get_proposal_stats(self) -> Dict:
        """
        Get proposal statistics.
        
        Returns:
            Proposal statistics dictionary
        """
        try:
            state_counts = {}
            type_counts = {}
            
            for proposal in self.proposals:
                state_counts[proposal.state] = state_counts.get(proposal.state, 0) + 1
                type_counts[proposal.proposal_type] = type_counts.get(proposal.proposal_type, 0)
            
            return {
                "total": len(self.proposals),
                "states": state_counts,
                "types": type_counts
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get proposal stats: {e}")
            return {}
    
    def get_vote_stats(self) -> Dict:
        """
        Get vote statistics.
        
        Returns:
            Vote statistics dictionary
        """
        try:
            total_votes = 0
            proposal_votes = {}
            
            for proposal in self.proposals:
                count = proposal.get_vote_count()
                total_votes += count["total"]
                proposal_votes[proposal.proposal_id] = count
            
            return {
                "total_votes": total_votes,
                "per_proposal": proposal_votes,
                "active_voters": len(set().union(*[v.keys() for v in self.vote_registry.values()]))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get vote stats: {e}")
            return {}
    
    def sync_with_blockchain(self, block_height: int):
        """
        Sync voting system with blockchain.
        
        Args:
            block_height: Current block height
        """
        try:
            # Check for proposals that need to be finalized
            for proposal in self.get_proposals(state="active"):
                if proposal.voting_end_time < time.time():
                    self.finalize_proposal(proposal.proposal_id)
            
            self.logger.debug(f"Voting system synced to block height: {block_height}")
            
        except Exception as e:
            self.logger.error(f"Failed to sync with blockchain: {e}")
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            Voting system as dictionary
        """
        try:
            return {
                "proposals": [p.to_dict() for p in self.proposals],
                "vote_registry": self.vote_registry,
                "total_staking_power": self.total_staking_power,
                "voting_power_by_address": self.voting_power_by_address
            }
            
        except Exception as e:
            self.logger.error(f"Failed to convert to dict: {e}")
            return {}
    
    def from_dict(self, data: Dict):
        """
        Load from dictionary.
        
        Args:
            data: Voting system data
        """
        try:
            self.proposals = []
            for proposal_data in data.get("proposals", []):
                proposal = Proposal.from_dict(proposal_data)
                self.proposals.append(proposal)
            
            self.vote_registry = data.get("vote_registry", {})
            self.total_staking_power = data.get("total_staking_power", 0)
            self.voting_power_by_address = data.get("voting_power_by_address", {})
            
            self.logger.debug("Voting system loaded from dict")
            
        except Exception as e:
            self.logger.error(f"Failed to load from dict: {e}")
            raise
    
    def __repr__(self):
        """String representation."""
        stats = self.get_proposal_stats()
        return f"VotingSystem(proposals={stats['total']}, active={stats['states'].get('active', 0)})"
    
    def __str__(self):
        """String representation for printing."""
        stats = self.get_proposal_stats()
        
        return (
            f"Voting System\n"
            f"=============\n"
            f"Total Proposals: {stats['total']}\n"
            f"Active Proposals: {stats['states'].get('active', 0)}\n"
            f"Total Voting Power: {self.total_staking_power:.0f}\n"
            f"Active Voters: {len(self.voting_power_by_address)}\n"
            f"State Distribution:\n"
            f"  Draft: {stats['states'].get('draft', 0)}\n"
            f"  Active: {stats['states'].get('active', 0)}\n"
            f"  Passed: {stats['states'].get('passed', 0)}\n"
            f"  Rejected: {stats['states'].get('rejected', 0)}\n"
            f"  Withdrawn: {stats['states'].get('withdrawn', 0)}\n"
            f"  Executed: {stats['states'].get('executed', 0)}"
        )
