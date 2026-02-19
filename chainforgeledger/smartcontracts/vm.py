"""
ChainForgeLedger Virtual Machine

Smart contract virtual machine implementation with bytecode execution.
"""

from typing import Any, Dict, List
from chainforgeledger.utils.logger import get_logger
from chainforgeledger.crypto.hashing import sha256_hash


class VirtualMachine:
    """
    Smart contract virtual machine implementation.
    
    Attributes:
        memory: VM memory
        stack: VM stack
        storage: Contract storage
        pc: Program counter
        running: Execution status
        gas_used: Gas used during execution
        max_gas: Maximum gas allowed per execution
    """
    
    OPCODES = {
        "NOP": 0x00,          # No operation
        "PUSH": 0x01,         # Push value to stack
        "POP": 0x02,          # Pop from stack
        "ADD": 0x03,          # Add two values
        "SUB": 0x04,          # Subtract two values
        "MUL": 0x05,          # Multiply two values
        "DIV": 0x06,          # Divide two values
        "EQ": 0x07,           # Equality check
        "LT": 0x08,           # Less than check
        "GT": 0x09,           # Greater than check
        "JMP": 0x0A,          # Jump to address
        "JMPIF": 0x0B,        # Jump if condition is true
        "JMPIFNOT": 0x0C,     # Jump if condition is false
        "STORE": 0x0D,        # Store in contract storage
        "LOAD": 0x0E,         # Load from contract storage
        "MSTORE": 0x0F,       # Store in memory
        "MLOAD": 0x10,        # Load from memory
        "CALL": 0x11,         # Call contract
        "RETURN": 0x12,       # Return from contract
        "SHA256": 0x13,       # Compute SHA-256 hash
        "LOG": 0x14,          # Log a message
        "ASSERT": 0x15,       # Assert condition
        "HALT": 0x16,         # Halt execution
    }
    
    GAS_COSTS = {
        "NOP": 1,
        "PUSH": 2,
        "POP": 1,
        "ADD": 3,
        "SUB": 3,
        "MUL": 5,
        "DIV": 5,
        "EQ": 3,
        "LT": 3,
        "GT": 3,
        "JMP": 2,
        "JMPIF": 4,
        "JMPIFNOT": 4,
        "STORE": 10,
        "LOAD": 5,
        "MSTORE": 3,
        "MLOAD": 2,
        "CALL": 100,
        "RETURN": 5,
        "SHA256": 20,
        "LOG": 5,
        "ASSERT": 1,
        "HALT": 1,
    }
    
    # Reverse opcode mapping for debugging
    OPCODE_NAMES = {v: k for k, v in OPCODES.items()}
    
    def __init__(self, max_gas: int = 1000000):
        """
        Initialize a new VirtualMachine instance.
        
        Args:
            max_gas: Maximum gas allowed per execution
        """
        self.memory = {}
        self.stack = []
        self.storage = {}
        self.pc = 0
        self.running = False
        self.gas_used = 0
        self.max_gas = max_gas
        self.logger = get_logger(__name__)
    
    def reset(self):
        """Reset VM state."""
        self.memory = {}
        self.stack = []
        self.storage = {}
        self.pc = 0
        self.running = False
        self.gas_used = 0
    
    def _check_gas(self, cost: int) -> bool:
        """
        Check if there's enough gas for the operation.
        
        Args:
            cost: Gas cost
            
        Returns:
            True if there's enough gas, False otherwise
        """
        if self.gas_used + cost > self.max_gas:
            self.logger.warning(f"Out of gas: {self.gas_used} + {cost} > {self.max_gas}")
            return False
        return True
    
    def _consume_gas(self, cost: int):
        """Consume gas for an operation."""
        self.gas_used += cost
    
    def execute_bytecode(self, bytecode: str) -> Any:
        """
        Execute bytecode.
        
        Args:
            bytecode: Bytecode to execute
            
        Returns:
            Execution result
        """
        self.reset()
        self.running = True
        
        try:
            # Convert bytecode string to list of integers
            instructions = self._parse_bytecode(bytecode)
            
            while self.running and self.pc < len(instructions):
                opcode = instructions[self.pc]
                self.pc += 1
                
                if opcode == self.OPCODES["NOP"]:
                    self._execute_nop()
                elif opcode == self.OPCODES["PUSH"]:
                    self._execute_push(instructions)
                elif opcode == self.OPCODES["POP"]:
                    self._execute_pop()
                elif opcode == self.OPCODES["ADD"]:
                    self._execute_add()
                elif opcode == self.OPCODES["SUB"]:
                    self._execute_sub()
                elif opcode == self.OPCODES["MUL"]:
                    self._execute_mul()
                elif opcode == self.OPCODES["DIV"]:
                    self._execute_div()
                elif opcode == self.OPCODES["EQ"]:
                    self._execute_eq()
                elif opcode == self.OPCODES["LT"]:
                    self._execute_lt()
                elif opcode == self.OPCODES["GT"]:
                    self._execute_gt()
                elif opcode == self.OPCODES["JMP"]:
                    self._execute_jmp(instructions)
                elif opcode == self.OPCODES["JMPIF"]:
                    self._execute_jmpif(instructions)
                elif opcode == self.OPCODES["JMPIFNOT"]:
                    self._execute_jmpifnot(instructions)
                elif opcode == self.OPCODES["STORE"]:
                    self._execute_store()
                elif opcode == self.OPCODES["LOAD"]:
                    self._execute_load()
                elif opcode == self.OPCODES["MSTORE"]:
                    self._execute_mstore()
                elif opcode == self.OPCODES["MLOAD"]:
                    self._execute_mload()
                elif opcode == self.OPCODES["CALL"]:
                    self._execute_call(instructions)
                elif opcode == self.OPCODES["RETURN"]:
                    return self._execute_return()
                elif opcode == self.OPCODES["SHA256"]:
                    self._execute_sha256()
                elif opcode == self.OPCODES["LOG"]:
                    self._execute_log(instructions)
                elif opcode == self.OPCODES["ASSERT"]:
                    self._execute_assert(instructions)
                elif opcode == self.OPCODES["HALT"]:
                    self._execute_halt()
                else:
                    raise ValueError(f"Unknown opcode: {opcode}")
        
        except Exception as e:
            self.logger.error(f"Execution error: {e}")
            self.running = False
            return {"success": False, "error": str(e), "gas_used": self.gas_used}
        
        return {"success": True, "result": self.stack[-1] if self.stack else None, "gas_used": self.gas_used}
    
    def _parse_bytecode(self, bytecode: str) -> List[int]:
        """
        Parse bytecode string to list of integers.
        
        Args:
            bytecode: Bytecode string
            
        Returns:
            List of instructions
        """
        try:
            if isinstance(bytecode, str) and bytecode.strip():
                # Try to parse hex string
                return bytes.fromhex(bytecode.strip())
            elif isinstance(bytecode, bytes):
                return list(bytecode)
            elif isinstance(bytecode, list):
                return bytecode
            
            raise ValueError("Unsupported bytecode format")
        
        except Exception as e:
            raise ValueError(f"Failed to parse bytecode: {e}")
    
    def _execute_nop(self):
        """Execute NOP operation."""
        if not self._check_gas(self.GAS_COSTS["NOP"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["NOP"])
    
    def _execute_push(self, instructions: List[int]):
        """Execute PUSH operation."""
        if not self._check_gas(self.GAS_COSTS["PUSH"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["PUSH"])
        
        value = instructions[self.pc]
        self.pc += 1
        self.stack.append(value)
    
    def _execute_pop(self):
        """Execute POP operation."""
        if not self._check_gas(self.GAS_COSTS["POP"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["POP"])
        
        if self.stack:
            self.stack.pop()
    
    def _execute_add(self):
        """Execute ADD operation."""
        if not self._check_gas(self.GAS_COSTS["ADD"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["ADD"])
        
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(a + b)
    
    def _execute_sub(self):
        """Execute SUB operation."""
        if not self._check_gas(self.GAS_COSTS["SUB"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["SUB"])
        
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(a - b)
    
    def _execute_mul(self):
        """Execute MUL operation."""
        if not self._check_gas(self.GAS_COSTS["MUL"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["MUL"])
        
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(a * b)
    
    def _execute_div(self):
        """Execute DIV operation."""
        if not self._check_gas(self.GAS_COSTS["DIV"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["DIV"])
        
        a = self.stack.pop()
        b = self.stack.pop()
        
        if b == 0:
            raise Exception("Division by zero")
        
        self.stack.append(a / b)
    
    def _execute_eq(self):
        """Execute EQ operation."""
        if not self._check_gas(self.GAS_COSTS["EQ"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["EQ"])
        
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(1 if a == b else 0)
    
    def _execute_lt(self):
        """Execute LT operation."""
        if not self._check_gas(self.GAS_COSTS["LT"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["LT"])
        
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(1 if a < b else 0)
    
    def _execute_gt(self):
        """Execute GT operation."""
        if not self._check_gas(self.GAS_COSTS["GT"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["GT"])
        
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(1 if a > b else 0)
    
    def _execute_jmp(self, instructions: List[int]):
        """Execute JMP operation."""
        if not self._check_gas(self.GAS_COSTS["JMP"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["JMP"])
        
        target = instructions[self.pc]
        self.pc = target
    
    def _execute_jmpif(self, instructions: List[int]):
        """Execute JMPIF operation."""
        if not self._check_gas(self.GAS_COSTS["JMPIF"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["JMPIF"])
        
        condition = self.stack.pop()
        target = instructions[self.pc]
        self.pc += 1
        
        if condition != 0:
            self.pc = target
    
    def _execute_jmpifnot(self, instructions: List[int]):
        """Execute JMPIFNOT operation."""
        if not self._check_gas(self.GAS_COSTS["JMPIFNOT"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["JMPIFNOT"])
        
        condition = self.stack.pop()
        target = instructions[self.pc]
        self.pc += 1
        
        if condition == 0:
            self.pc = target
    
    def _execute_store(self):
        """Execute STORE operation."""
        if not self._check_gas(self.GAS_COSTS["STORE"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["STORE"])
        
        value = self.stack.pop()
        key = self.stack.pop()
        self.storage[key] = value
    
    def _execute_load(self):
        """Execute LOAD operation."""
        if not self._check_gas(self.GAS_COSTS["LOAD"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["LOAD"])
        
        key = self.stack.pop()
        self.stack.append(self.storage.get(key, 0))
    
    def _execute_mstore(self):
        """Execute MSTORE operation."""
        if not self._check_gas(self.GAS_COSTS["MSTORE"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["MSTORE"])
        
        value = self.stack.pop()
        key = self.stack.pop()
        self.memory[key] = value
    
    def _execute_mload(self):
        """Execute MLOAD operation."""
        if not self._check_gas(self.GAS_COSTS["MLOAD"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["MLOAD"])
        
        key = self.stack.pop()
        self.stack.append(self.memory.get(key, 0))
    
    def _execute_call(self, instructions: List[int]):
        """Execute CALL operation."""
        if not self._check_gas(self.GAS_COSTS["CALL"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["CALL"])
        
        contract_address = instructions[self.pc]
        self.pc += 1
        
        # For now, just simulate a call
        self.logger.debug(f"Calling contract at address: {contract_address}")
    
    def _execute_return(self) -> Dict:
        """Execute RETURN operation."""
        if not self._check_gas(self.GAS_COSTS["RETURN"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["RETURN"])
        
        self.running = False
        return {"success": True, "result": self.stack[-1] if self.stack else None, "gas_used": self.gas_used}
    
    def _execute_sha256(self):
        """Execute SHA256 operation."""
        if not self._check_gas(self.GAS_COSTS["SHA256"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["SHA256"])
        
        value = self.stack.pop()
        hash_result = sha256_hash(str(value))
        self.stack.append(int(hash_result, 16))
    
    def _execute_log(self, instructions: List[int]):
        """Execute LOG operation."""
        if not self._check_gas(self.GAS_COSTS["LOG"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["LOG"])
        
        message = instructions[self.pc]
        self.pc += 1
        self.logger.info(f"Contract log: {message}")
    
    def _execute_assert(self, instructions: List[int]):
        """Execute ASSERT operation."""
        if not self._check_gas(self.GAS_COSTS["ASSERT"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["ASSERT"])
        
        condition = self.stack.pop()
        if condition == 0:
            raise Exception("Assertion failed")
    
    def _execute_halt(self):
        """Execute HALT operation."""
        if not self._check_gas(self.GAS_COSTS["HALT"]):
            raise Exception("Out of gas")
        self._consume_gas(self.GAS_COSTS["HALT"])
        
        self.running = False
    
    def get_vm_state(self) -> Dict:
        """
        Get VM state information.
        
        Returns:
            VM state information
        """
        return {
            "pc": self.pc,
            "stack": self.stack.copy(),
            "memory": self.memory.copy(),
            "storage": self.storage.copy(),
            "gas_used": self.gas_used,
            "max_gas": self.max_gas,
            "running": self.running
        }
    
    def get_gas_info(self) -> Dict:
        """
        Get gas information.
        
        Returns:
            Gas information
        """
        remaining = self.max_gas - self.gas_used
        percentage = (self.gas_used / self.max_gas) * 100 if self.max_gas > 0 else 0
        
        return {
            "used": self.gas_used,
            "remaining": remaining,
            "max": self.max_gas,
            "percentage": percentage
        }
    
    def get_memory_info(self) -> Dict:
        """
        Get memory information.
        
        Returns:
            Memory information
        """
        return {
            "size": len(self.memory),
            "keys": list(self.memory.keys()),
            "max_key": max(self.memory.keys()) if self.memory else 0
        }
    
    def get_stack_info(self) -> Dict:
        """
        Get stack information.
        
        Returns:
            Stack information
        """
        return {
            "size": len(self.stack),
            "depth": len(self.stack),
            "elements": self.stack.copy()
        }
    
    def get_storage_info(self) -> Dict:
        """
        Get storage information.
        
        Returns:
            Storage information
        """
        return {
            "size": len(self.storage),
            "keys": list(self.storage.keys()),
            "values": list(self.storage.values())
        }
    
    def __repr__(self):
        """String representation of VM."""
        return f"VirtualMachine(running={self.running}, gas={self.gas_used}/{self.max_gas})"
    
    def __str__(self):
        """String representation for printing."""
        state = self.get_vm_state()
        return (
            f"Virtual Machine State\n"
            f"=====================\n"
            f"Running: {state['running']}\n"
            f"Program Counter: {state['pc']}\n"
            f"Stack Size: {len(state['stack'])}\n"
            f"Stack: {state['stack']}\n"
            f"Memory Size: {len(state['memory'])}\n"
            f"Storage Size: {len(state['storage'])}\n"
            f"Gas Used: {state['gas_used']}/{state['max_gas']}"
        )
