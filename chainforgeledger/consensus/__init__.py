"""
ChainForgeLedger Consensus Mechanisms

Implementations of various blockchain consensus mechanisms including:
- Proof of Work (PoW)
- Proof of Stake (PoS)
- Validator management
- Finality mechanisms (LMD-GHOST, Casper FFG, PBFT)
"""

from chainforgeledger.consensus.pow import ProofOfWork
from chainforgeledger.consensus.pos import ProofOfStake
from chainforgeledger.consensus.validator import Validator
from chainforgeledger.consensus.finality import FinalityManager, Checkpoint, Vote
from chainforgeledger.consensus.interface import (
    ConsensusInterface,
    ProofOfWorkInterface,
    ProofOfStakeInterface,
    DelegatedProofOfStakeInterface,
    PBFTInterface,
    ConsensusFactory,
    ConsensusManager
)

__all__ = [
    "ProofOfWork", "ProofOfStake", "Validator", "FinalityManager", "Checkpoint", "Vote",
    "ConsensusInterface", "ProofOfWorkInterface", "ProofOfStakeInterface",
    "DelegatedProofOfStakeInterface", "PBFTInterface",
    "ConsensusFactory", "ConsensusManager"
]
