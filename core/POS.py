from core.SHA_256 import sha256_hash
import time
import random

class Validator:
    """
    Represents a validator in the PoS consensus mechanism.
    """
    def __init__(self, address, stake):
        """
        Initialize a new validator.
        
        Args:
            address: Unique identifier of the validator
            stake: Amount of coins staked by the validator
        """
        self.address = address
        self.stake = stake
        self.total_blocks_forged = 0
        self.reputation = 1.0  # Reputation affects validator selection (0.5 to 1.5)

    def increase_reputation(self, amount=0.01):
        """Increase validator's reputation."""
        self.reputation = min(1.5, self.reputation + amount)

    def decrease_reputation(self, amount=0.01):
        """Decrease validator's reputation."""
        self.reputation = max(0.5, self.reputation - amount)

    def forge_block(self):
        """Mark that the validator forged a block successfully."""
        self.total_blocks_forged += 1
        self.increase_reputation()

    def __str__(self):
        """String representation of the validator."""
        return (
            f"Validator: {self.address}\n"
            f"Stake: {self.stake} coins\n"
            f"Blocks Forged: {self.total_blocks_forged}\n"
            f"Reputation: {self.reputation:.2f}"
        )


class POSBlock:
    """
    Represents a block in the blockchain for PoS consensus mechanism.
    """
    def __init__(self, index, previous_hash, transactions, timestamp, validator):
        """
        Initialize a new block.
        
        Args:
            index: Block index in the chain
            previous_hash: Hash of the previous block
            transactions: List of transactions in this block
            timestamp: Time when the block was created
            validator: The validator who forged this block
        """
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp
        self.validator = validator
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calculate the hash of the block using all its fields."""
        block_data = (
            str(self.index) +
            str(self.previous_hash) +
            str(self.transactions) +
            str(self.timestamp) +
            str(self.validator.address)
        )
        return sha256_hash(block_data)

    def __str__(self):
        """String representation of the block."""
        return (
            f"Block {self.index}\n"
            f"Previous Hash: {self.previous_hash[:16]}...\n"
            f"Transactions: {len(self.transactions)}\n"
            f"Timestamp: {self.timestamp}\n"
            f"Validator: {self.validator.address}\n"
            f"Hash: {self.hash[:16]}..."
        )


class ProofOfStake:
    """
    Implementation of Proof-of-Stake consensus mechanism.
    
    PoS uses staked coins to select validators to forge new blocks. Validators
    are chosen based on their stake and reputation, making it energy-efficient
    compared to PoW.
    """
    def __init__(self, initial_validators=None, inflation_rate=0.02):
        """
        Initialize the PoS algorithm.
        
        Args:
            initial_validators: List of initial validators with their stakes
            inflation_rate: Annual inflation rate for staking rewards (2%)
        """
        self.chain = []
        self.current_transactions = []
        self.validators = []
        self.inflation_rate = inflation_rate

        if initial_validators:
            for address, stake in initial_validators:
                self.validators.append(Validator(address, stake))

        self.create_genesis_block()

    def create_genesis_block(self):
        """Create the first block in the chain (genesis block)."""
        # If no validators, create a default one
        if not self.validators:
            self.validators.append(Validator("genesis", 1000))

        genesis_block = POSBlock(
            index=0,
            previous_hash="0",
            transactions=["Genesis Block"],
            timestamp=time.time(),
            validator=self.validators[0]
        )
        self.chain.append(genesis_block)
        self.validators[0].forge_block()

    def add_transaction(self, transaction):
        """
        Add a transaction to the current list of pending transactions.
        
        Args:
            transaction: Transaction to be added
        """
        self.current_transactions.append(transaction)

    def select_validator(self):
        """
        Select a validator based on stake and reputation.
        
        Returns:
            The selected validator
        """
        if not self.validators:
            return None

        # Calculate total stake with reputation factor
        total_weight = sum(validator.stake * validator.reputation for validator in self.validators)

        # Select validator randomly based on weighted probability
        random_value = random.uniform(0, total_weight)
        current_weight = 0

        for validator in self.validators:
            current_weight += validator.stake * validator.reputation
            if random_value <= current_weight:
                return validator

        # Fallback to first validator if selection fails
        return self.validators[0]

    def calculate_reward(self, validator, block):
        """
        Calculate staking reward for a validator.
        
        Args:
            validator: The validator who forged the block
            block: The block that was forged
            
        Returns:
            Reward amount in coins
        """
        # Reward is based on stake and inflation rate, multiplied by block difficulty factor
        base_reward = validator.stake * (self.inflation_rate / 365)  # Daily inflation
        transaction_reward = len(block.transactions) * 0.1  # 0.1 coins per transaction fee
        reputation_bonus = base_reward * (validator.reputation - 1)  # Bonus for higher reputation

        return base_reward + transaction_reward + reputation_bonus

    def forge_block(self):
        """
        Forge a new block using the PoS algorithm.
        
        Returns:
            The newly forged block
        """
        if not self.current_transactions:
            print("No transactions to forge.")
            return None

        # Select validator
        validator = self.select_validator()
        if not validator:
            print("No validators available to forge block.")
            return None

        print(f"🔐 Validator {validator.address} selected to forge block")

        # Create new block
        previous_block = self.chain[-1]
        new_block = POSBlock(
            index=previous_block.index + 1,
            previous_hash=previous_block.hash,
            transactions=self.current_transactions.copy(),
            timestamp=time.time(),
            validator=validator
        )

        # Simulate block forging time
        forging_time = random.uniform(0.5, 2.0)
        time.sleep(forging_time)

        print(f"✅ Block {new_block.index} forged successfully!")
        print(f"⏱️  Forging Time: {forging_time:.2f} seconds")
        print(f"🎯 Hash: {new_block.hash[:16]}...")

        # Calculate and distribute reward
        reward = self.calculate_reward(validator, new_block)
        validator.stake += reward

        # Mark block as forged and update reputation
        validator.forge_block()
        reward_transaction = f"Reward: {reward:.2f} coins to {validator.address}"
        self.current_transactions = [reward_transaction]

        # Add new block to the chain
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self):
        """
        Verify the entire blockchain's validity.
        
        Returns:
            True if the chain is valid, False otherwise
        """
        previous_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            current_block = self.chain[block_index]

            # Check hash
            if current_block.hash != current_block.calculate_hash():
                print(f"❌ Invalid hash at block {block_index}")
                return False

            # Check previous hash reference
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Invalid previous hash at block {block_index}")
                return False

            # Verify validator exists
            validator_exists = any(v.address == current_block.validator.address for v in self.validators)
            if not validator_exists:
                print(f"❌ Invalid validator at block {block_index}")
                return False

            previous_block = current_block
            block_index += 1

        return True

    def add_validator(self, address, stake):
        """
        Add a new validator to the network.
        
        Args:
            address: Address of the new validator
            stake: Amount of coins the validator is staking
        """
        # Check if validator already exists
        if any(v.address == address for v in self.validators):
            print(f"Validator {address} already exists.")
            return False

        self.validators.append(Validator(address, stake))
        return True

    def get_network_info(self):
        """Get information about the PoS network."""
        total_stake = sum(validator.stake for validator in self.validators)
        avg_reputation = sum(validator.reputation for validator in self.validators) / len(self.validators)
        total_blocks = sum(validator.total_blocks_forged for validator in self.validators)

        return {
            "chain_length": len(self.chain),
            "total_transactions": sum(len(block.transactions) for block in self.chain),
            "total_validators": len(self.validators),
            "total_stake": total_stake,
            "average_reputation": avg_reputation,
            "total_blocks_forged": total_blocks,
            "chain_validity": self.is_chain_valid()
        }

    def __str__(self):
        """String representation of the PoS blockchain."""
        info = self.get_network_info()
        return (
            f"Proof-of-Stake Blockchain\n"
            f"=========================\n"
            f"Chain Length: {info['chain_length']} blocks\n"
            f"Total Transactions: {info['total_transactions']}\n"
            f"Validators: {info['total_validators']}\n"
            f"Total Stake: {info['total_stake']:.2f} coins\n"
            f"Avg Reputation: {info['average_reputation']:.2f}\n"
            f"Blocks Forged: {info['total_blocks_forged']}\n"
            f"Chain Valid: {info['chain_validity']}\n"
            f"Latest Block Hash: {self.chain[-1].hash[:16]}..."
        )


# Example Usage
if __name__ == "__main__":
    print("=== Proof-of-Stake Blockchain Example ===\n")

    # Create initial validators
    initial_validators = [
        ("validator1", 500),
        ("validator2", 300),
        ("validator3", 200),
        ("validator4", 150)
    ]

    # Create PoS blockchain
    pos_blockchain = ProofOfStake(initial_validators, inflation_rate=0.02)
    print(f"Initial Network Info:\n{pos_blockchain}\n")

    # Add some transactions
    print("Adding transactions...")
    for i in range(4):
        transaction = f"Transaction {i+1}: User{random.randint(1,100)} -> User{random.randint(1,100)}"
        pos_blockchain.add_transaction(transaction)

    # Forge a new block
    print("\nStarting forging process...")
    new_block = pos_blockchain.forge_block()
    print()

    # Check chain validity
    print("Checking blockchain validity:", pos_blockchain.is_chain_valid())

    # Show validators info
    print("\n=== Validators Info ===")
    for validator in pos_blockchain.validators:
        print(f"\n{validator}")

    # Show the blockchain
    print("\n=== Blockchain ===")
    for block in pos_blockchain.chain:
        print(f"\n{block}")
