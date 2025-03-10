"""
Encryption utilities for protecting sensitive data.

This module provides functions for encrypting and decrypting sensitive data
using Fernet symmetric encryption from the cryptography library.
"""
import base64
import os
from typing import Any, Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy.ext.hybrid import hybrid_property

from backend.core.config import settings

# Generate or retrieve the encryption key
def get_encryption_key() -> bytes:
    """
    Get the encryption key from settings or generate one if needed.
    
    Returns:
        bytes: The encryption key
    """
    key = settings.ENCRYPTION_KEY
    if not key:
        # If no key is provided in settings, generate one
        # In production, this should be set as an environment variable
        key = Fernet.generate_key().decode()
        # Log warning that a temporary key is being used
        print("WARNING: Using a temporary encryption key. Set ENCRYPTION_KEY in environment variables.")
    
    if isinstance(key, str):
        key = key.encode()
    
    return key

# Initialize Fernet cipher with our key
_FERNET = None

def get_fernet() -> Fernet:
    """
    Get or initialize the Fernet encryption object.
    
    Returns:
        Fernet: The Fernet cipher object
    """
    global _FERNET
    if _FERNET is None:
        _FERNET = Fernet(get_encryption_key())
    return _FERNET

def encrypt(data: Union[str, bytes]) -> bytes:
    """
    Encrypt data using Fernet symmetric encryption.
    
    Args:
        data: The data to encrypt, either as string or bytes
        
    Returns:
        bytes: The encrypted data
    """
    if data is None:
        return None
        
    if isinstance(data, str):
        data = data.encode()
        
    return get_fernet().encrypt(data)

def decrypt(data: bytes) -> bytes:
    """
    Decrypt data using Fernet symmetric encryption.
    
    Args:
        data: The encrypted data
        
    Returns:
        bytes: The decrypted data
    """
    if data is None:
        return None
        
    return get_fernet().decrypt(data)

def encrypt_string(text: str) -> str:
    """
    Encrypt a string and return the result as a base64-encoded string.
    
    Args:
        text: The text to encrypt
        
    Returns:
        str: The encrypted text as a base64-encoded string
    """
    if text is None:
        return None
        
    encrypted = encrypt(text)
    return base64.b64encode(encrypted).decode()

def decrypt_string(text: str) -> str:
    """
    Decrypt a base64-encoded encrypted string.
    
    Args:
        text: The base64-encoded encrypted text
        
    Returns:
        str: The decrypted text
    """
    if text is None:
        return None
        
    encrypted = base64.b64decode(text)
    return decrypt(encrypted).decode()

class EncryptedType:
    """
    A mixin to provide encrypted fields for SQLAlchemy models.
    
    Usage:
        class User(Base):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            _ssn = Column('ssn', String)
            
            @hybrid_property
            def ssn(self):
                return EncryptedType.decrypt_value(self._ssn)
                
            @ssn.setter
            def ssn(self, value):
                self._ssn = EncryptedType.encrypt_value(value)
    """
    
    @staticmethod
    def encrypt_value(value: Any) -> Optional[str]:
        """
        Encrypt a value for storage in the database.
        
        Args:
            value: The value to encrypt
            
        Returns:
            Optional[str]: The encrypted value as a string, or None if value is None
        """
        if value is None:
            return None
        return encrypt_string(str(value))
    
    @staticmethod
    def decrypt_value(value: str) -> Optional[str]:
        """
        Decrypt a value from the database.
        
        Args:
            value: The encrypted value
            
        Returns:
            Optional[str]: The decrypted value, or None if value is None
        """
        if value is None:
            return None
        return decrypt_string(value) 