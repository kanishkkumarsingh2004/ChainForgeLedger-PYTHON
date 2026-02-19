"""
ChainForgeLedger Logger Module

Logging utilities for blockchain operations.
"""

import logging
import os
import sys
from datetime import datetime


def get_logger(name: str = __name__, log_file: str = None, level: int = logging.INFO):
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        log_file: Log file path (None for console only)
        level: Log level
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # File handler (if log_file specified)
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Disable propagation
    logger.propagate = False
    
    return logger


def configure_global_logger(log_level: str = 'INFO', log_dir: str = 'logs'):
    """
    Configure global logger.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Log directory path
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    level = level_map.get(log_level.upper(), logging.INFO)
    
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'chainforgeledger_{timestamp}.log')
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, mode='a', encoding='utf-8')
        ]
    )
    
    return log_file


class LoggerMixin:
    """
    Mixin class to provide logger functionality.
    
    Classes inheriting from this mixin will have a `logger` attribute.
    """
    
    @property
    def logger(self):
        """Get logger instance for the class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
