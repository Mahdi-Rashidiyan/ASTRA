"""
Core shell implementation with command processing loop
"""

import os
import sys
import signal
import platform
from typing import List, Optional, Dict
from pathlib import Path

# readline is Unix-specific, try importing but don't fail if unavailable
try:
    import readline
    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False

from core.parser import CommandParser
from core.executor import CommandExecutor
from core.builtin import BuiltinCommands
from scheduler.queue import JobQueue
from monitor.resource import ResourceMonitor
from utils.logger import get_logger

class HPCShell:
    """Main HPC Shell class"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.running = True
        self.parser = CommandParser()
        self.executor = CommandExecutor(config)
        self.builtin = BuiltinCommands(self)
        self.job_queue = JobQueue(config)
        self.resource_monitor = ResourceMonitor()
        
        # Shell state
        self.env = dict(os.environ)
        self.aliases = {}
        self.history = []
        self.history_file = Path.home() / '.hpcshell_history'
        
        # Job tracking
        self.jobs = {}  # job_id -> job_info
        self.next_job_id = 1
        
        # Setup signal handlers
        self._setup_signals()
        
        # Load history
        self._load_history()
        
        # Setup tab completion
        self._setup_completion()
    
    def _setup_signals(self):
        """Setup signal handlers"""
        signal.signal(signal.SIGINT, self._handle_sigint)
        # SIGTSTP is not available on Windows
        if hasattr(signal, 'SIGTSTP'):
            signal.signal(signal.SIGTSTP, self._handle_sigtstp)
    
    def _handle_sigint(self, signum, frame):
        """Handle Ctrl+C"""
        print("\n(To exit, type 'exit' or press Ctrl+D)")
    
    def _handle_sigtstp(self, signum, frame):
        """Handle Ctrl+Z"""
        print("\n(Job control not yet implemented for shell itself)")
    
    def _load_history(self):
        """Load command history from file"""
        try:
            if HAS_READLINE and self.history_file.exists():
                readline.read_history_file(str(self.history_file))
        except Exception as e:
            self.logger.warning(f"Could not load history: {e}")
    
    def _save_history(self):
        """Save command history to file"""
        try:
            if HAS_READLINE:
                readline.write_history_file(str(self.history_file))
        except Exception as e:
            self.logger.warning(f"Could not save history: {e}")
    
    def _setup_completion(self):
        """Setup tab completion"""
        if not HAS_READLINE:
            return
        
        def completer(text, state):
            options = [cmd for cmd in self.builtin.get_commands() if cmd.startswith(text)]
            if state < len(options):
                return options[state]
            return None
        
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")
    
    def get_prompt(self) -> str:
        """Generate shell prompt"""
        cwd = os.getcwd()
        home = str(Path.home())
        if cwd.startswith(home):
            cwd = "~" + cwd[len(home):]
        
        # Color codes
        blue = "\033[34m"
        green = "\033[32m"
        reset = "\033[0m"
        
        return f"{green}hpc{reset}:{blue}{cwd}{reset}> "
    
    def run(self):
        """Main shell loop"""
        self.logger.info("HPCShell started")
        
        while self.running:
            try:
                # Get input
                prompt = self.get_prompt()
                line = input(prompt)
                
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Add to history
                self.history.append(line)
                
                # Process command
                self.process_command(line)
                
            except EOFError:
                # Ctrl+D pressed
                print("\nExiting...")
                self.running = False
            except KeyboardInterrupt:
                # Ctrl+C pressed
                print()
                continue
            except Exception as e:
                self.logger.error(f"Error processing command: {e}")
                print(f"Error: {e}")
        
        # Cleanup
        self._save_history()
        self.logger.info("HPCShell stopped")
    
    def process_command(self, line: str):
        """Process a command line"""
        try:
            # Parse command
            commands = self.parser.parse(line)
            
            if not commands:
                return
            
            # Execute pipeline
            for cmd in commands:
                self._execute_single_command(cmd)
                
        except Exception as e:
            print(f"Error: {e}")
            self.logger.error(f"Command error: {e}")
    
    def _execute_single_command(self, cmd: Dict):
        """Execute a single command"""
        command_name = cmd['command']
        args = cmd['args']
        
        # Check if it's a builtin command
        if self.builtin.is_builtin(command_name):
            self.builtin.execute(command_name, args, cmd)
        else:
            # Execute external command
            self.executor.execute(cmd)
    
    def stop(self):
        """Stop the shell"""
        self.running = False