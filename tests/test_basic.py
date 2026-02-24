"""
Basic tests for ChainForgeLedger blockchain platform library
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
    KeyPair
)
from chainforgeledger.consensus import FinalityManager, Checkpoint, Vote
from chainforgeledger.core import (
    TransactionReceipt,
    LogEntry,
    create_transaction_receipt,
    LightClient,
    BlockHeader,
    ExecutionPipeline,
    PipelineContext,
    create_execution_pipeline,
    default_plugins,
    LoggingPlugin,
    GasTrackingPlugin,
    BlockProducer,
    ProductionOptions,
    ProductionResult,
    create_block_producer
)
from chainforgeledger.runtime import (
    EventSystem,
    Event,
    GasSystem,
    GasConfig,
    GasMetrics,
    PluginSystem,
    Plugin,
    PluginInfo,
    PluginConfig,
    StateMachine,
    StateSnapshot,
    ExecutionResult
)


class TestChainForgeLedger(unittest.TestCase):
    """Test ChainForgeLedger blockchain platform functionality"""
    
    def test_blockchain_creation(self):
        """Test blockchain creation"""
        blockchain = Blockchain(difficulty=2)
        self.assertEqual(len(blockchain.chain), 1)
        self.assertEqual(blockchain.chain[0].index, 0)
        
    def test_block_creation(self):
        """Test block creation"""
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
        
    def test_transaction_creation(self):
        """Test transaction creation"""
        tx = Transaction(
            sender="sender1",
            receiver="receiver1",
            amount=10.0
        )
        
        self.assertIsNotNone(tx)
        self.assertEqual(tx.sender, "sender1")
        self.assertEqual(tx.receiver, "receiver1")
        self.assertEqual(tx.amount, 10.0)
        
    def test_pow_creation(self):
        """Test Proof of Work creation"""
        blockchain = Blockchain(difficulty=2)
        pow_consensus = ProofOfWork(blockchain, difficulty=2, reward=50.0)
        self.assertIsNotNone(pow_consensus)
        self.assertEqual(pow_consensus.difficulty, 2)
        self.assertEqual(pow_consensus.reward, 50.0)
        
    def test_pos_creation(self):
        """Test Proof of Stake creation"""
        blockchain = Blockchain(difficulty=2)
        pos_consensus = ProofOfStake(blockchain)
        self.assertIsNotNone(pos_consensus)
        
    def test_wallet_creation(self):
        """Test wallet creation"""
        wallet = Wallet()
        self.assertIsNotNone(wallet.address)
        self.assertEqual(wallet.balance, 0.0)
        
    def test_key_generation(self):
        """Test key generation"""
        key_pair, address = generate_keys()
        self.assertIsNotNone(key_pair)
        self.assertIsNotNone(address)
        self.assertIsInstance(key_pair, KeyPair)
        
    def test_node_creation(self):
        """Test network node creation"""
        node = Node("node1")
        self.assertIsNotNone(node)
        self.assertEqual(node.node_id, "node1")
        
    def test_peer_creation(self):
        """Test peer creation"""
        peer = Peer("peer1", "127.0.0.1", 8080)
        self.assertIsNotNone(peer)
        self.assertEqual(peer.address, "127.0.0.1")
        self.assertEqual(peer.port, 8080)
        
    def test_mem_pool_creation(self):
        """Test mempool creation"""
        mempool = MemPool()
        self.assertIsNotNone(mempool)
        
    def test_proposal_creation(self):
        """Test governance proposal creation"""
        proposal = Proposal(
            title="Test Proposal",
            description="This is a test proposal",
            proposer_address="user1"
        )
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.title, "Test Proposal")
        
    def test_voting_system_creation(self):
        """Test voting system creation"""
        voting = VotingSystem()
        self.assertIsNotNone(voting)
        
    def test_pos_creation(self):
        """Test Proof of Stake creation"""
        from chainforgeledger.consensus.validator import ValidatorManager
        
        blockchain = Blockchain(difficulty=2)
        validator_manager = ValidatorManager()
        pos_consensus = ProofOfStake(blockchain, validator_manager, reward=50.0)
        self.assertIsNotNone(pos_consensus)
        
    def test_virtual_machine_creation(self):
        """Test virtual machine creation"""
        vm = VirtualMachine()
        self.assertIsNotNone(vm)
        
    def test_compiler_creation(self):
        """Test compiler creation"""
        compiler = Compiler()
        self.assertIsNotNone(compiler)
        
    def test_contract_executor_creation(self):
        """Test contract executor creation"""
        executor = ContractExecutor()
        self.assertIsNotNone(executor)
        
    def test_protocol_creation(self):
        """Test network protocol creation"""
        protocol = Protocol()
        self.assertIsNotNone(protocol)
        
    def test_sha256_hash(self):
        """Test SHA-256 hashing"""
        test_data = "test data"
        hash_result = sha256_hash(test_data)
        self.assertIsNotNone(hash_result)
        self.assertEqual(len(hash_result), 64)
        self.assertIsInstance(hash_result, str)
        
    def test_blockchain_info(self):
        """Test blockchain information retrieval"""
        blockchain = Blockchain(difficulty=2)
        info = blockchain.get_blockchain_info()
        self.assertIsNotNone(info)
        self.assertEqual(info["chain_length"], 1)
        self.assertEqual(info["difficulty"], 2)
        self.assertEqual(info["total_transactions"], 0)
        self.assertIsNotNone(info["last_block_hash"])
        self.assertTrue(info["is_valid"])
        
    def test_block_validation(self):
        """Test block validation"""
        blockchain = Blockchain(difficulty=2)
        previous_block = blockchain.get_last_block()
        
        block = Block(
            index=1,
            previous_hash=previous_block.hash,
            transactions=[],
            difficulty=2
        )
        
        self.assertTrue(blockchain.is_valid_block(block))
        
    def test_chain_validation(self):
        """Test chain validation"""
        blockchain = Blockchain(difficulty=2)
        self.assertTrue(blockchain.is_chain_valid())
        
    def test_block_by_index(self):
        """Test block retrieval by index"""
        blockchain = Blockchain(difficulty=2)
        block = blockchain.get_block_by_index(0)
        self.assertIsNotNone(block)
        self.assertEqual(block.index, 0)
        
    def test_block_by_hash(self):
        """Test block retrieval by hash"""
        blockchain = Blockchain(difficulty=2)
        genesis_block = blockchain.get_last_block()
        block = blockchain.get_block_by_hash(genesis_block.hash)
        self.assertIsNotNone(block)
        self.assertEqual(block.index, 0)
    
    def test_finality_manager_creation(self):
        """Test FinalityManager creation"""
        fm = FinalityManager()
        self.assertIsNotNone(fm)
    
    def test_checkpoint_creation(self):
        """Test Checkpoint creation"""
        checkpoint = Checkpoint(block_number=1, block_hash="0"*64, epoch=0, timestamp=0)
        self.assertIsNotNone(checkpoint)
        self.assertEqual(checkpoint.block_number, 1)
    
    def test_vote_creation(self):
        """Test Vote creation"""
        vote = Vote(block_number=1, validator_id="validator1", signature="0"*64)
        self.assertIsNotNone(vote)
        self.assertEqual(vote.block_number, 1)
        self.assertEqual(vote.validator_id, "validator1")
    
    def test_transaction_receipt_creation(self):
        """Test TransactionReceipt creation"""
        receipt = create_transaction_receipt()
        self.assertIsNotNone(receipt)
        self.assertIsInstance(receipt, TransactionReceipt)
    
    def test_log_entry_creation(self):
        """Test LogEntry creation"""
        log = LogEntry(type="info", message="Test log")
        self.assertIsNotNone(log)
        self.assertEqual(log.type, "info")
        self.assertEqual(log.message, "Test log")
    
    def test_light_client_creation(self):
        """Test LightClient creation"""
        client = LightClient()
        self.assertIsNotNone(client)
    
    def test_block_header_creation(self):
        """Test BlockHeader creation"""
        header = BlockHeader(
            index=1,
            previous_hash="0"*64,
            tx_root="0"*64,
            state_root="0"*64,
            receipt_root="0"*64,
            validator="validator1",
            timestamp=0,
            hash="0"*64
        )
        self.assertIsNotNone(header)
        self.assertEqual(header.index, 1)
    
    def test_execution_pipeline_creation(self):
        """Test ExecutionPipeline creation"""
        pipeline = create_execution_pipeline()
        self.assertIsNotNone(pipeline)
        self.assertIsInstance(pipeline, ExecutionPipeline)
    
    def test_pipeline_context_creation(self):
        """Test PipelineContext creation"""
        context = PipelineContext(block_hash="0"*64, block_number=1)
        self.assertIsNotNone(context)
        self.assertEqual(context.block_number, 1)
    
    def test_block_producer_creation(self):
        """Test BlockProducer creation"""
        producer = create_block_producer()
        self.assertIsNotNone(producer)
        self.assertIsInstance(producer, BlockProducer)
    
    def test_production_options_creation(self):
        """Test ProductionOptions creation"""
        options = ProductionOptions(max_block_size=2000000)
        self.assertIsNotNone(options)
        self.assertEqual(options.max_block_size, 2000000)
    
    def test_event_system_creation(self):
        """Test EventSystem creation"""
        events = EventSystem()
        self.assertIsNotNone(events)
    
    def test_event_creation(self):
        """Test Event creation"""
        event = Event(event_type="block.created", data={"block_number": 1})
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, "block.created")
    
    def test_gas_system_creation(self):
        """Test GasSystem creation"""
        gas = GasSystem()
        self.assertIsNotNone(gas)
    
    def test_gas_config_creation(self):
        """Test GasConfig creation"""
        config = GasConfig(block_gas_limit=20000000)
        self.assertIsNotNone(config)
        self.assertEqual(config.block_gas_limit, 20000000)
    
    def test_gas_metrics_creation(self):
        """Test GasMetrics creation"""
        metrics = GasMetrics(total_gas=10000000, used_gas=5000000)
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.total_gas, 10000000)
        self.assertEqual(metrics.used_gas, 5000000)
    
    def test_plugin_system_creation(self):
        """Test PluginSystem creation"""
        plugins = PluginSystem()
        self.assertIsNotNone(plugins)
    
    def test_plugin_info_creation(self):
        """Test PluginInfo creation"""
        info = PluginInfo(name="test-plugin", version="1.0.0", author="test", description="Test plugin", category="test")
        self.assertIsNotNone(info)
        self.assertEqual(info.name, "test-plugin")
    
    def test_plugin_config_creation(self):
        """Test PluginConfig creation"""
        config = PluginConfig(name="test-plugin", version="1.0.0", config={"key": "value"})
        self.assertIsNotNone(config)
        self.assertEqual(config.name, "test-plugin")
    
    def test_state_machine_creation(self):
        """Test StateMachine creation"""
        state_machine = StateMachine()
        self.assertIsNotNone(state_machine)
    
    def test_state_snapshot_creation(self):
        """Test StateSnapshot creation"""
        snapshot = StateSnapshot(block_number=1, block_hash="0"*64, state_root="0"*64, timestamp=0)
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.block_number, 1)
    
    def test_execution_result_creation(self):
        """Test ExecutionResult creation"""
        result = ExecutionResult(success=True, state_root="0"*64, gas_used=1000, gas_limit=2000)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertEqual(result.gas_used, 1000)


if __name__ == '__main__':
    unittest.main()
