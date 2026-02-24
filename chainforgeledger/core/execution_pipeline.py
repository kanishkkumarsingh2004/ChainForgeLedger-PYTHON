"""
Execution pipeline for processing transactions and blocks

A comprehensive execution pipeline that handles:
- Transaction validation and processing
- Block creation and validation
- State transitions
- Gas calculation and fee management
- Receipt generation
- Plugin-based extensibility
"""

import time
from typing import Dict, List, Any
from dataclasses import dataclass, field
from chainforgeledger.core.receipt import TransactionReceipt, create_transaction_receipt


@dataclass
class PipelineContext:
    """Execution pipeline context"""
    block_hash: str = None
    block_number: int = None
    timestamp: float = field(default_factory=lambda: time.time())
    gas_limit: int = 10_000_000
    gas_price: float = 1e-9
    validator: str = None


class ExecutionPipeline:
    """
    Execution pipeline for blockchain operations
    """
    
    def __init__(self, options: Dict = None):
        options = options or {}
        self.state_machine = options.get('stateMachine')
        self.gas_calculator = options.get('gasCalculator')
        self.fee_calculator = options.get('feeCalculator')
        self.event_emitter = options.get('eventEmitter')
        self.plugins = options.get('plugins', [])
        self.logger = options.get('logger')
    
    async def process_transaction(self, transaction: Any, context: PipelineContext = None) -> 'TransactionReceipt':
        """Process a single transaction"""
        
        context = context or PipelineContext()
        receipt = create_transaction_receipt({
            'transactionId': transaction.id,
            'blockHash': context.block_hash,
            'blockNumber': context.block_number
        })
        
        try:
            # Validate transaction before execution
            validation = transaction.validate()
            if not validation['isValid']:
                receipt.set_status('failed')
                receipt.add_log({
                    'type': 'error',
                    'message': validation['message'],
                    'timestamp': time.time()
                })
                return receipt
            
            # Execute pre-processing plugins
            for plugin in self.plugins:
                if hasattr(plugin, 'pre_process_transaction'):
                    await plugin.pre_process_transaction(transaction, context)
            
            # Estimate gas requirements
            estimated_gas = self.gas_calculator.estimate_gas(transaction)
            if transaction.gas_limit < estimated_gas:
                receipt.set_status('failed')
                receipt.add_log({
                    'type': 'error',
                    'message': f"Insufficient gas limit: required {estimated_gas}, provided {transaction.gas_limit}",
                    'timestamp': time.time()
                })
                return receipt
            
            # Execute transaction
            result = await self.state_machine.apply_transaction(transaction)
            
            # Handle execution results
            if result.success:
                receipt.set_status('successful')
                receipt.set_gas_used(result.gas_used)
                receipt.set_fee(result.gas_used * context.gas_price)
                receipt.set_root(result.state_root)
                
                for log in result.logs:
                    receipt.add_log(log)
                
                # Handle contract creation
                if not transaction.to_address:
                    # Calculate contract address from transaction
                    contract_address = self._calculate_contract_address(transaction)
                    receipt.set_contract_address(contract_address)
            else:
                receipt.set_status('failed')
                receipt.add_log({
                    'type': 'error',
                    'message': result.error,
                    'timestamp': time.time()
                })
            
            # Execute post-processing plugins
            for plugin in self.plugins:
                if hasattr(plugin, 'post_process_transaction'):
                    await plugin.post_process_transaction(transaction, context, receipt)
            
            # Emit events
            if self.event_emitter:
                await self.event_emitter.emit('transaction.processed', {
                    'transaction': transaction,
                    'receipt': receipt,
                    'context': context
                })
        
        except Exception as e:
            receipt.set_status('failed')
            receipt.add_log({
                'type': 'error',
                'message': str(e),
                'timestamp': time.time()
            })
        
        return receipt
    
    async def process_block(self, block: Any, context: PipelineContext = None) -> List['TransactionReceipt']:
        """Process all transactions in a block"""
        context = context or PipelineContext()
        context.block_hash = block.hash
        context.block_number = block.index
        context.timestamp = block.timestamp
        context.validator = block.validator
        
        receipts = []
        cumulative_gas_used = 0
        
        # Execute block-level pre-processing plugins
        for plugin in self.plugins:
            if hasattr(plugin, 'pre_process_block'):
                await plugin.pre_process_block(block, context)
        
        for transaction in block.transactions:
            # Check gas limit
            if cumulative_gas_used + transaction.gas_limit > context.gas_limit:
                receipt = await self._create_gas_limit_exceeded_receipt(transaction, context)
                receipts.append(receipt)
                continue
            
            receipt = await self.process_transaction(transaction, context)
            cumulative_gas_used += receipt.gas_used
            
            # Update cumulative gas used in receipt
            receipt.set_cumulative_gas_used(cumulative_gas_used)
            receipt.set_effective_gas_price(context.gas_price)
            
            receipts.append(receipt)
        
        # Execute block-level post-processing plugins
        for plugin in self.plugins:
            if hasattr(plugin, 'post_process_block'):
                await plugin.post_process_block(block, context, receipts)
        
        return receipts
    
    async def _create_gas_limit_exceeded_receipt(self, transaction: Any, context: PipelineContext) -> 'TransactionReceipt':
        """Create receipt for gas limit exceeded"""
        from chainforgeledger.core.receipt import TransactionReceipt
        
        receipt = TransactionReceipt(
            transaction_id=transaction.id,
            block_hash=context.block_hash,
            block_number=context.block_number,
            status='failed'
        )
        
        receipt.add_log({
            'type': 'error',
            'message': 'Block gas limit exceeded',
            'timestamp': time.time()
        })
        
        return receipt
    
    def _calculate_contract_address(self, transaction: Any) -> str:
        """Calculate contract address from transaction"""
        from chainforgeledger.crypto.hashing import sha256_hash
        address_data = f"{transaction.from_address}:{transaction.nonce}"
        return sha256_hash(address_data)
    
    async def validate_block(self, block: Any) -> Dict:
        """Validate block before processing"""
        errors = []
        
        # Check block structure
        if not hasattr(block, 'index') or block.index < 0:
            errors.append("Invalid block index")
        
        if not hasattr(block, 'hash') or len(block.hash) != 64:
            errors.append("Invalid block hash format")
        
        if not hasattr(block, 'transactions') or not isinstance(block.transactions, list):
            errors.append("Invalid transactions format")
        
        # Check transaction validity
        for transaction in block.transactions:
            validation = transaction.validate()
            if not validation['isValid']:
                errors.append(f"Invalid transaction: {validation['message']}")
        
        # Execute validation plugins
        for plugin in self.plugins:
            if hasattr(plugin, 'validate_block'):
                plugin_errors = await plugin.validate_block(block)
                errors.extend(plugin_errors)
        
        return {
            'isValid': len(errors) == 0,
            'errors': errors
        }
    
    def add_plugin(self, plugin: Any):
        """Add plugin to pipeline"""
        self.plugins.append(plugin)
    
    def remove_plugin(self, plugin: Any):
        """Remove plugin from pipeline"""
        if plugin in self.plugins:
            self.plugins.remove(plugin)
    
    def get_plugins(self) -> List[Any]:
        """Get all plugins"""
        return list(self.plugins)


def create_execution_pipeline(options: Dict = None) -> ExecutionPipeline:
    """Create a new execution pipeline instance"""
    options = options or {}
    return ExecutionPipeline(options)


class LoggingPlugin:
    """Example plugin for transaction and block logging"""
    
    def __init__(self, logger):
        self.logger = logger
    
    async def pre_process_transaction(self, transaction: Any, context: PipelineContext):
        self.logger.debug(f"Processing transaction {transaction.id}")
    
    async def post_process_transaction(self, transaction: Any, context: PipelineContext, receipt: 'TransactionReceipt'):
        status = '✅' if receipt.status == 'successful' else '❌'
        self.logger.debug(f"Transaction {transaction.id} {status}: {receipt.status}")
    
    async def pre_process_block(self, block: Any, context: PipelineContext):
        self.logger.debug(f"Processing block {block.index} with {len(block.transactions)} transactions")
    
    async def post_process_block(self, block: Any, context: PipelineContext, receipts: List['TransactionReceipt']):
        successful = sum(1 for r in receipts if r.status == 'successful')
        failed = sum(1 for r in receipts if r.status == 'failed')
        self.logger.debug(f"Block {block.index} processed: {successful} successful, {failed} failed")


class GasTrackingPlugin:
    """Example plugin for gas usage tracking"""
    
    async def pre_process_transaction(self, transaction: Any, context: PipelineContext):
        pass
    
    async def post_process_transaction(self, transaction: Any, context: PipelineContext, receipt: 'TransactionReceipt'):
        pass
    
    async def pre_process_block(self, block: Any, context: PipelineContext):
        pass
    
    async def post_process_block(self, block: Any, context: PipelineContext, receipts: List['TransactionReceipt']):
        total_gas = sum(r.gas_used for r in receipts)
        print(f"Block {block.index} gas usage: {total_gas} units")


# Default pipeline configuration
default_plugins = {
    'logging': LoggingPlugin,
    'gasTracking': GasTrackingPlugin
}
