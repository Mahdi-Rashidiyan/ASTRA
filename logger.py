"""
Logging system for HPCShell
"""

import logging
import sys
from pathlib import Path

# Global logger registry
_loggers = {}

def setup_logger(name: str = 'hpcshell', level: str = 'INFO', log_file: str = None):
    """Setup main logger"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")
    
    # Console handler (only warnings and errors)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    _loggers[name] = logger
    return logger

def get_logger(name: str = 'hpcshell'):
    """Get logger instance"""
    if name not in _loggers:
        # Create default logger
        log_file = str(Path.home() / '.hpcshell.log')
        return setup_logger(name, log_file=log_file)
    return _loggers[name]