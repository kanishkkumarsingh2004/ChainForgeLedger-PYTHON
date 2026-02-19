"""
ChainForgeLedger Digital Signature Module

Digital signature implementation.
"""

from chainforgeledger.crypto.hashing import sha256_hash


class Signature:
    """
    Represents a digital signature.
    
    Attributes:
        value: Signature value
        public_key: Public key of signer
    """
    
    def __init__(self, value: str, public_key: str):
        """
        Initialize a new Signature instance.
        
        Args:
            value: Signature value
            public_key: Public key of signer
        """
        self.value = value
        self.public_key = public_key
    
    def verify(self, data: str) -> bool:
        """
        Verify the signature against data.
        
        Args:
            data: Data to verify
            
        Returns:
            True if signature is valid
        """
        # Simplified verification for demo purposes
        expected_signature = sha256_hash(str(data) + self.public_key)
        return self.value == expected_signature
    
    def to_dict(self) -> dict:
        """
        Convert signature to dictionary.
        
        Returns:
            Dictionary representation of signature
        """
        return {
            "value": self.value,
            "public_key": self.public_key
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Signature":
        """
        Create signature from dictionary.
        
        Args:
            data: Signature data
            
        Returns:
            Signature instance
        """
        return cls(
            data.get("value", ""),
            data.get("public_key", "")
        )
    
    def __repr__(self):
        """String representation of signature."""
        return f"Signature(value={self.value[:16]}..., public_key={self.public_key[:16]}...)"
    
    def __str__(self):
        """String representation for printing."""
        return (
            f"Signature: {self.value}\n"
            f"Public Key: {self.public_key}"
        )


def sign(data: str, private_key: str) -> str:
    """
    Sign data with private key.
    
    Args:
        data: Data to sign
        private_key: Private key to sign with
        
    Returns:
        Signature value
    """
    return sha256_hash(str(data) + private_key)


def verify(signature: Signature, data: str, private_key: str) -> bool:
    """
    Verify signature.
    
    Args:
        signature: Signature to verify
        data: Data to verify
        private_key: Private key of signer
        
    Returns:
        True if signature is valid
    """
    # For demo purposes, we'll use a simplified verification that matches the signing
    # In a real implementation, this would use public-key cryptography
    # For now, we'll just use the same mechanism for both
    expected_signature = sha256_hash(str(data) + private_key)
    return signature.value == expected_signature
