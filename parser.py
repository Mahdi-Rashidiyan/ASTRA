"""
Command line parser for HPCShell
Handles pipes, redirections, background jobs, and variable expansion
"""

import re
import shlex
from typing import List, Dict, Optional

class CommandParser:
    """Parse command lines into structured format"""
    
    def __init__(self):
        self.pipe_pattern = re.compile(r'\|')
        self.redirect_pattern = re.compile(r'(>>?|<|2>|&>)')
    
    def parse(self, line: str) -> List[Dict]:
        """
        Parse a command line into structured commands
        
        Returns list of command dictionaries with:
        - command: command name
        - args: list of arguments
        - redirects: dict of redirections
        - background: boolean
        - pipe_to: next command if piped
        """
        line = line.strip()
        
        if not line:
            return []
        
        # Check for background execution
        background = line.endswith('&')
        if background:
            line = line[:-1].strip()
        
        # Split by pipes
        pipe_parts = self._split_pipes(line)
        
        commands = []
        for i, part in enumerate(pipe_parts):
            cmd = self._parse_single_command(part)
            cmd['background'] = background and (i == len(pipe_parts) - 1)
            cmd['pipe_from'] = i > 0
            cmd['pipe_to'] = i < len(pipe_parts) - 1
            commands.append(cmd)
        
        return commands
    
    def _split_pipes(self, line: str) -> List[str]:
        """Split command line by pipes, respecting quotes"""
        parts = []
        current = []
        in_quotes = False
        quote_char = None
        
        i = 0
        while i < len(line):
            char = line[i]
            
            # Handle quotes
            if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
            
            # Handle pipe
            if char == '|' and not in_quotes:
                if current:
                    parts.append(''.join(current).strip())
                    current = []
            else:
                current.append(char)
            
            i += 1
        
        if current:
            parts.append(''.join(current).strip())
        
        return parts
    
    def _parse_single_command(self, cmd_str: str) -> Dict:
        """Parse a single command (no pipes)"""
        # Extract redirections
        redirects = {}
        remaining = cmd_str
        
        # Find all redirections
        redirect_matches = list(self.redirect_pattern.finditer(cmd_str))
        
        if redirect_matches:
            # Process redirections from right to left
            for match in reversed(redirect_matches):
                redirect_type = match.group(1)
                start = match.end()
                
                # Find the filename (next token)
                rest = cmd_str[start:].strip()
                if rest:
                    try:
                        tokens = shlex.split(rest)
                        if tokens:
                            filename = tokens[0]
                            redirects[redirect_type] = filename
                    except ValueError:
                        pass
            
            # Remove redirections from command
            remaining = self.redirect_pattern.sub('', cmd_str)
            for filename in redirects.values():
                remaining = remaining.replace(filename, '')
        
        # Parse command and arguments
        try:
            tokens = shlex.split(remaining)
        except ValueError as e:
            # Handle unclosed quotes
            tokens = remaining.split()
        
        if not tokens:
            return {
                'command': '',
                'args': [],
                'redirects': redirects,
                'background': False,
                'pipe_from': False,
                'pipe_to': False,
                'raw': cmd_str
            }
        
        command = tokens[0]
        args = tokens[1:] if len(tokens) > 1 else []
        
        return {
            'command': command,
            'args': args,
            'redirects': redirects,
            'background': False,
            'pipe_from': False,
            'pipe_to': False,
            'raw': cmd_str
        }
    
    def expand_variables(self, text: str, env: Dict[str, str]) -> str:
        """Expand environment variables in text"""
        # Replace $VAR and ${VAR}
        def replacer(match):
            var_name = match.group(1) or match.group(2)
            return env.get(var_name, '')
        
        pattern = r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
        return re.sub(pattern, replacer, text)
    
    def parse_hpc_options(self, args: List[str]) -> Dict:
        """
        Parse HPC-specific options like --cores, --memory, --priority
        
        Returns dict with options and remaining args
        """
        options = {
            'cores': None,
            'memory': None,
            'time': None,
            'priority': 'normal',
            'queue': 'default',
            'gpu': None,
            'nodes': 1,
        }
        
        remaining_args = []
        i = 0
        
        while i < len(args):
            arg = args[i]
            
            if arg.startswith('--'):
                option = arg[2:]
                
                if option in options and i + 1 < len(args):
                    value = args[i + 1]
                    
                    # Parse value based on option type
                    if option in ('cores', 'nodes', 'gpu'):
                        try:
                            options[option] = int(value)
                        except ValueError:
                            pass
                    elif option == 'memory':
                        options[option] = self._parse_memory(value)
                    elif option == 'time':
                        options[option] = self._parse_time(value)
                    else:
                        options[option] = value
                    
                    i += 2
                    continue
            
            remaining_args.append(arg)
            i += 1
        
        return {
            'options': options,
            'args': remaining_args
        }
    
    def _parse_memory(self, mem_str: str) -> int:
        """Parse memory string like '8GB', '512MB' to bytes"""
        mem_str = mem_str.upper()
        
        units = {
            'B': 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4,
        }
        
        for unit, multiplier in units.items():
            if mem_str.endswith(unit):
                try:
                    value = float(mem_str[:-len(unit)])
                    return int(value * multiplier)
                except ValueError:
                    pass
        
        # Try parsing as plain number (assume MB)
        try:
            return int(float(mem_str) * 1024**2)
        except ValueError:
            return 0
    
    def _parse_time(self, time_str: str) -> int:
        """Parse time string like '2h', '30m', '1d' to seconds"""
        time_str = time_str.lower()
        
        units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
        }
        
        for unit, multiplier in units.items():
            if time_str.endswith(unit):
                try:
                    value = float(time_str[:-len(unit)])
                    return int(value * multiplier)
                except ValueError:
                    pass
        
        # Try parsing as plain number (assume seconds)
        try:
            return int(float(time_str))
        except ValueError:
            return 0