"""
ChainForgeLedger Database Module

Database abstraction layer for blockchain data storage.
"""

import json
import sqlite3
import threading
from typing import Dict, List, Optional
from chainforgeledger.utils.logger import get_logger


class Database:
    """
    Database abstraction layer for blockchain operations.
    
    Provides a unified interface for different database implementations.
    """
    
    def __init__(self, db_path: str = "chainforgeledger.db"):
        """
        Initialize database.
        
        Args:
            db_path: Database file path
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.lock = threading.Lock()
        self.logger = get_logger(__name__)
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            self.logger.debug(f"Connected to database: {self.db_path}")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables."""
        try:
            # Blocks table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_index INTEGER UNIQUE NOT NULL,
                    previous_hash TEXT NOT NULL,
                    block_hash TEXT UNIQUE NOT NULL,
                    merkle_root TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    difficulty REAL NOT NULL,
                    nonce INTEGER NOT NULL,
                    transactions TEXT NOT NULL,
                    miner_address TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Transactions table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT UNIQUE NOT NULL,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    amount REAL NOT NULL,
                    fee REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    data TEXT,
                    signature TEXT NOT NULL,
                    block_index INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (block_index) REFERENCES blocks(block_index)
                )
            ''')
            
            # State table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS state (
                    address TEXT PRIMARY KEY,
                    balance REAL NOT NULL DEFAULT 0,
                    nonce INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Contracts table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS contracts (
                    contract_address TEXT PRIMARY KEY,
                    source_code TEXT NOT NULL,
                    bytecode TEXT NOT NULL,
                    language TEXT NOT NULL,
                    compiler_options TEXT,
                    deployed_at REAL NOT NULL,
                    state TEXT NOT NULL DEFAULT 'deployed',
                    bytecode_hash TEXT NOT NULL,
                    source_code_hash TEXT NOT NULL,
                    updated_at REAL,
                    deactivated_at REAL,
                    activated_at REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Contract storage table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS contract_storage (
                    contract_address TEXT,
                    storage_key TEXT,
                    storage_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (contract_address, storage_key),
                    FOREIGN KEY (contract_address) REFERENCES contracts(contract_address)
                )
            ''')
            
            # Wallets table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS wallets (
                    address TEXT PRIMARY KEY,
                    public_key TEXT NOT NULL,
                    private_key TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Nodes table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY,
                    address TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    last_seen REAL,
                    is_connected INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Mempool table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS mempool (
                    transaction_id TEXT PRIMARY KEY,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    amount REAL NOT NULL,
                    fee REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    data TEXT,
                    signature TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Stats table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.connection.commit()
            self.logger.debug("Database tables created/verified")
        
        except Exception as e:
            self.logger.error(f"Table creation failed: {e}")
            self.connection.rollback()
            raise
    
    # Block operations
    def save_block(self, block_data: Dict) -> int:
        """
        Save block to database.
        
        Args:
            block_data: Block data dictionary
            
        Returns:
            Number of affected rows
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO blocks (
                        block_index, previous_hash, block_hash, merkle_root,
                        timestamp, difficulty, nonce, transactions,
                        miner_address, hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    block_data['block_index'],
                    block_data['previous_hash'],
                    block_data['block_hash'],
                    block_data['merkle_root'],
                    block_data['timestamp'],
                    block_data['difficulty'],
                    block_data['nonce'],
                    json.dumps(block_data['transactions']),
                    block_data['miner_address'],
                    block_data['block_hash']
                ))
                
                self.connection.commit()
                return self.cursor.rowcount
                
        except Exception as e:
            self.logger.error(f"Failed to save block: {e}")
            self.connection.rollback()
            raise
    
    def get_block(self, block_index: int) -> Optional[Dict]:
        """
        Get block by index.
        
        Args:
            block_index: Block index
            
        Returns:
            Block data or None
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM blocks WHERE block_index = ?
                ''', (block_index,))
                
                row = self.cursor.fetchone()
                if row:
                    return self._row_to_block(row)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get block: {e}")
            return None
    
    def get_block_by_hash(self, block_hash: str) -> Optional[Dict]:
        """
        Get block by hash.
        
        Args:
            block_hash: Block hash
            
        Returns:
            Block data or None
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM blocks WHERE block_hash = ?
                ''', (block_hash,))
                
                row = self.cursor.fetchone()
                if row:
                    return self._row_to_block(row)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get block by hash: {e}")
            return None
    
    def get_last_block(self) -> Optional[Dict]:
        """
        Get last block.
        
        Returns:
            Last block data or None
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM blocks ORDER BY block_index DESC LIMIT 1
                ''')
                
                row = self.cursor.fetchone()
                if row:
                    return self._row_to_block(row)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get last block: {e}")
            return None
    
    def get_all_blocks(self) -> List[Dict]:
        """
        Get all blocks.
        
        Returns:
            List of blocks
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM blocks ORDER BY block_index ASC
                ''')
                
                blocks = []
                for row in self.cursor.fetchall():
                    blocks.append(self._row_to_block(row))
                
                return blocks
                
        except Exception as e:
            self.logger.error(f"Failed to get all blocks: {e}")
            return []
    
    def get_blocks_range(self, start_index: int, end_index: int) -> List[Dict]:
        """
        Get blocks in range.
        
        Args:
            start_index: Start block index
            end_index: End block index
            
        Returns:
            List of blocks
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM blocks
                    WHERE block_index BETWEEN ? AND ?
                    ORDER BY block_index ASC
                ''', (start_index, end_index))
                
                blocks = []
                for row in self.cursor.fetchall():
                    blocks.append(self._row_to_block(row))
                
                return blocks
                
        except Exception as e:
            self.logger.error(f"Failed to get blocks range: {e}")
            return []
    
    def get_block_count(self) -> int:
        """
        Get number of blocks.
        
        Returns:
            Block count
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT COUNT(*) FROM blocks
                ''')
                
                return self.cursor.fetchone()[0]
                
        except Exception as e:
            self.logger.error(f"Failed to get block count: {e}")
            return 0
    
    # Transaction operations
    def save_transaction(self, transaction_data: Dict, block_index: int = None):
        """
        Save transaction to database.
        
        Args:
            transaction_data: Transaction data
            block_index: Block index
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO transactions (
                        transaction_id, sender, recipient, amount, fee,
                        timestamp, data, signature, block_index
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction_data['transaction_id'],
                    transaction_data['sender'],
                    transaction_data['recipient'],
                    transaction_data['amount'],
                    transaction_data['fee'],
                    transaction_data['timestamp'],
                    json.dumps(transaction_data.get('data', {})),
                    transaction_data['signature'],
                    block_index
                ))
                
                self.connection.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to save transaction: {e}")
            self.connection.rollback()
            raise
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict]:
        """
        Get transaction by ID.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction data or None
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM transactions WHERE transaction_id = ?
                ''', (transaction_id,))
                
                row = self.cursor.fetchone()
                if row:
                    return self._row_to_transaction(row)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get transaction: {e}")
            return None
    
    def get_transactions_by_block(self, block_index: int) -> List[Dict]:
        """
        Get transactions by block index.
        
        Args:
            block_index: Block index
            
        Returns:
            List of transactions
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM transactions WHERE block_index = ?
                ''', (block_index,))
                
                transactions = []
                for row in self.cursor.fetchall():
                    transactions.append(self._row_to_transaction(row))
                
                return transactions
                
        except Exception as e:
            self.logger.error(f"Failed to get transactions by block: {e}")
            return []
    
    def get_transactions_by_address(self, address: str) -> List[Dict]:
        """
        Get transactions by address.
        
        Args:
            address: Address
            
        Returns:
            List of transactions
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM transactions WHERE sender = ? OR recipient = ?
                ''', (address, address))
                
                transactions = []
                for row in self.cursor.fetchall():
                    transactions.append(self._row_to_transaction(row))
                
                return transactions
                
        except Exception as e:
            self.logger.error(f"Failed to get transactions by address: {e}")
            return []
    
    def get_all_transactions(self) -> List[Dict]:
        """
        Get all transactions.
        
        Returns:
            List of transactions
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM transactions ORDER BY timestamp DESC
                ''')
                
                transactions = []
                for row in self.cursor.fetchall():
                    transactions.append(self._row_to_transaction(row))
                
                return transactions
                
        except Exception as e:
            self.logger.error(f"Failed to get all transactions: {e}")
            return []
    
    # State operations
    def save_state(self, address: str, balance: float, nonce: int = 0):
        """
        Save state.
        
        Args:
            address: Address
            balance: Balance
            nonce: Nonce
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO state (address, balance, nonce, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (address, balance, nonce))
                
                self.connection.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
            self.connection.rollback()
            raise
    
    def get_state(self, address: str) -> Optional[Dict]:
        """
        Get state.
        
        Args:
            address: Address
            
        Returns:
            State data or None
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM state WHERE address = ?
                ''', (address,))
                
                row = self.cursor.fetchone()
                if row:
                    return self._row_to_state(row)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get state: {e}")
            return None
    
    def get_all_states(self) -> List[Dict]:
        """
        Get all states.
        
        Returns:
            List of states
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM state
                ''')
                
                states = []
                for row in self.cursor.fetchall():
                    states.append(self._row_to_state(row))
                
                return states
                
        except Exception as e:
            self.logger.error(f"Failed to get all states: {e}")
            return []
    
    # Contract operations
    def save_contract(self, contract_data: Dict):
        """
        Save contract.
        
        Args:
            contract_data: Contract data
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO contracts (
                        contract_address, source_code, bytecode, language,
                        compiler_options, deployed_at, state, bytecode_hash,
                        source_code_hash, updated_at, deactivated_at, activated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    contract_data['contract_address'],
                    contract_data['source_code'],
                    contract_data['bytecode'],
                    contract_data['language'],
                    json.dumps(contract_data.get('compiler_options', {})),
                    contract_data['deployed_at'],
                    contract_data.get('state', 'deployed'),
                    contract_data['bytecode_hash'],
                    contract_data['source_code_hash'],
                    contract_data.get('updated_at'),
                    contract_data.get('deactivated_at'),
                    contract_data.get('activated_at')
                ))
                
                self.connection.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to save contract: {e}")
            self.connection.rollback()
            raise
    
    def get_contract(self, contract_address: str) -> Optional[Dict]:
        """
        Get contract.
        
        Args:
            contract_address: Contract address
            
        Returns:
            Contract data or None
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM contracts WHERE contract_address = ?
                ''', (contract_address,))
                
                row = self.cursor.fetchone()
                if row:
                    return self._row_to_contract(row)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get contract: {e}")
            return None
    
    def get_all_contracts(self) -> List[Dict]:
        """
        Get all contracts.
        
        Returns:
            List of contracts
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM contracts
                ''')
                
                contracts = []
                for row in self.cursor.fetchall():
                    contracts.append(self._row_to_contract(row))
                
                return contracts
                
        except Exception as e:
            self.logger.error(f"Failed to get all contracts: {e}")
            return []
    
    # Contract storage operations
    def save_contract_storage(self, contract_address: str, storage_key: str, storage_value: str):
        """
        Save contract storage.
        
        Args:
            contract_address: Contract address
            storage_key: Storage key
            storage_value: Storage value
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO contract_storage (
                        contract_address, storage_key, storage_value, updated_at
                    ) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (contract_address, storage_key, storage_value))
                
                self.connection.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to save contract storage: {e}")
            self.connection.rollback()
            raise
    
    def get_contract_storage(self, contract_address: str) -> Dict:
        """
        Get contract storage.
        
        Args:
            contract_address: Contract address
            
        Returns:
            Contract storage
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT storage_key, storage_value FROM contract_storage
                    WHERE contract_address = ?
                ''', (contract_address,))
                
                storage = {}
                for row in self.cursor.fetchall():
                    storage[row['storage_key']] = row['storage_value']
                
                return storage
                
        except Exception as e:
            self.logger.error(f"Failed to get contract storage: {e}")
            return {}
    
    # Wallet operations
    def save_wallet(self, wallet_data: Dict):
        """
        Save wallet.
        
        Args:
            wallet_data: Wallet data
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO wallets (
                        address, public_key, private_key, updated_at
                    ) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    wallet_data['address'],
                    wallet_data['public_key'],
                    wallet_data['private_key']
                ))
                
                self.connection.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to save wallet: {e}")
            self.connection.rollback()
            raise
    
    def get_wallet(self, address: str) -> Optional[Dict]:
        """
        Get wallet.
        
        Args:
            address: Address
            
        Returns:
            Wallet data or None
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM wallets WHERE address = ?
                ''', (address,))
                
                row = self.cursor.fetchone()
                if row:
                    return self._row_to_wallet(row)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get wallet: {e}")
            return None
    
    def get_all_wallets(self) -> List[Dict]:
        """
        Get all wallets.
        
        Returns:
            List of wallets
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM wallets
                ''')
                
                wallets = []
                for row in self.cursor.fetchall():
                    wallets.append(self._row_to_wallet(row))
                
                return wallets
                
        except Exception as e:
            self.logger.error(f"Failed to get all wallets: {e}")
            return []
    
    # Node operations
    def save_node(self, node_data: Dict):
        """
        Save node.
        
        Args:
            node_data: Node data
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO nodes (
                        node_id, address, port, last_seen, is_connected, updated_at
                    ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    node_data['node_id'],
                    node_data['address'],
                    node_data['port'],
                    node_data['last_seen'],
                    node_data['is_connected']
                ))
                
                self.connection.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to save node: {e}")
            self.connection.rollback()
            raise
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """
        Get node.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node data or None
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM nodes WHERE node_id = ?
                ''', (node_id,))
                
                row = self.cursor.fetchone()
                if row:
                    return self._row_to_node(row)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get node: {e}")
            return None
    
    def get_all_nodes(self) -> List[Dict]:
        """
        Get all nodes.
        
        Returns:
            List of nodes
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM nodes
                ''')
                
                nodes = []
                for row in self.cursor.fetchall():
                    nodes.append(self._row_to_node(row))
                
                return nodes
                
        except Exception as e:
            self.logger.error(f"Failed to get all nodes: {e}")
            return []
    
    # Mempool operations
    def save_to_mempool(self, transaction_data: Dict):
        """
        Save transaction to mempool.
        
        Args:
            transaction_data: Transaction data
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO mempool (
                        transaction_id, sender, recipient, amount, fee,
                        timestamp, data, signature
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction_data['transaction_id'],
                    transaction_data['sender'],
                    transaction_data['recipient'],
                    transaction_data['amount'],
                    transaction_data['fee'],
                    transaction_data['timestamp'],
                    json.dumps(transaction_data.get('data', {})),
                    transaction_data['signature']
                ))
                
                self.connection.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to save to mempool: {e}")
            self.connection.rollback()
            raise
    
    def get_mempool_transactions(self) -> List[Dict]:
        """
        Get mempool transactions.
        
        Returns:
            List of mempool transactions
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT * FROM mempool ORDER BY fee DESC
                ''')
                
                transactions = []
                for row in self.cursor.fetchall():
                    transactions.append(self._row_to_mempool_transaction(row))
                
                return transactions
                
        except Exception as e:
            self.logger.error(f"Failed to get mempool transactions: {e}")
            return []
    
    def remove_from_mempool(self, transaction_id: str):
        """
        Remove transaction from mempool.
        
        Args:
            transaction_id: Transaction ID
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    DELETE FROM mempool WHERE transaction_id = ?
                ''', (transaction_id,))
                
                self.connection.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to remove from mempool: {e}")
            self.connection.rollback()
            raise
    
    # Stats operations
    def set_stat(self, key: str, value: str):
        """
        Set statistic.
        
        Args:
            key: Statistic key
            value: Statistic value
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO stats (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value))
                
                self.connection.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to set stat: {e}")
            self.connection.rollback()
            raise
    
    def get_stat(self, key: str) -> Optional[str]:
        """
        Get statistic.
        
        Args:
            key: Statistic key
            
        Returns:
            Statistic value or None
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT value FROM stats WHERE key = ?
                ''', (key,))
                
                row = self.cursor.fetchone()
                return row['value'] if row else None
                
        except Exception as e:
            self.logger.error(f"Failed to get stat: {e}")
            return None
    
    def get_all_stats(self) -> Dict:
        """
        Get all statistics.
        
        Returns:
            Dictionary of all statistics
        """
        try:
            with self.lock:
                self.cursor.execute('''
                    SELECT key, value FROM stats
                ''')
                
                stats = {}
                for row in self.cursor.fetchall():
                    stats[row['key']] = row['value']
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get all stats: {e}")
            return {}
    
    # Helper methods for row conversion
    def _row_to_block(self, row: sqlite3.Row) -> Dict:
        """Convert database row to block dictionary."""
        return {
            'block_index': row['block_index'],
            'previous_hash': row['previous_hash'],
            'block_hash': row['block_hash'],
            'merkle_root': row['merkle_root'],
            'timestamp': row['timestamp'],
            'difficulty': row['difficulty'],
            'nonce': row['nonce'],
            'transactions': json.loads(row['transactions']),
            'miner_address': row['miner_address'],
            'hash': row['hash']
        }
    
    def _row_to_transaction(self, row: sqlite3.Row) -> Dict:
        """Convert database row to transaction dictionary."""
        return {
            'transaction_id': row['transaction_id'],
            'sender': row['sender'],
            'recipient': row['recipient'],
            'amount': row['amount'],
            'fee': row['fee'],
            'timestamp': row['timestamp'],
            'data': json.loads(row['data']) if row['data'] else {},
            'signature': row['signature'],
            'block_index': row['block_index']
        }
    
    def _row_to_state(self, row: sqlite3.Row) -> Dict:
        """Convert database row to state dictionary."""
        return {
            'address': row['address'],
            'balance': row['balance'],
            'nonce': row['nonce'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
    
    def _row_to_contract(self, row: sqlite3.Row) -> Dict:
        """Convert database row to contract dictionary."""
        return {
            'contract_address': row['contract_address'],
            'source_code': row['source_code'],
            'bytecode': row['bytecode'],
            'language': row['language'],
            'compiler_options': json.loads(row['compiler_options']) if row['compiler_options'] else {},
            'deployed_at': row['deployed_at'],
            'state': row['state'],
            'bytecode_hash': row['bytecode_hash'],
            'source_code_hash': row['source_code_hash'],
            'updated_at': row['updated_at'],
            'deactivated_at': row['deactivated_at'],
            'activated_at': row['activated_at'],
            'created_at': row['created_at']
        }
    
    def _row_to_wallet(self, row: sqlite3.Row) -> Dict:
        """Convert database row to wallet dictionary."""
        return {
            'address': row['address'],
            'public_key': row['public_key'],
            'private_key': row['private_key'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
    
    def _row_to_node(self, row: sqlite3.Row) -> Dict:
        """Convert database row to node dictionary."""
        return {
            'node_id': row['node_id'],
            'address': row['address'],
            'port': row['port'],
            'last_seen': row['last_seen'],
            'is_connected': bool(row['is_connected']),
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
    
    def _row_to_mempool_transaction(self, row: sqlite3.Row) -> Dict:
        """Convert database row to mempool transaction dictionary."""
        return {
            'transaction_id': row['transaction_id'],
            'sender': row['sender'],
            'recipient': row['recipient'],
            'amount': row['amount'],
            'fee': row['fee'],
            'timestamp': row['timestamp'],
            'data': json.loads(row['data']) if row['data'] else {},
            'signature': row['signature']
        }
    
    # Database management
    def backup(self, backup_path: str):
        """
        Backup database.
        
        Args:
            backup_path: Backup file path
        """
        try:
            import shutil
            
            self.connection.commit()
            shutil.copy2(self.db_path, backup_path)
            self.logger.debug(f"Database backed up to: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            raise
    
    def restore(self, backup_path: str):
        """
        Restore database from backup.
        
        Args:
            backup_path: Backup file path
        """
        try:
            import shutil
            
            self.connection.close()
            shutil.copy2(backup_path, self.db_path)
            self._connect()
            self.logger.debug(f"Database restored from: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            raise
    
    def vacuum(self):
        """Optimize database."""
        try:
            with self.lock:
                self.cursor.execute('VACUUM')
                self.connection.commit()
                self.logger.debug("Database vacuumed")
                
        except Exception as e:
            self.logger.error(f"Vacuum failed: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            self.logger.debug("Database connection closed")
    
    def __del__(self):
        """Cleanup on destruction."""
        self.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self):
        """String representation."""
        return f"Database(path={self.db_path})"
    
    def __str__(self):
        """String representation for printing."""
        try:
            block_count = self.get_block_count()
            transaction_count = len(self.get_all_transactions())
            contract_count = len(self.get_all_contracts())
            
            return (
                f"ChainForgeLedger Database\n"
                f"==========================\n"
                f"Path: {self.db_path}\n"
                f"Blocks: {block_count}\n"
                f"Transactions: {transaction_count}\n"
                f"Contracts: {contract_count}"
            )
            
        except Exception as e:
            return f"Database({self.db_path}) - Error: {e}"
