"""
ChainForgeLedger Cryptography Module

Cryptographic utilities for blockchain operations.
"""

import binascii
import os
from typing import Any, Tuple
from chainforgeledger.crypto.hashing import (
    sha256_hash,
    generate_keys as ecdsa_generate_keys,
    sign as ecdsa_sign,
    verify as ecdsa_verify
)


class CryptoUtils:
    """
    Cryptographic utilities for blockchain operations.
    
    Provides common cryptographic operations like hashing, digital signatures,
    and encryption for blockchain applications.
    """
    
    @staticmethod
    def sha256(data: Any) -> str:
        """
        Compute SHA-256 hash of data using self-made implementation.
        
        Args:
            data: Data to hash
            
        Returns:
            SHA-256 hash as hexadecimal string
        """
        if isinstance(data, str):
            pass  # Already string, use directly
        elif isinstance(data, bytes):
            data = data.decode('utf-8')
        else:
            data = str(data)
            
        return sha256_hash(data)
    
    @staticmethod
    def sha512(data: Any) -> str:
        """
        Compute SHA-512 hash of data (placeholder - using SHA-256 for consistency).
        
        Args:
            data: Data to hash
            
        Returns:
            SHA-512 hash as hexadecimal string (using SHA-256 for now)
        """
        # Note: SHA-512 implementation not available, using SHA-256 for consistency
        if isinstance(data, str):
            pass  # Already string, use directly
        elif isinstance(data, bytes):
            data = data.decode('utf-8')
        else:
            data = str(data)
            
        return sha256_hash(data)
    
    @staticmethod
    def md5(data: Any) -> str:
        """
        Compute MD5 hash of data (placeholder - using SHA-256 for consistency).
        
        Args:
            data: Data to hash
            
        Returns:
            MD5 hash as hexadecimal string (using SHA-256 for now)
        """
        # Note: MD5 implementation not available, using SHA-256 for consistency
        if isinstance(data, str):
            pass  # Already string, use directly
        elif isinstance(data, bytes):
            data = data.decode('utf-8')
        else:
            data = str(data)
            
        return sha256_hash(data)
    
    @staticmethod
    def hmac_sha256(key: str, message: str) -> str:
        """
        Compute HMAC-SHA256 (placeholder implementation).
        
        Args:
            key: Secret key
            message: Message to authenticate
            
        Returns:
            HMAC-SHA256 as hexadecimal string (simple implementation)
        """
        # Simple HMAC implementation using SHA-256 (not cryptographically secure for production)
        combined = key + message
        return sha256_hash(combined)
    
    @staticmethod
    def generate_rsa_keys(bits: int = 2048) -> Tuple[str, str]:
        """
        Generate RSA key pair (placeholder - using simple key generation for demonstration).
        
        Args:
            bits: Key size in bits
            
        Returns:
            Tuple containing private key and public key (simple string format)
        """
        # For demonstration purposes - in real scenario, implement RSA key generation
        import random
        private_key = hex(random.randint(10**100, 10**200))
        public_key = hex(random.randint(10**100, 10**200))
        return private_key, public_key
    
    @staticmethod
    def generate_ec_keys(curve: str = 'secp256k1') -> Tuple[str, str]:
        """
        Generate elliptic curve key pair using self-made ECDSA implementation.
        
        Args:
            curve: Elliptic curve name (currently only secp256k1 supported)
            
        Returns:
            Tuple containing private key and public key (hexadecimal strings)
        """
        private_key, public_key = ecdsa_generate_keys()
        # Convert to hex format for storage/transmission
        private_hex = hex(private_key)
        public_hex = f"04{hex(public_key[0])[2:].zfill(64)}{hex(public_key[1])[2:].zfill(64)}"
        return private_hex, public_hex
    
    @staticmethod
    def rsa_sign(private_key_pem: str, message: str) -> str:
        """
        Sign message using RSA (placeholder - using simple signature for demonstration).
        
        Args:
            private_key_pem: Private key in PEM format
            message: Message to sign
            
        Returns:
            Signature as hexadecimal string
        """
        # For demonstration purposes - in real scenario, implement RSA signing
        signature = sha256_hash(private_key_pem + message)
        return signature
    
    @staticmethod
    def rsa_verify(public_key_pem: str, message: str, signature_b64: str) -> bool:
        """
        Verify RSA signature (placeholder - simple verification for demonstration).
        
        Args:
            public_key_pem: Public key in PEM format
            message: Message to verify
            signature_b64: Signature as base64 encoded string
            
        Returns:
            True if signature is valid, False otherwise
        """
        # For demonstration purposes - in real scenario, implement RSA verification
        expected_signature = sha256_hash(public_key_pem + message)
        return signature_b64 == expected_signature
    
    @staticmethod
    def ec_sign(private_key_pem: str, message: str, curve: str = 'secp256k1') -> str:
        """
        Sign message using elliptic curve cryptography with self-made ECDSA.
        
        Args:
            private_key_pem: Private key in hex format
            message: Message to sign
            curve: Elliptic curve name
            
        Returns:
            Signature as base64 encoded string
        """
        try:
            # Convert private key from hex to integer
            private_key = int(private_key_pem.strip('0x'), 16)
            # Sign message
            r, s = ecdsa_sign(message, private_key)
            # Combine r and s into signature string
            signature = f"{hex(r)[2:].zfill(64)}{hex(s)[2:].zfill(64)}"
            return signature
        except Exception as e:
            raise Exception(f"EC signature failed: {e}")
    
    @staticmethod
    def ec_verify(public_key_pem: str, message: str, signature_b64: str, curve: str = 'secp256k1') -> bool:
        """
        Verify elliptic curve signature using self-made ECDSA.
        
        Args:
            public_key_pem: Public key in hex format (04 prefix)
            message: Message to verify
            signature_b64: Signature as hex string (64-byte r + 64-byte s)
            curve: Elliptic curve name
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Parse public key
            if public_key_pem.startswith('04'):
                public_key_pem = public_key_pem[2:]
            x = int(public_key_pem[:64], 16)
            y = int(public_key_pem[64:], 16)
            public_key = (x, y)
            
            # Parse signature
            r = int(signature_b64[:64], 16)
            s = int(signature_b64[64:], 16)
            signature = (r, s)
            
            # Verify signature
            return ecdsa_verify(message, signature, public_key)
        except Exception as e:
            raise Exception(f"EC verification failed: {e}")
    
    @staticmethod
    def aes_encrypt(key: str, data: str, mode: str = 'CBC', iv: str = None) -> str:
        """
        Simple XOR encryption as a placeholder for AES (self-made implementation).
        
        Args:
            key: Encryption key
            data: Data to encrypt
            mode: Encryption mode (ignored for XOR)
            iv: Initialization vector (ignored for XOR)
            
        Returns:
            Encrypted data as hexadecimal string
        """
        try:
            # XOR encryption (simple self-made approach)
            key_bytes = key.encode('utf-8')
            data_bytes = data.encode('utf-8')
            
            encrypted_bytes = bytearray()
            key_len = len(key_bytes)
            
            for i, byte in enumerate(data_bytes):
                encrypted_bytes.append(byte ^ key_bytes[i % key_len])
                
            return binascii.hexlify(encrypted_bytes).decode('utf-8')
                
        except Exception as e:
            raise Exception(f"Encryption failed: {e}")
    
    @staticmethod
    def aes_decrypt(key: str, encrypted_data: str, mode: str = 'CBC') -> str:
        """
        Simple XOR decryption as a placeholder for AES (self-made implementation).
        
        Args:
            key: Encryption key
            encrypted_data: Encrypted data as hexadecimal string
            mode: Encryption mode (ignored for XOR)
            
        Returns:
            Decrypted data
        """
        try:
            # XOR decryption (simple self-made approach)
            key_bytes = key.encode('utf-8')
            encrypted_bytes = binascii.unhexlify(encrypted_data)
            
            decrypted_bytes = bytearray()
            key_len = len(key_bytes)
            
            for i, byte in enumerate(encrypted_bytes):
                decrypted_bytes.append(byte ^ key_bytes[i % key_len])
                
            return decrypted_bytes.decode('utf-8')
                
        except Exception as e:
            raise Exception(f"Decryption failed: {e}")
    
    @staticmethod
    def generate_random(length: int = 16) -> str:
        """
        Generate random string.
        
        Args:
            length: Length of random string
            
        Returns:
            Random string
        """
        return binascii.hexlify(os.urandom(length)).decode('utf-8')
    
    @staticmethod
    def generate_salt(length: int = 16) -> str:
        """
        Generate salt value.
        
        Args:
            length: Length of salt
            
        Returns:
            Salt as hexadecimal string
        """
        return CryptoUtils.generate_random(length)
    
    @staticmethod
    def pbkdf2(password: str, salt: str, iterations: int = 100000, key_length: int = 32) -> str:
        """
        Simple key derivation function as a placeholder for PBKDF2.
        
        Args:
            password: Password
            salt: Salt value
            iterations: Number of iterations
            key_length: Length of derived key
            
        Returns:
            Derived key as hexadecimal string
        """
        # Simple key derivation using repeated hashing
        key = password + salt
        for i in range(iterations):
            key = CryptoUtils.sha256(key)
        
        return key[:key_length*2]  # Each hex character is 4 bits


# ==========================================
# Helper Functions for Key Conversion
# ==========================================

def private_key_to_hex(private_key: int) -> str:
    """Convert private key integer to hexadecimal string."""
    return hex(private_key)

def public_key_to_hex(public_key: Tuple[int, int]) -> str:
    """Convert public key (x, y) coordinates to hexadecimal string with 04 prefix."""
    return f"04{hex(public_key[0])[2:].zfill(64)}{hex(public_key[1])[2:].zfill(64)}"

def hex_to_private_key(private_key_hex: str) -> int:
    """Convert hexadecimal private key string to integer."""
    return int(private_key_hex.strip('0x'), 16)

def hex_to_public_key(public_key_hex: str) -> Tuple[int, int]:
    """Convert hexadecimal public key string to (x, y) coordinates."""
    if public_key_hex.startswith('04'):
        public_key_hex = public_key_hex[2:]
    x = int(public_key_hex[:64], 16)
    y = int(public_key_hex[64:], 16)
    return (x, y)
