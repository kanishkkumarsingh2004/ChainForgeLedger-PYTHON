from core.SHA_256 import sha256_hash
import time
import random

class Block:
    """
    Represents a block in the blockchain for PoW consensus mechanism.
    """
    def __init__(self, index, previous_hash, transactions, timestamp, nonce=0):
        """
        Initialize a new block.
        
        Args:
            index: Block index in the chain
            previous_hash: Hash of the previous block
            transactions: List of transactions in this block
            timestamp: Time when the block was created
            nonce: Number used once for mining
        """
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calculate the hash of the block using all its fields."""
        block_data = (
            str(self.index) +
            str(self.previous_hash) +
            str(self.transactions) +
            str(self.timestamp) +
            str(self.nonce)
        )
        return sha256_hash(block_data)

    def __str__(self):
        """String representation of the block."""
        return (
            f"Block {self.index}\n"
            f"Previous Hash: {self.previous_hash[:16]}...\n"
            f"Transactions: {len(self.transactions)}\n"
            f"Timestamp: {self.timestamp}\n"
            f"Nonce: {self.nonce}\n"
            f"Hash: {self.hash[:16]}..."
        )


class ProofOfWork:
    """
    Implementation of Proof-of-Work consensus mechanism.
    
    PoW requires miners to solve a complex cryptographic puzzle to validate
    transactions and secure the network. The solution is easy to verify but
    computationally expensive to find.
    """
    def __init__(self, difficulty=4):
        """
        Initialize the PoW algorithm.
        
        Args:
            difficulty: Number of leading zeros required in the hash
        """
        self.difficulty = difficulty
        self.chain = []
        self.current_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """Create the first block in the chain (genesis block)."""
        genesis_block = Block(
            index=0,
            previous_hash="0",
            transactions=["Genesis Block"],
            timestamp=time.time(),
            nonce=0
        )
        self.chain.append(genesis_block)

    def add_transaction(self, transaction):
        """
        Add a transaction to the current list of pending transactions.
        
        Args:
            transaction: Transaction to be added
        """
        self.current_transactions.append(transaction)

    def mine_block(self, miner_address):
        """
        Mine a new block using the PoW algorithm.
        
        Args:
            miner_address: Address of the miner who will receive the reward
            
        Returns:
            The newly mined block
        """
        if not self.current_transactions:
            print("No transactions to mine.")
            return None

        # Create new block
        previous_block = self.chain[-1]
        new_block = Block(
            index=previous_block.index + 1,
            previous_hash=previous_block.hash,
            transactions=self.current_transactions.copy(),
            timestamp=time.time(),
            nonce=0
        )

        # Mine the block
        print(f"🔨 Mining block {new_block.index} with difficulty {self.difficulty}...")
        start_time = time.time()

        while True:
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()

            # Check if hash meets difficulty requirement
            if new_block.hash.startswith("0" * self.difficulty):
                mining_time = time.time() - start_time
                print(f"✅ Block {new_block.index} mined successfully!")
                print(f"⏱️  Mining Time: {mining_time:.2f} seconds")
                print(f"⛏️  Nonce: {new_block.nonce}")
                print(f"🎯 Hash: {new_block.hash[:16]}...")

                # Add mining reward
                reward_transaction = f"Reward: 50 coins to {miner_address}"
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

            # Check difficulty requirement
            if not current_block.hash.startswith("0" * self.difficulty):
                print(f"❌ Hash does not meet difficulty requirement at block {block_index}")
                return False

            previous_block = current_block
            block_index += 1

        return True

    def get_blockchain_info(self):
        """Get information about the blockchain."""
        info = {
            "length": len(self.chain),
            "difficulty": self.difficulty,
            "total_transactions": sum(len(block.transactions) for block in self.chain),
            "chain_validity": self.is_chain_valid()
        }
        return info

    def __str__(self):
        """String representation of the PoW blockchain."""
        info = self.get_blockchain_info()
        return (
            f"Proof-of-Work Blockchain\n"
            f"========================\n"
            f"Length: {info['length']} blocks\n"
            f"Difficulty: {info['difficulty']}\n"
            f"Total Transactions: {info['total_transactions']}\n"
            f"Chain Valid: {info['chain_validity']}\n"
            f"Latest Block Hash: {self.chain[-1].hash[:16]}..."
        )


# Example Usage
if __name__ == "__main__":
    print("=== Proof-of-Work Blockchain Example ===\n")

    # Create a PoW blockchain with difficulty 4
    pow_blockchain = ProofOfWork(difficulty=4)
    print(f"Initial Blockchain Info:\n{pow_blockchain}\n")

    # Add some transactions
    print("Adding transactions...")
    for i in range(3):
        transaction = f"Transaction {i+1}: User{random.randint(1,100)} -> User{random.randint(1,100)}"
        pow_blockchain.add_transaction(transaction)

    # Mine a new block
    print("\nStarting mining process...")
    miner_address = "miner1@example.com"
    new_block = pow_blockchain.mine_block(miner_address)
    print()

    # Check chain validity
    print("Checking blockchain validity:", pow_blockchain.is_chain_valid())

    # Show the blockchain
    print("\n=== Blockchain ===")
    for block in pow_blockchain.chain:
        print(f"\n{block}")
