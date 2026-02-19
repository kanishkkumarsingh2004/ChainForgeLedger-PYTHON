"""
ChainForgeLedger Smart Contract Executor

Contract execution engine for managing contract instances.
"""

import time
from typing import Any, Dict, List, Optional
from chainforgeledger.utils.logger import get_logger
from chainforgeledger.smartcontracts.vm import VirtualMachine
from chainforgeledger.smartcontracts.compiler import Compiler
from chainforgeledger.crypto.hashing import sha256_hash


class ContractExecutor:
    """
    Smart contract execution engine.
    
    Manages contract deployment, execution, and state management.
    """
    
    def __init__(self, vm: Optional[VirtualMachine] = None):
        """
        Initialize a new ContractExecutor instance.
        
        Args:
            vm: Virtual machine instance (will be created if not provided)
        """
        self.vm = vm or VirtualMachine()
        self.compiler = Compiler()
        self.contracts = {}
        self.contract_events = []
        self.logger = get_logger(__name__)
    
    def deploy_contract(self, source_code: str, language: str = "simple", compiler_options: Dict = None) -> str:
        """
        Deploy a contract to the blockchain.
        
        Args:
            source_code: Contract source code
            language: Source language
            compiler_options: Compiler options
            
        Returns:
            Contract address
        """
        try:
            # Compile source code
            self.compiler.language = language
            bytecode = self.compiler.compile(source_code)
            
            # Generate contract address (hash of bytecode)
            contract_address = self._generate_contract_address(bytecode)
            
            # Store contract
            self.contracts[contract_address] = {
                "source_code": source_code,
                "bytecode": bytecode,
                "language": language,
                "compiler_options": compiler_options or {},
                "deployed_at": time.time(),
                "storage": {},
                "bytecode_hash": self._compute_bytecode_hash(bytecode),
                "source_code_hash": self._compute_source_hash(source_code),
                "state": "deployed"
            }
            
            self.logger.info(f"Contract deployed at address: {contract_address}")
            
            return contract_address
        
        except Exception as e:
            self.logger.error(f"Contract deployment failed: {e}")
            raise
    
    def execute_contract(self, contract_address: str, method: str = None, params: List[Any] = None) -> Dict:
        """
        Execute a contract method.
        
        Args:
            contract_address: Contract address
            method: Method to call
            params: Method parameters
            
        Returns:
            Execution result
        """
        try:
            contract = self._get_contract(contract_address)
            
            # Check if contract is active
            if contract["state"] != "deployed":
                raise Exception(f"Contract is {contract['state']}")
            
            # Execute bytecode
            result = self.vm.execute_bytecode(contract["bytecode"])
            
            # Log execution
            self._log_event({
                "contract_address": contract_address,
                "method": method,
                "params": params,
                "result": result,
                "timestamp": time.time()
            })
            
            return result
        
        except Exception as e:
            self.logger.error(f"Contract execution failed: {e}")
            return {"success": False, "error": str(e), "gas_used": self.vm.gas_used}
    
    def call_contract_method(self, contract_address: str, method: str, params: List[Any] = None) -> Any:
        """
        Call a contract method.
        
        Args:
            contract_address: Contract address
            method: Method to call
            params: Method parameters
            
        Returns:
            Method return value
        """
        try:
            contract = self._get_contract(contract_address)
            
            # Check if contract is active
            if contract["state"] != "deployed":
                raise Exception(f"Contract is {contract['state']}")
            
            # For now, just execute the entire contract
            return self.execute_contract(contract_address, method, params)
        
        except Exception as e:
            self.logger.error(f"Method call failed: {e}")
            return {"success": False, "error": str(e)}
    
    def update_contract(self, contract_address: str, new_source_code: str, language: str = "simple") -> bool:
        """
        Update a deployed contract.
        
        Args:
            contract_address: Contract address
            new_source_code: New source code
            language: Source language
            
        Returns:
            True if contract was updated successfully
        """
        try:
            contract = self._get_contract(contract_address)
            
            # Compile new source code
            self.compiler.language = language
            new_bytecode = self.compiler.compile(new_source_code)
            
            # Update contract
            contract.update({
                "source_code": new_source_code,
                "bytecode": new_bytecode,
                "language": language,
                "bytecode_hash": self._compute_bytecode_hash(new_bytecode),
                "source_code_hash": self._compute_source_hash(new_source_code),
                "updated_at": time.time()
            })
            
            self.logger.info(f"Contract updated at address: {contract_address}")
            return True
        
        except Exception as e:
            self.logger.error(f"Contract update failed: {e}")
            return False
    
    def deactivate_contract(self, contract_address: str) -> bool:
        """
        Deactivate a contract.
        
        Args:
            contract_address: Contract address
            
        Returns:
            True if contract was deactivated successfully
        """
        try:
            contract = self._get_contract(contract_address)
            contract["state"] = "deactivated"
            contract["deactivated_at"] = time.time()
            
            self.logger.info(f"Contract deactivated at address: {contract_address}")
            return True
        
        except Exception as e:
            self.logger.error(f"Contract deactivation failed: {e}")
            return False
    
    def activate_contract(self, contract_address: str) -> bool:
        """
        Activate a deactivated contract.
        
        Args:
            contract_address: Contract address
            
        Returns:
            True if contract was activated successfully
        """
        try:
            contract = self._get_contract(contract_address)
            contract["state"] = "deployed"
            contract["activated_at"] = time.time()
            
            self.logger.info(f"Contract activated at address: {contract_address}")
            return True
        
        except Exception as e:
            self.logger.error(f"Contract activation failed: {e}")
            return False
    
    def delete_contract(self, contract_address: str) -> bool:
        """
        Delete a contract (dangerous operation).
        
        Args:
            contract_address: Contract address
            
        Returns:
            True if contract was deleted successfully
        """
        try:
            del self.contracts[contract_address]
            self.logger.info(f"Contract deleted: {contract_address}")
            return True
        
        except Exception as e:
            self.logger.error(f"Contract deletion failed: {e}")
            return False
    
    def get_contract_info(self, contract_address: str) -> Dict:
        """
        Get contract information.
        
        Args:
            contract_address: Contract address
            
        Returns:
            Contract information
        """
        contract = self._get_contract(contract_address)
        info = contract.copy()
        
        # Add execution statistics
        execution_count = len([e for e in self.contract_events 
                             if e["contract_address"] == contract_address])
        info["execution_count"] = execution_count
        
        return info
    
    def get_contract_storage(self, contract_address: str) -> Dict:
        """
        Get contract storage.
        
        Args:
            contract_address: Contract address
            
        Returns:
            Contract storage
        """
        contract = self._get_contract(contract_address)
        return contract["storage"].copy()
    
    def update_contract_storage(self, contract_address: str, key: str, value: Any):
        """
        Update contract storage.
        
        Args:
            contract_address: Contract address
            key: Storage key
            value: Storage value
        """
        try:
            contract = self._get_contract(contract_address)
            contract["storage"][key] = value
            
            self.logger.debug(f"Contract storage updated: {contract_address} -> {key}: {value}")
            
        except Exception as e:
            self.logger.error(f"Storage update failed: {e}")
            raise
    
    def get_contract_bytecode(self, contract_address: str) -> str:
        """
        Get contract bytecode.
        
        Args:
            contract_address: Contract address
            
        Returns:
            Contract bytecode
        """
        contract = self._get_contract(contract_address)
        return contract["bytecode"]
    
    def get_contract_source_code(self, contract_address: str) -> str:
        """
        Get contract source code.
        
        Args:
            contract_address: Contract address
            
        Returns:
            Contract source code
        """
        contract = self._get_contract(contract_address)
        return contract["source_code"]
    
    def get_all_contracts(self) -> List[Dict]:
        """
        Get all deployed contracts.
        
        Returns:
            List of contract information
        """
        return [
            self.get_contract_info(addr)
            for addr in self.contracts
        ]
    
    def get_contract_events(self, contract_address: str = None, limit: int = 100) -> List[Dict]:
        """
        Get contract events.
        
        Args:
            contract_address: Optional contract address filter
            limit: Maximum number of events to return
            
        Returns:
            List of contract events
        """
        events = self.contract_events
        
        if contract_address:
            events = [e for e in events if e["contract_address"] == contract_address]
        
        return events[-limit:]
    
    def get_vm_state(self) -> Dict:
        """
        Get VM state information.
        
        Returns:
            VM state information
        """
        return self.vm.get_vm_state()
    
    def get_gas_usage(self, contract_address: str = None) -> Dict:
        """
        Get gas usage information.
        
        Args:
            contract_address: Optional contract address filter
            
        Returns:
            Gas usage statistics
        """
        if contract_address:
            events = [e for e in self.contract_events if e["contract_address"] == contract_address]
        else:
            events = self.contract_events
        
        if not events:
            return {
                "total": 0,
                "average": 0,
                "maximum": 0,
                "minimum": 0,
                "count": 0
            }
        
        gas_used = [e["result"]["gas_used"] for e in events if "gas_used" in e["result"]]
        
        return {
            "total": sum(gas_used),
            "average": sum(gas_used) / len(gas_used),
            "maximum": max(gas_used),
            "minimum": min(gas_used),
            "count": len(gas_used)
        }
    
    def analyze_contract(self, contract_address: str) -> Dict:
        """
        Analyze contract performance and security.
        
        Args:
            contract_address: Contract address
            
        Returns:
            Analysis results
        """
        contract = self._get_contract(contract_address)
        events = [e for e in self.contract_events if e["contract_address"] == contract_address]
        
        gas_info = self.get_gas_usage(contract_address)
        
        return {
            "contract_address": contract_address,
            "bytecode_length": len(contract["bytecode"]),
            "storage_size": len(contract["storage"]),
            "execution_count": len(events),
            "gas_usage": gas_info,
            "storage_analysis": self._analyze_storage(contract["storage"])
        }
    
    def verify_contract(self, contract_address: str, source_code: str, language: str = "simple") -> bool:
        """
        Verify contract source code against deployed bytecode.
        
        Args:
            contract_address: Contract address
            source_code: Source code to verify
            language: Source language
            
        Returns:
            True if source code matches bytecode
        """
        try:
            contract = self._get_contract(contract_address)
            
            self.compiler.language = language
            compiled_bytecode = self.compiler.compile(source_code)
            
            return contract["bytecode"] == compiled_bytecode
        
        except Exception as e:
            self.logger.error(f"Contract verification failed: {e}")
            return False
    
    def _get_contract(self, contract_address: str) -> Dict:
        """Get contract or raise exception if not found."""
        if contract_address not in self.contracts:
            raise Exception(f"Contract not found: {contract_address}")
        return self.contracts[contract_address]
    
    def _generate_contract_address(self, bytecode: str) -> str:
        """Generate contract address from bytecode."""
        return sha256_hash(bytecode)[:40]  # 20 bytes
    
    def _compute_bytecode_hash(self, bytecode: str) -> str:
        """Compute SHA-256 hash of bytecode."""
        return sha256_hash(bytecode)
    
    def _compute_source_hash(self, source_code: str) -> str:
        """Compute SHA-256 hash of source code."""
        return sha256_hash(source_code)
    
    def _log_event(self, event: Dict):
        """Log contract execution event."""
        self.contract_events.append(event)
        
        # Keep only last 1000 events
        if len(self.contract_events) > 1000:
            self.contract_events = self.contract_events[-1000:]
    
    def _analyze_storage(self, storage: Dict) -> Dict:
        """Analyze contract storage."""
        types = {}
        for key, value in storage.items():
            value_type = type(value).__name__
            types[value_type] = types.get(value_type, 0) + 1
        
        return {
            "total_items": len(storage),
            "types": types,
            "average_value_length": sum(len(str(v)) for v in storage.values()) / len(storage) if storage else 0
        }
    
    def __repr__(self):
        """String representation of executor."""
        return f"ContractExecutor(contract_count={len(self.contracts)}, vm={repr(self.vm)})"
    
    def __str__(self):
        """String representation for printing."""
        gas_info = self.get_gas_usage()
        
        return (
            f"Contract Executor\n"
            f"=================\n"
            f"Contracts: {len(self.contracts)}\n"
            f"Events: {len(self.contract_events)}\n"
            f"VM: {repr(self.vm)}\n"
            f"Gas Usage: {gas_info['total']} total, {gas_info['average']:.2f} average"
        )
