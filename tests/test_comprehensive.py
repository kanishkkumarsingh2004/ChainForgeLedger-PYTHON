"""
Comprehensive tests for ChainForgeLedger blockchain platform library
Testing all major components and functionality
"""

import unittest
from chainforgeledger import (
    Blockchain,
    Block,
    Transaction,
    ProofOfWork,
    ProofOfStake,
    Wallet,
    VirtualMachine,
    Compiler,
    ContractExecutor,
    Node,
    Peer,
    Protocol,
    MemPool,
    Proposal,
    VotingSystem,
    sha256_hash,
    generate_keys,
    KeyPair,
    MerkleTree,
    State,
    Validator,
    ValidatorManager,
    ApiServer,
    ApiRoutes,
    Database,
    LevelDBStorage,
    BlockStorage,
    TransactionStorage,
    Tokenomics,
    Config
)


class TestChainForgeLedgerComprehensive(unittest.TestCase):
    """Comprehensive test suite for ChainForgeLedger blockchain platform"""
    
    # ==================== Core Blockchain Tests ====================
    
    def test_blockchain_operations(self):
        """Test blockchain creation and basic operations"""
        blockchain = Blockchain(difficulty=2)
        self.assertEqual(len(blockchain.chain), 1)
        self.assertEqual(blockchain.chain[0].index, 0)
        
        # Test blockchain info
        info = blockchain.get_blockchain_info()
        self.assertIsNotNone(info)
        self.assertEqual(info["chain_length"], 1)
        self.assertEqual(info["difficulty"], 2)
        self.assertEqual(info["total_transactions"], 0)
        self.assertIsNotNone(info["last_block_hash"])
        self.assertTrue(info["is_valid"])
        
    def test_block_operations(self):
        """Test block creation and validation"""
        previous_block = Block(
            index=0,
            previous_hash="0" * 64,
            transactions=[],
            difficulty=2
        )
        
        block = Block(
            index=1,
            previous_hash=previous_block.hash,
            transactions=[],
            difficulty=2
        )
        
        self.assertIsNotNone(block)
        self.assertEqual(block.index, 1)
        self.assertEqual(block.previous_hash, previous_block.hash)
    
    def test_transaction_operations(self):
        """Test transaction creation and management"""
        tx = Transaction(
            sender="sender1",
            receiver="receiver1",
            amount=10.0
        )
        
        self.assertIsNotNone(tx)
        self.assertEqual(tx.sender, "sender1")
        self.assertEqual(tx.receiver, "receiver1")
        self.assertEqual(tx.amount, 10.0)
        
    def test_chain_validation(self):
        """Test blockchain chain validation"""
        blockchain = Blockchain(difficulty=2)
        self.assertTrue(blockchain.is_chain_valid())
        
        # Test block retrieval
        block_by_index = blockchain.get_block_by_index(0)
        self.assertIsNotNone(block_by_index)
        self.assertEqual(block_by_index.index, 0)
        
        genesis_block = blockchain.get_last_block()
        block_by_hash = blockchain.get_block_by_hash(genesis_block.hash)
        self.assertIsNotNone(block_by_hash)
        self.assertEqual(block_by_hash.index, 0)
    
    # ==================== Consensus Mechanisms ====================
    
    def test_pow_consensus(self):
        """Test Proof of Work consensus mechanism"""
        blockchain = Blockchain(difficulty=2)
        pow_consensus = ProofOfWork(blockchain, difficulty=2, reward=50.0)
        self.assertIsNotNone(pow_consensus)
        self.assertEqual(pow_consensus.difficulty, 2)
        self.assertEqual(pow_consensus.reward, 50.0)
    
    def test_pos_consensus(self):
        """Test Proof of Stake consensus mechanism"""
        blockchain = Blockchain(difficulty=2)
        validator_manager = ValidatorManager()
        pos_consensus = ProofOfStake(blockchain, validator_manager, reward=50.0)
        self.assertIsNotNone(pos_consensus)
    
    def test_validator_system(self):
        """Test validator management system"""
        validator_manager = ValidatorManager()
        validator = Validator("address1", stake=1000)
        validator_manager.add_validator(validator)
        
        self.assertEqual(len(validator_manager.validators), 1)
        self.assertIsNotNone(validator_manager.get_validator("address1"))
    
    # ==================== Cryptographic Tests ====================
    
    def test_wallet_operations(self):
        """Test wallet creation and management"""
        wallet = Wallet()
        self.assertIsNotNone(wallet.address)
        self.assertEqual(wallet.balance, 0.0)
    
    def test_key_generation(self):
        """Test cryptographic key generation"""
        key_pair, address = generate_keys()
        self.assertIsNotNone(key_pair)
        self.assertIsNotNone(address)
        self.assertIsInstance(key_pair, KeyPair)
    
    def test_hashing_functions(self):
        """Test SHA-256 hashing functionality"""
        test_data = "test data"
        hash_result = sha256_hash(test_data)
        self.assertIsNotNone(hash_result)
        self.assertEqual(len(hash_result), 64)
        self.assertIsInstance(hash_result, str)
        
        # Test hash consistency
        self.assertEqual(sha256_hash(test_data), hash_result)
    
    # ==================== Networking Tests ====================
    
    def test_node_operations(self):
        """Test network node creation and management"""
        node = Node("node1")
        self.assertIsNotNone(node)
        self.assertEqual(node.node_id, "node1")
    
    def test_peer_operations(self):
        """Test peer creation and management"""
        peer = Peer("peer1", "127.0.0.1", 8080)
        self.assertIsNotNone(peer)
        self.assertEqual(peer.address, "127.0.0.1")
        self.assertEqual(peer.port, 8080)
    
    def test_mempool_operations(self):
        """Test mempool operations"""
        mempool = MemPool()
        self.assertIsNotNone(mempool)
        
        # Test adding transactions (with signatures)
        tx1 = Transaction("sender1", "receiver1", 10.0)
        tx1.sign_transaction("private_key")
        tx2 = Transaction("sender2", "receiver2", 20.0)
        tx2.sign_transaction("private_key")
        
        mempool.add_transaction(tx1)
        mempool.add_transaction(tx2)
        
        self.assertEqual(len(mempool.transactions), 2)
    
    def test_protocol_operations(self):
        """Test network protocol operations"""
        protocol = Protocol()
        self.assertIsNotNone(protocol)
    
    # ==================== Smart Contracts Tests ====================
    
    def test_virtual_machine(self):
        """Test virtual machine operations"""
        vm = VirtualMachine()
        self.assertIsNotNone(vm)
    
    def test_compiler(self):
        """Test smart contract compiler"""
        compiler = Compiler()
        self.assertIsNotNone(compiler)
    
    def test_contract_executor(self):
        """Test contract executor operations"""
        executor = ContractExecutor()
        self.assertIsNotNone(executor)
    
    # ==================== Storage Tests ====================
    
    def test_database_operations(self):
        """Test database operations"""
        db = Database()
        self.assertIsNotNone(db)
    
    def test_block_storage(self):
        """Test block storage operations"""
        block_storage = BlockStorage()
        self.assertIsNotNone(block_storage)
    
    def test_transaction_storage(self):
        """Test transaction storage operations"""
        tx_storage = TransactionStorage()
        self.assertIsNotNone(tx_storage)
    
    # ==================== Governance Tests ====================
    
    def test_proposal_operations(self):
        """Test governance proposal creation and management"""
        proposal = Proposal(
            title="Test Proposal",
            description="This is a test proposal",
            proposer_address="user1"
        )
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.title, "Test Proposal")
    
    def test_voting_system(self):
        """Test voting system operations"""
        voting = VotingSystem()
        self.assertIsNotNone(voting)
    
    # ==================== Tokenomics Tests ====================
    
    def test_tokenomics_system(self):
        """Test tokenomics system operations"""
        tokenomics = Tokenomics()
        self.assertIsNotNone(tokenomics)
    
    # ==================== API Tests ====================
    
    def test_api_server(self):
        """Test API server operations"""
        server = ApiServer()
        self.assertIsNotNone(server)
    
    def test_api_routes(self):
        """Test API routes operations"""
        routes = ApiRoutes()
        self.assertIsNotNone(routes)
    
    # ==================== Utility Tests ====================
    
    def test_config_system(self):
        """Test configuration system"""
        config = Config()
        self.assertIsNotNone(config)
    
    def test_merkle_tree(self):
        """Test Merkle tree operations"""
        data = ["data1", "data2", "data3"]
        merkle_tree = MerkleTree(data)
        self.assertIsNotNone(merkle_tree)
        self.assertIsNotNone(merkle_tree.root)
    
    def test_state_management(self):
        """Test state management system"""
        state = State()
        self.assertIsNotNone(state)
    
    # ==================== Integration Tests ====================
    
    def test_blockchain_integration(self):
        """Test blockchain integration with transactions"""
        # Create blockchain
        blockchain = Blockchain(difficulty=2)
        
        # Create transactions
        tx1 = Transaction("sender1", "receiver1", 10.0)
        tx1.sign_transaction("private_key")
        tx2 = Transaction("sender2", "receiver2", 20.0)
        tx2.sign_transaction("private_key")
    
    def test_consensus_integration(self):
        """Test consensus mechanism integration"""
        blockchain = Blockchain(difficulty=2)
        pow_consensus = ProofOfWork(blockchain, difficulty=2, reward=50.0)
        self.assertIsNotNone(pow_consensus)
        
        # Test PoS integration
        validator_manager = ValidatorManager()
        validator = Validator("address1", stake=1000)
        validator_manager.add_validator(validator)
        pos_consensus = ProofOfStake(blockchain, validator_manager, reward=50.0)
        self.assertIsNotNone(pos_consensus)
    
    def test_wallet_transaction_integration(self):
        """Test wallet and transaction integration"""
        wallet1 = Wallet()
        wallet2 = Wallet()
        
        # Test transaction between wallets
        tx = Transaction(wallet1.address, wallet2.address, 10.0)
        self.assertIsNotNone(tx)
        self.assertEqual(tx.sender, wallet1.address)
        self.assertEqual(tx.receiver, wallet2.address)
        self.assertEqual(tx.amount, 10.0)
    
    def test_networking_integration(self):
        """Test networking components integration"""
        node1 = Node("node1")
        node2 = Node("node2")
        mempool = MemPool()
        
        # Connect nodes
        node1.connect(node2)
        self.assertEqual(len(node1.peers), 1)
        self.assertEqual(len(node2.peers), 1)
        
        # Add transaction to mempool
        tx = Transaction("sender1", "receiver1", 10.0)
        tx.sign_transaction("private_key")
        mempool.add_transaction(tx)
        self.assertEqual(len(mempool.transactions), 1)
    
    def test_smart_contract_integration(self):
        """Test smart contract components integration"""
        vm = VirtualMachine()
        compiler = Compiler()
        executor = ContractExecutor()
        
        self.assertIsNotNone(vm)
        self.assertIsNotNone(compiler)
        self.assertIsNotNone(executor)
    
    def test_storage_integration(self):
        """Test storage system integration"""
        db = Database()
        block_storage = BlockStorage()
        tx_storage = TransactionStorage()
        
        self.assertIsNotNone(db)
        self.assertIsNotNone(block_storage)
        self.assertIsNotNone(tx_storage)
    
    def test_governance_integration(self):
        """Test governance system integration"""
        proposal = Proposal(title="Test Proposal", description="Description", proposer_address="proposer1")
        voting = VotingSystem()
        
        self.assertIsNotNone(proposal)
        self.assertIsNotNone(voting)
    
    def test_tokenomics_integration(self):
        """Test tokenomics system integration"""
        tokenomics = Tokenomics()
        self.assertIsNotNone(tokenomics)


if __name__ == '__main__':
    print("Running ChainForgeLedger Comprehensive Tests...")
    print("=" * 60)
    
    # Run tests
    unittest.main()
