#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparison test between Proof-of-Work and Proof-of-Stake consensus mechanisms.
This script demonstrates the differences in performance, energy efficiency,
and security characteristics of both consensus algorithms.
"""

import sys
import time
import random
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from core.POW import ProofOfWork
from core.POS import ProofOfStake


def test_pow_performance(difficulty=4, transactions=5):
    """
    Test PoW performance with specific difficulty and transaction count.
    
    Args:
        difficulty: Number of leading zeros required
        transactions: Number of transactions per block
        
    Returns:
        Dictionary containing performance metrics
    """
    print(f"Testing PoW with difficulty {difficulty}, {transactions} transactions...")
    
    pow_chain = ProofOfWork(difficulty=difficulty)
    
    # Add transactions
    for i in range(transactions):
        transaction = f"Tx{i+1}: User{random.randint(1,100)} -> User{random.randint(1,100)}"
        pow_chain.add_transaction(transaction)
    
    # Mine block and measure time
    start_time = time.time()
    pow_chain.mine_block("pow_miner@example.com")
    mining_time = time.time() - start_time
    
    # Get last block info
    last_block = pow_chain.chain[-1]
    
    return {
        "algorithm": "Proof-of-Work",
        "difficulty": difficulty,
        "transactions": transactions,
        "time": mining_time,
        "hash": last_block.hash,
        "nonce": last_block.nonce,
        "valid": pow_chain.is_chain_valid()
    }


def test_pos_performance(validators=4, transactions=5):
    """
    Test PoS performance with specific number of validators and transaction count.
    
    Args:
        validators: Number of validators
        transactions: Number of transactions per block
        
    Returns:
        Dictionary containing performance metrics
    """
    print(f"Testing PoS with {validators} validators, {transactions} transactions...")
    
    # Create validators with random stakes
    initial_validators = []
    for i in range(validators):
        stake = random.randint(100, 500)
        initial_validators.append((f"validator{i+1}", stake))
    
    pos_chain = ProofOfStake(initial_validators, inflation_rate=0.02)
    
    # Add transactions
    for i in range(transactions):
        transaction = f"Tx{i+1}: User{random.randint(1,100)} -> User{random.randint(1,100)}"
        pos_chain.add_transaction(transaction)
    
    # Forge block and measure time
    start_time = time.time()
    pos_chain.forge_block()
    forging_time = time.time() - start_time
    
    # Get last block info
    last_block = pos_chain.chain[-1]
    
    return {
        "algorithm": "Proof-of-Stake",
        "validators": validators,
        "transactions": transactions,
        "time": forging_time,
        "hash": last_block.hash,
        "validator": last_block.validator.address,
        "valid": pos_chain.is_chain_valid()
    }


def main():
    """Main comparison test function"""
    print("=== PoW vs PoS Consensus Mechanism Comparison ===")
    print("=" * 70)
    
    # Test with medium difficulty and transaction count
    print("\n1. Performance Comparison (4 transactions):")
    pow_result = test_pow_performance(difficulty=4, transactions=4)
    pos_result = test_pos_performance(validators=4, transactions=4)
    
    print()
    print("=" * 70)
    print(f"| Algorithm       | Time (s)  | Hash (first 16)    | Details               | Valid |")
    print("=" * 70)
    print(f"| PoW (diff=4)    | {pow_result['time']:.2f}  | {pow_result['hash'][:16]} | Nonce: {pow_result['nonce']} | {pow_result['valid']}    |")
    print(f"| PoS (4 valid)   | {pos_result['time']:.2f}  | {pos_result['hash'][:16]} | Validator: {pos_result['validator']} | {pos_result['valid']}    |")
    print("=" * 70)
    
    # Test PoW with increasing difficulty
    print("\n2. PoW Performance with Increasing Difficulty:")
    difficulties = [3, 4, 5]
    results = []
    
    for difficulty in difficulties:
        result = test_pow_performance(difficulty=difficulty, transactions=3)
        results.append(result)
    
    print()
    print("=" * 60)
    print(f"| Difficulty | Time (s)  | Hash (first 16)    | Nonce      | Valid |")
    print("=" * 60)
    for result in results:
        print(f"| {result['difficulty']:10} | {result['time']:.2f}  | {result['hash'][:16]} | {result['nonce']:8} | {result['valid']}    |")
    print("=" * 60)
    
    # Test PoS with varying number of validators
    print("\n3. PoS Performance with Varying Validators:")
    validator_counts = [2, 4, 8]
    results = []
    
    for count in validator_counts:
        result = test_pos_performance(validators=count, transactions=3)
        results.append(result)
    
    print()
    print("=" * 70)
    print(f"| Validators | Time (s)  | Hash (first 16)    | Validator           | Valid |")
    print("=" * 70)
    for result in results:
        print(f"| {result['validators']:10} | {result['time']:.2f}  | {result['hash'][:16]} | {result['validator']:18} | {result['valid']}    |")
    print("=" * 70)
    
    print("\n=== Analysis ===")
    print()
    print("📊 Key Observations:")
    print()
    print("1. **Performance**: PoS is significantly faster than PoW, especially at higher difficulties")
    print("2. **Scalability**: PoW performance degrades exponentially with increasing difficulty")
    print("3. **Energy Efficiency**: PoS requires minimal computational effort compared to PoW")
    print("4. **Security**: PoW provides strong network security through computational expenditure")
    print("5. **Decentralization**: PoW allows anyone to mine, while PoS is influenced by stake distribution")
    print()
    print("💡 Conclusion:")
    print("PoW excels in security and decentralization (e.g., Bitcoin), while PoS offers better scalability")
    print("and energy efficiency (e.g., Ethereum 2.0). The choice depends on network requirements.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
