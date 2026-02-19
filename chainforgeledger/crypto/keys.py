"""
ChainForgeLedger Key Management Module

Key pair generation and management.
"""

import random
import string
from typing import Tuple
from chainforgeledger.crypto.hashing import  sha256_hash


class KeyPair:
    """
    Represents an RSA-like key pair (simplified).
    
    Attributes:
        public_key: Public key
        private_key: Private key
    """
    
    def __init__(self, public_key: str, private_key: str):
        """
        Initialize a new KeyPair instance.
        
        Args:
            public_key: Public key
            private_key: Private key
        """
        self.public_key = public_key
        self.private_key = private_key
    
    def to_dict(self) -> dict:
        """
        Convert key pair to dictionary.
        
        Returns:
            Dictionary representation of key pair
        """
        return {
            "public_key": self.public_key,
            "private_key": self.private_key
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "KeyPair":
        """
        Create key pair from dictionary.
        
        Args:
            data: Key pair data
            
        Returns:
            KeyPair instance
        """
        return cls(
            data.get("public_key", ""),
            data.get("private_key", "")
        )
    
    def __repr__(self):
        """String representation of key pair."""
        return (
            f"KeyPair(public_key={self.public_key[:16]}..., "
            f"private_key={self.private_key[:16]}...)"
        )
    
    def __str__(self):
        """String representation for printing."""
        return (
            f"Public Key: {self.public_key}\n"
            f"Private Key: {self.private_key}"
        )


def generate_random_string(length: int) -> str:
    """
    Generate a random string.
    
    Args:
        length: Length of random string
        
    Returns:
        Random string
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


def generate_keys(length: int = 128) -> Tuple[KeyPair, str]:
    """
    Generate a new key pair.
    
    Args:
        length: Length of key
        
    Returns:
        KeyPair instance and address
    """
    public_key = generate_random_string(length)
    private_key = generate_random_string(length)
    
    key_pair = KeyPair(public_key, private_key)
    address = sha256_hash(public_key)
    
    return key_pair, address
