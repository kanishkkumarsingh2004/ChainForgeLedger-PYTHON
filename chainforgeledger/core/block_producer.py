"""
Block producer for creating and validating blocks

A comprehensive block production system that manages:
- Transaction selection from mempool
- Block creation and validation
- Consensus integration
- Execution pipeline management
- Block size and transaction count limits
- Production metrics
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ProductionOptions:
    """Block production configuration options"""
    max_block_size: int = 1000000  # 1MB
    max_transactions_per_block: int = 1000
    block_time_target: float = 10.0  # seconds
    gas_limit: int = 10_000_000
    include_all_transactions: bool = False
    prioritize_high_fee: bool = True


@dataclass
class ProductionResult:
    """Result of block production process"""
    success: bool
    block: Any = None
    transactions_count: int = 0
    block_size: int = 0
    production_time: float = 0.0
    validation_result: Dict = field(default_factory=dict)
    error: str = None


class BlockProducer:
    """
    Block producer for creating and validating blocks
    """
    
    def __init__(self, options: Dict = None):
        options = options or {}
        self.blockchain = options.get('blockchain')
        self.mempool = options.get('mempool')
        self.consensus = options.get('consensus')
        self.execution_pipeline = options.get('executionPipeline')
        self.logger = options.get('logger')
        
        self.max_block_size = options.get('maxBlockSize', 1000000)  # 1MB
        self.max_transactions_per_block = options.get('maxTransactionsPerBlock', 1000)
        self.block_time_target = options.get('blockTimeTarget', 10.0)  # 10 seconds
        
        # Create default execution pipeline if not provided
        if not self.execution_pipeline:
            from chainforgeledger.core.execution_pipeline import create_execution_pipeline, default_plugins
            self.execution_pipeline = create_execution_pipeline({
                'plugins': [default_plugins['logging'], default_plugins['gasTracking']]
            })
    
    async def produce_block(self, options: ProductionOptions = None) -> ProductionResult:
        """Produce a new block"""
        options = options or ProductionOptions()
        start_time = time.time()
        
        try:
            # Get transactions from mempool
            transactions = await self.select_transactions(options)
            
            # Create new block
            block = await self.create_new_block(transactions, options)
            
            # Validate block
            validation = await self.validate_block(block)
            if not validation['isValid']:
                raise Exception(f"Block validation failed: {validation['errors'][0]}")
            
            # Add block to blockchain
            await self.blockchain.add_block(block)
            
            # Calculate production metrics
            production_time = time.time() - start_time
            block_size = self.calculate_block_size(block)
            
            return ProductionResult(
                success=True,
                block=block,
                transactions_count=len(transactions),
                block_size=block_size,
                production_time=production_time,
                validation_result=validation
            )
        
        except Exception as e:
            return ProductionResult(
                success=False,
                error=str(e),
                production_time=time.time() - start_time
            )
    
    async def select_transactions(self, options: ProductionOptions) -> List[Any]:
        """Select transactions from mempool for inclusion in block"""
        if options.include_all_transactions:
            transactions = await self.mempool.get_all_transactions()
        else:
            transactions = await self.mempool.get_transactions()
        
        # Filter by transaction validity
        valid_transactions = []
        for tx in transactions:
            validation = tx.validate()
            if validation['isValid']:
                valid_transactions.append(tx)
        
        # Sort transactions (prioritize high fee)
        if options.prioritize_high_fee:
            valid_transactions.sort(
                key=lambda tx: (tx.gas_price * tx.gas_limit, -tx.timestamp),
                reverse=True
            )
        
        # Apply block limits
        selected_transactions = []
        total_size = 0
        
        for tx in valid_transactions:
            tx_size = self.calculate_transaction_size(tx)
            
            if len(selected_transactions) >= options.max_transactions_per_block:
                break
            
            if total_size + tx_size > options.max_block_size:
                break
            
            selected_transactions.append(tx)
            total_size += tx_size
        
        return selected_transactions
    
    async def create_new_block(self, transactions: List[Any], options: ProductionOptions) -> Any:
        """Create a new block instance"""
        from chainforgeledger.core.block import Block
        
        previous_block = self.blockchain.chain[-1] if self.blockchain.chain else None
        
        block = Block(
            index=(previous_block.index + 1) if previous_block else 0,
            previous_hash=previous_block.hash if previous_block else '0' * 64,
            transactions=transactions,
            validator=self.consensus.get_validator(),
            timestamp=time.time(),
            gas_limit=options.gas_limit
        )
        
        # Calculate block hash
        block.calculate_hash()
        
        return block
    
    async def validate_block(self, block: Any) -> Dict:
        """Validate block before addition to chain"""
        errors = []
        
        # Check block structure
        if not hasattr(block, 'index') or block.index < 0:
            errors.append("Invalid block index")
        
        if not hasattr(block, 'hash') or len(block.hash) != 64:
            errors.append("Invalid block hash format")
        
        if not hasattr(block, 'transactions') or not isinstance(block.transactions, list):
            errors.append("Invalid transactions format")
        
        # Check previous block reference
        if block.index > 0:
            previous_block = self.blockchain.get_block(block.index - 1)
            if not previous_block or previous_block.hash != block.previous_hash:
                errors.append(f"Invalid previous block reference: expected {previous_block.hash if previous_block else 'None'}, got {block.previous_hash}")
        
        # Check block size
        block_size = self.calculate_block_size(block)
        if block_size > self.max_block_size:
            errors.append(f"Block size exceeds limit: {block_size} bytes > {self.max_block_size} bytes")
        
        # Check transaction count
        if len(block.transactions) > self.max_transactions_per_block:
            errors.append(f"Transaction count exceeds limit: {len(block.transactions)} > {self.max_transactions_per_block}")
        
        # Validate via execution pipeline
        pipeline_validation = await self.execution_pipeline.validate_block(block)
        errors.extend(pipeline_validation['errors'])
        
        return {
            'isValid': len(errors) == 0,
            'errors': errors
        }
    
    def calculate_block_size(self, block: Any) -> int:
        """Calculate block size in bytes"""
        import sys
        return sys.getsizeof(str(block.to_dict()))
    
    def calculate_transaction_size(self, transaction: Any) -> int:
        """Calculate transaction size in bytes"""
        import sys
        return sys.getsizeof(str(transaction.to_dict()))
    
    async def estimate_block_production_time(self, transaction_count: int) -> float:
        """Estimate block production time based on transaction count"""
        base_time = 0.5
        per_transaction_time = 0.01
        return base_time + (transaction_count * per_transaction_time)
    
    async def get_production_metrics(self) -> Dict:
        """Get block production metrics"""
        if not self.blockchain or not self.blockchain.chain:
            return {
                'blocksProduced': 0,
                'transactionsProcessed': 0,
                'avgBlockTime': 0,
                'avgTransactionCount': 0
            }
        
        blocks_produced = len(self.blockchain.chain)
        transactions_processed = sum(len(block.transactions) for block in self.blockchain.chain)
        avg_transaction_count = transactions_processed / blocks_produced
        
        # Calculate average block time
        if blocks_produced > 1:
            first_block = self.blockchain.chain[0]
            last_block = self.blockchain.chain[-1]
            total_time = last_block.timestamp - first_block.timestamp
            avg_block_time = total_time / (blocks_produced - 1)
        else:
            avg_block_time = 0
        
        return {
            'blocksProduced': blocks_produced,
            'transactionsProcessed': transactions_processed,
            'avgBlockTime': avg_block_time,
            'avgTransactionCount': avg_transaction_count
        }
    
    def set_blockchain(self, blockchain):
        """Set blockchain instance"""
        self.blockchain = blockchain
    
    def set_mempool(self, mempool):
        """Set mempool instance"""
        self.mempool = mempool
    
    def set_consensus(self, consensus):
        """Set consensus instance"""
        self.consensus = consensus
    
    def set_execution_pipeline(self, pipeline):
        """Set execution pipeline instance"""
        self.execution_pipeline = pipeline
    
    def get_blockchain(self):
        """Get blockchain instance"""
        return self.blockchain
    
    def get_mempool(self):
        """Get mempool instance"""
        return self.mempool
    
    def get_consensus(self):
        """Get consensus instance"""
        return self.consensus
    
    def get_execution_pipeline(self):
        """Get execution pipeline instance"""
        return self.execution_pipeline


def create_block_producer(options: Dict = None) -> BlockProducer:
    """Create a new block producer instance"""
    options = options or {}
    return BlockProducer(options)
