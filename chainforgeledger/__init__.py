"""
ChainForgeLedger - A complete blockchain platform library

A comprehensive blockchain platform built from scratch with pure Python.
Features include:
- Proof of Work (PoW) and Proof of Stake (PoS) consensus mechanisms
- Smart contract virtual machine with stack-based execution
- Decentralized exchange (DEX) with automated market making (AMM)
- Lending protocol with borrowing and lending functionality
- NFT marketplace for digital asset creation and trading
- Blockchain explorer for analytics and visualization
- Wallet system with various types (CLI, web, mobile, multisig, hardware)
- Governance system with DAO framework
- Security architecture with multiple protection mechanisms
- Tokenomics system with vesting, staking, and reward mechanisms

Author: Kanishk Kumar Singh
Email: kanishkkumar2004@gmail.com
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Kanishk Kumar Singh"
__email__ = "kanishkkumar2004@gmail.com"
__description__ = "A complete blockchain platform library with PoW/PoS consensus, smart contracts, and DeFi applications"

# Export core modules
from chainforgeledger.core.block import Block
from chainforgeledger.core.blockchain import Blockchain
from chainforgeledger.core.transaction import Transaction
from chainforgeledger.core.merkle import MerkleTree
from chainforgeledger.core.state import State

# Export consensus mechanisms
from chainforgeledger.consensus.pow import ProofOfWork
from chainforgeledger.consensus.pos import ProofOfStake
from chainforgeledger.consensus.validator import Validator, ValidatorManager

# Export cryptographic utilities
from chainforgeledger.crypto.hashing import sha256_hash
from chainforgeledger.crypto.keys import generate_keys, KeyPair
from chainforgeledger.crypto.signature import Signature
from chainforgeledger.crypto.wallet import Wallet

# Export networking
from chainforgeledger.networking.node import Node
from chainforgeledger.networking.peer import Peer
from chainforgeledger.networking.protocol import Protocol
from chainforgeledger.networking.mempool import MemPool

# Export smart contracts
from chainforgeledger.smartcontracts.vm import VirtualMachine
from chainforgeledger.smartcontracts.compiler import Compiler
from chainforgeledger.smartcontracts.executor import ContractExecutor

# Export API
from chainforgeledger.api.server import ApiServer
from chainforgeledger.api.routes import ApiRoutes

# Export storage
from chainforgeledger.storage.database import Database
from chainforgeledger.storage.leveldb import LevelDBStorage
from chainforgeledger.storage.models import BlockStorage, TransactionStorage

# Export governance
from chainforgeledger.governance.proposal import Proposal
from chainforgeledger.governance.voting import VotingSystem

# Export governance
from chainforgeledger.governance.proposal import Proposal
from chainforgeledger.governance.voting import VotingSystem

# Export tokenomics
from chainforgeledger.tokenomics import Tokenomics

# Export utilities
from chainforgeledger.utils.config import Config

