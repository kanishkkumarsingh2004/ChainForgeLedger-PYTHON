"""
ChainForgeLedger Governance Proposals Module

Proposal management for blockchain governance.
"""

import time
import json
from typing import Dict
from chainforgeledger.utils.logger import get_logger
from chainforgeledger.crypto.hashing import sha256_hash


class Proposal:
    """
    Governance proposal for blockchain upgrades and changes.
    
    Represents a formal proposal that can be voted on by the community.
    """
    
    # Proposal states
    STATES = {
        "draft": "draft",
        "active": "active",
        "passed": "passed",
        "rejected": "rejected",
        "withdrawn": "withdrawn",
        "executed": "executed"
    }
    
    # Proposal types
    TYPES = {
        "upgrade": "upgrade",
        "parameter": "parameter",
        "feature": "feature",
        "policy": "policy",
        "funding": "funding",
        "other": "other"
    }
    
    def __init__(self, **kwargs):
        """
        Initialize governance proposal.
        
        Args:
            **kwargs: Proposal attributes
        """
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.proposer_address = kwargs.get('proposer_address', '')
        self.proposal_type = kwargs.get('proposal_type', self.TYPES["other"])
        self.state = kwargs.get('state', self.STATES["draft"])
        self.parameters = kwargs.get('parameters', {})
        self.voting_start_time = kwargs.get('voting_start_time', 0)
        self.voting_end_time = kwargs.get('voting_end_time', 0)
        self.quorum_required = kwargs.get('quorum_required', 0.5)
        self.approval_threshold = kwargs.get('approval_threshold', 0.66)
        self.votes = kwargs.get('votes', [])
        self.created_at = kwargs.get('created_at', self._get_current_timestamp())
        self.updated_at = kwargs.get('updated_at', self._get_current_timestamp())
        self.proposal_id = kwargs.get('proposal_id', self._generate_proposal_id())
        self.logger = get_logger(__name__)
        # Initialize the voted addresses set for O(1) lookups
        self._voted_addresses = set(v["voter_address"] for v in self.votes)
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp in seconds."""
        return time.time()
    
    def _generate_proposal_id(self) -> str:
        """Generate unique proposal ID."""
        timestamp = self._get_current_timestamp()
        unique_id = sha256_hash(f"{timestamp}-{self.title}")
        return unique_id[:16]
    
    def validate(self) -> bool:
        """
        Validate proposal structure.
        
        Returns:
            True if proposal is valid, False otherwise
        """
        validation_rules = [
            (isinstance(self.title, str) and len(self.title.strip()) > 0),
            (isinstance(self.description, str) and len(self.description.strip()) > 0),
            (isinstance(self.proposer_address, str) and len(self.proposer_address.strip()) > 0),
            (self.proposal_type in self.TYPES.values()),
            (self.state in self.STATES.values()),
            (isinstance(self.quorum_required, (int, float)) and 0 <= self.quorum_required <= 1),
            (isinstance(self.approval_threshold, (int, float)) and 0 <= self.approval_threshold <= 1)
        ]
        
        return all(validation_rules)
    
    def activate(self, voting_duration: int = 86400):
        """
        Activate proposal for voting.
        
        Args:
            voting_duration: Voting duration in seconds (default: 24 hours)
        """
        if self.state != self.STATES["draft"]:
            raise ValueError("Only draft proposals can be activated")
        
        self.state = self.STATES["active"]
        self.voting_start_time = self._get_current_timestamp()
        self.voting_end_time = self.voting_start_time + voting_duration
        self.updated_at = self._get_current_timestamp()
        
        self.logger.info(f"Proposal {self.proposal_id} activated for voting")
    
    def deactivate(self):
        """Deactivate proposal."""
        if self.state not in [self.STATES["active"], self.STATES["passed"]]:
            raise ValueError("Only active or passed proposals can be deactivated")
        
        self.state = self.STATES["rejected"]
        self.updated_at = self._get_current_timestamp()
        
        self.logger.info(f"Proposal {self.proposal_id} deactivated")
    
    def withdraw(self):
        """Withdraw proposal."""
        if self.state not in [self.STATES["draft"], self.STATES["active"]]:
            raise ValueError("Only draft or active proposals can be withdrawn")
        
        self.state = self.STATES["withdrawn"]
        self.updated_at = self._get_current_timestamp()
        
        self.logger.info(f"Proposal {self.proposal_id} withdrawn")
    
    def execute(self):
        """Execute proposal."""
        if self.state != self.STATES["passed"]:
            raise ValueError("Only passed proposals can be executed")
        
        if not self._has_reached_end_time():
            raise ValueError("Voting period has not ended yet")
        
        self.state = self.STATES["executed"]
        self.updated_at = self._get_current_timestamp()
        
        self.logger.info(f"Proposal {self.proposal_id} executed")
    
    def add_vote(self, voter_address: str, vote: str, voting_power: float):
        """
        Add vote to proposal.
        
        Args:
            voter_address: Voter address
            vote: Vote choice (yes/no/abstain)
            voting_power: Voter's voting power
        """
        if self.state != self.STATES["active"]:
            raise ValueError("Only active proposals accept votes")
        
        if self._has_reached_end_time():
            raise ValueError("Voting period has ended")
        
        # Check if voter already voted (O(1) lookup using set)
        if not hasattr(self, '_voted_addresses'):
            self._voted_addresses = set(v["voter_address"] for v in self.votes)
        
        if voter_address in self._voted_addresses:
            raise ValueError(f"Voter {voter_address} has already voted")
        
        new_vote = {
            "voter_address": voter_address,
            "vote": vote.lower(),
            "voting_power": voting_power,
            "timestamp": self._get_current_timestamp()
        }
        
        self.votes.append(new_vote)
        self._voted_addresses.add(voter_address)
        self.updated_at = self._get_current_timestamp()
        
        self.logger.debug(f"Vote added to proposal {self.proposal_id}: {voter_address} voted {vote}")
    
    def get_vote_count(self) -> Dict:
        """
        Get vote count.
        
        Returns:
            Vote count dictionary
        """
        vote_counts = {"yes": 0, "no": 0, "abstain": 0, "total": 0}
        
        for vote in self.votes:
            vote_type = vote["vote"]
            if vote_type in vote_counts:
                vote_counts[vote_type] += vote["voting_power"]
            vote_counts["total"] += vote["voting_power"]
        
        return vote_counts
    
    def get_vote_percentage(self) -> Dict:
        """
        Get vote percentages.
        
        Returns:
            Vote percentage dictionary
        """
        counts = self.get_vote_count()
        
        if counts["total"] == 0:
            return {
                "yes": 0,
                "no": 0,
                "abstain": 0
            }
        
        return {
            "yes": counts["yes"] / counts["total"],
            "no": counts["no"] / counts["total"],
            "abstain": counts["abstain"] / counts["total"]
        }
    
    def has_reached_quorum(self, total_staking_power: float) -> bool:
        """
        Check if proposal has reached quorum.
        
        Args:
            total_staking_power: Total staking power in the network
            
        Returns:
            True if quorum is reached, False otherwise
        """
        if self.state != self.STATES["active"]:
            return False
        
        vote_count = self.get_vote_count()
        participation_rate = vote_count["total"] / total_staking_power
        
        return participation_rate >= self.quorum_required
    
    def is_passing(self, total_staking_power: float) -> bool:
        """
        Check if proposal is passing.
        
        Args:
            total_staking_power: Total staking power in the network
            
        Returns:
            True if proposal is passing, False otherwise
        """
        if self.state != self.STATES["active"]:
            return False
        
        vote_percentages = self.get_vote_percentage()
        
        return (
            self.has_reached_quorum(total_staking_power) and
            vote_percentages["yes"] >= self.approval_threshold
        )
    
    def finalize(self, total_staking_power: float):
        """
        Finalize proposal after voting period ends.
        
        Args:
            total_staking_power: Total staking power in the network
        """
        if self.state != self.STATES["active"]:
            raise ValueError("Only active proposals can be finalized")
        
        if not self._has_reached_end_time():
            raise ValueError("Voting period has not ended yet")
        
        if self.is_passing(total_staking_power):
            self.state = self.STATES["passed"]
        else:
            self.state = self.STATES["rejected"]
        
        self.updated_at = self._get_current_timestamp()
        
        self.logger.info(f"Proposal {self.proposal_id} finalized: {self.state}")
    
    def _has_reached_end_time(self) -> bool:
        """Check if voting period has ended."""
        return self._get_current_timestamp() >= self.voting_end_time
    
    def get_time_remaining(self) -> float:
        """
        Get time remaining in voting period.
        
        Returns:
            Time remaining in seconds, or 0 if ended
        """
        if self.state != self.STATES["active"]:
            return 0
        
        remaining = self.voting_end_time - self._get_current_timestamp()
        
        return max(0, remaining)
    
    def get_progress(self) -> float:
        """
        Get voting progress percentage.
        
        Returns:
            Progress percentage (0-1)
        """
        if self.state != self.STATES["active"]:
            return 0
        
        total_duration = self.voting_end_time - self.voting_start_time
        elapsed = self._get_current_timestamp() - self.voting_start_time
        
        return min(1.0, elapsed / total_duration)
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            Proposal as dictionary
        """
        return {
            'proposal_id': self.proposal_id,
            'title': self.title,
            'description': self.description,
            'proposer_address': self.proposer_address,
            'proposal_type': self.proposal_type,
            'state': self.state,
            'parameters': self.parameters,
            'voting_start_time': self.voting_start_time,
            'voting_end_time': self.voting_end_time,
            'quorum_required': self.quorum_required,
            'approval_threshold': self.approval_threshold,
            'votes': self.votes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def to_json(self) -> str:
        """
        Convert to JSON string.
        
        Returns:
            Proposal as JSON string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Proposal':
        """
        Create from dictionary.
        
        Args:
            data: Proposal data
            
        Returns:
            Proposal instance
        """
        proposal = cls(**data)
        # Initialize the voted addresses set for O(1) lookups
        proposal._voted_addresses = set(v["voter_address"] for v in proposal.votes)
        return proposal
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Proposal':
        """
        Create from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            Proposal instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self):
        """String representation."""
        return f"Proposal(id={self.proposal_id}, title=\"{self.title[:30]}...\")"
    
    def __str__(self):
        """String representation for printing."""
        return (
            f"Proposal {self.proposal_id}\n"
            f"Title: {self.title}\n"
            f"Type: {self.proposal_type}\n"
            f"State: {self.state}\n"
            f"Proposer: {self.proposer_address}\n"
            f"Votes: {len(self.votes)}\n"
            f"Created: {self.created_at}"
        )
