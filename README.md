# ChainForgeLedger

A complete blockchain platform library built from scratch with pure Python. Features include:

- **Proof of Work (PoW)** and **Proof of Stake (PoS)** consensus mechanisms
- **Smart contract virtual machine** with stack-based execution
- **Decentralized exchange (DEX)** with automated market making (AMM)
- **Lending protocol** with borrowing and lending functionality
- **NFT marketplace** for digital asset creation and trading
- **Blockchain explorer** for analytics and visualization
- **Wallet system** with various types (CLI, web, mobile, multisig, hardware)
- **Governance system** with DAO framework
- **Security architecture** with multiple protection mechanisms
- **Tokenomics system** with vesting, staking, and reward mechanisms

## Installation

### From Source Code

```bash
cd /home/KK-kanishk/Desktop/RunningProject/BCT-IMP-ALG
pip install -e .
```

### Using Virtual Environment (Recommended)

```bash
cd /home/KK-kanishk/Desktop/RunningProject/BCT-IMP-ALG
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

### Quick Start Example

```python
from chainforgeledger import ProofOfWork, Tokenomics, Wallet

# Create a blockchain with PoW consensus (difficulty 3)
pow_chain = ProofOfWork(difficulty=3)
pow_chain.add_transaction("Transaction 1: User1 -> User2")
pow_chain.add_transaction("Transaction 2: User3 -> User4")
block = pow_chain.mine_block("miner1")

# Create tokenomics system with 1 billion tokens
tokenomics = Tokenomics(total_supply=1000000000, inflation_rate=0.02)
tokenomics.mint_tokens(1000000, 'staking_rewards')

# Create wallets
standard_wallet = Wallet()
multisig_wallet = Wallet('multisig')

# Get blockchain info
print(f"Chain Length: {len(pow_chain.chain)}")
print(f"Block Hash: {block.hash}")
print(f"Total Supply: {tokenomics.total_supply:,}")
```

### Running Examples

#### Basic Usage Example

```bash
cd /home/KK-kanishk/Desktop/RunningProject/BCT-IMP-ALG
PYTHONPATH=. python3 example/basic_usage.py
```

#### Comprehensive Platform Example

```bash
cd /home/KK-kanishk/Desktop/RunningProject/BCT-IMP-ALG
PYTHONPATH=. python3 example/comprehensive_usage.py
```

## CLI Commands

### ChainForgeLedger CLI

The library provides a comprehensive command-line interface with multiple commands:

```bash
# Show help information
chainforgeledger --help

# Run basic blockchain demonstration
chainforgeledger basic

# Run comprehensive platform demonstration
chainforgeledger demo

# Run Proof of Work operations
chainforgeledger pow --mine          # Mine a block with default difficulty (3)
chainforgeledger pow --mine --difficulty 2  # Mine with lower difficulty

# Run Proof of Stake operations
chainforgeledger pos --forge         # Forge a block

# Tokenomics operations
chainforgeledger token --create              # Create tokenomics system
chainforgeledger token --create --supply 500000000  # Custom supply
chainforgeledger token --mint 100000        # Mint 100,000 tokens
```

## Testing

### Running Tests

```bash
cd /home/KK-kanishk/Desktop/RunningProject/BCT-IMP-ALG
python -m pytest tests/test_basic.py -v
```

### Test Coverage

```bash
cd /home/KK-kanishk/Desktop/RunningProject/BCT-IMP-ALG
python -m pytest tests/test_basic.py --cov=chainforgeledger --cov-report=html
```

## Project Structure

```
/home/KK-kanishk/Desktop/RunningProject/BCT-IMP-ALG/
├── chainforgeledger/          # Main library package
│   ├── __init__.py            # Package initialization
│   ├── core/                  # Core blockchain functionality
│   │   ├── block.py          # Block structure and validation
│   │   ├── blockchain.py     # Blockchain management
│   │   ├── transaction.py    # Transaction handling
│   │   ├── merkle.py         # Merkle tree implementation
│   │   └── state.py          # State management
│   ├── consensus/            # Consensus mechanisms
│   │   ├── pow.py            # Proof of Work
│   │   ├── pos.py            # Proof of Stake
│   │   └── validator.py      # Validator management
│   ├── crypto/               # Cryptographic operations
│   │   ├── __init__.py       # Crypto module initialization
│   │   ├── hashing.py        # SHA-256 hashing and ECDSA signatures
│   │   ├── keys.py           # Key pair generation and management
│   │   ├── signature.py      # Digital signature utilities
│   │   └── wallet.py         # Wallet system
│   ├── governance/           # Governance system
│   │   ├── dao.py            # DAO framework
│   │   ├── proposal.py       # Proposal management
│   │   └── voting.py         # Voting mechanisms
│   ├── networking/           # Network communication
│   │   ├── node.py           # Node management
│   │   ├── peer.py           # Peer discovery
│   │   ├── protocol.py       # Communication protocols
│   │   └── mempool.py        # Transaction mempool
│   ├── smartcontracts/       # Smart contract layer
│   │   ├── vm.py             # Virtual machine
│   │   ├── compiler.py       # Contract compiler
│   │   └── executor.py       # Contract execution engine
│   ├── storage/              # Data storage
│   │   ├── database.py       # Database interface
│   │   ├── leveldb.py        # LevelDB storage
│   │   └── models.py         # Data models
│   ├── utils/                # Utility modules
│   │   ├── config.py         # Configuration management
│   │   ├── crypto.py         # Cryptographic utilities
│   │   └── logger.py         # Logging system
│   └── api/                  # API interface
│       ├── server.py         # API server
│       └── routes.py         # API routes
├── example/                    # Usage examples
│   ├── basic_usage.py         # Basic blockchain operations
│   ├── comprehensive_usage.py # Complete platform integration
│   └── compare_consensus.py   # Consensus mechanism comparison
├── tests/                     # Test suite
│   └── test_basic.py          # Basic functionality tests
├── setup.py                   # Package configuration
├── pyproject.toml             # Project metadata
├── requirements.txt           # Dependency management
└── README.md                  # Project documentation
```

## Performance Optimizations

The ChainForgeLedger library has been optimized for minimum time and space complexity. Key optimizations include:

### 1. Blockchain Module (`chainforgeledger/core/blockchain.py`)
- **Block Lookup**: Changed from O(n) linear search to O(1) hash map lookup using `_block_hash_map`
- **Storage**: Maintains both list and dictionary representations for efficient traversal and lookups

### 2. MemPool Module (`chainforgeledger/networking/mempool.py`)
- **Transaction Lookup**: Changed from O(n) linear search to O(1) hash map lookup using `_transaction_map`
- **Existence Check**: Optimized from O(n) to O(1) using dictionary contains operation

### 3. Governance Modules
- **DAO (`chainforgeledger/governance/dao.py`)**: Simplified validation logic with list comprehensions and `all()` function
- **Voting System (`chainforgeledger/governance/voting.py`)**: Added `_proposals_dict` for O(1) proposal lookups
- **Proposal (`chainforgeledger/governance/proposal.py`)**: Added `_voted_addresses` set for O(1) duplicate vote checking

### Performance Benefits
- Block lookups by hash: **O(1) instead of O(n)**
- Transaction lookups: **O(1) instead of O(n)**
- Vote checking: **O(1) instead of O(n)**
- Proposal lookups: **O(1) instead of O(n)**

These optimizations make the blockchain system much more efficient when handling large numbers of transactions, blocks, and proposals, especially in decentralized governance scenarios.

## Features

### Cryptographic Operations
- **SHA-256 Hashing**: Self-made implementation for secure hashing
- **ECDSA Signatures**: Self-made Elliptic Curve Digital Signature Algorithm
- **Key Management**: Key pair generation, storage, and conversion
- **Encryption**: XOR-based AES placeholder for data encryption
- **HMAC**: Hash-based Message Authentication Code
- **PBKDF2**: Password-based key derivation function
- **Random Number Generation**: Secure random string generation

### Core Blockchain
- **Proof of Work (PoW)**: Bitcoin-style mining with difficulty adjustment
- **Proof of Stake (PoS)**: Ethereum-style staking with validator selection
- **Transaction Management**: Complete transaction lifecycle
- **Block Validation**: Blockchain integrity and security checks

### Smart Contracts
- **Virtual Machine**: Stack-based VM with gas calculation
- **Contract Execution**: Method dispatch and storage management
- **Deployment**: Contract compilation and deployment process

### Decentralized Finance (DeFi)
- **DEX**: Automated Market Making (AMM) with liquidity pools
- **Lending Protocol**: Borrowing and lending with interest rates
- **NFT Marketplace**: Digital asset creation, minting, and trading

### Security
- **51% Attack Protection**: Chain reorganization detection
- **Sybil Attack Detection**: Node reputation and behavior monitoring
- **Replay Protection**: Transaction replay prevention
- **Double-Spending Detection**: Transaction validation mechanisms

### Governance
- **DAO Framework**: Decentralized governance with voting
- **Vesting Schedules**: Token distribution mechanisms
- **Treasury Management**: Fund allocation and distribution
- **Validator Rewards**: Incentive systems for network participants

### Wallet System
- **Standard Wallet**: Basic wallet functionality
- **CLI Wallet**: Command-line interface for direct interaction
- **Web Wallet**: Browser-based interface
- **Mobile Wallet**: Smartphone-optimized interface
- **Multisig Wallet**: Multiple signature authorization
- **Hardware Wallet**: Cold storage integration

### Tokenomics
- **Total Supply**: 1 billion tokens with annual inflation
- **Staking Rewards**: 10% of supply for staking incentives
- **Vesting Periods**: Lock-up periods for different stakeholders
- **Slashing Mechanisms**: Penalties for malicious behavior

## Requirements

- Python 3.8 or higher
- No external dependencies (pure Python implementation)
- Platform independent (works on Linux, macOS, Windows)

## Development

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for new functionality
5. Run tests to ensure everything passes
6. Create a pull request

### Building Package

```bash
cd /home/KK-kanishk/Desktop/RunningProject/BCT-IMP-ALG
python -m build
```

## License

MIT License - see LICENSE file for details

## Authors

Kanishk Kumar Singh - Initial development

## Support

For issues or questions:
- Open an issue on GitHub
- Contact the development team

---

**Note**: This is an educational implementation designed for learning purposes. It is not intended for production use with real cryptocurrency.
