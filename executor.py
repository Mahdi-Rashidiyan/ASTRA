"""
Command executor - handles process creation and management
"""

import os
import sys
import subprocess
import signal
import time
import psutil
from typing import Dict, Optional, List
from pathlib import Path

from utils.logger import get_logger

class CommandExecutor:
    """Execute external commands with resource management"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.processes = {}  # pid -> process info
    
    def execute(self, cmd: Dict, job_id: Optional[int] = None) -> Optional[subprocess.Popen]:
        """
        Execute a command
        
        Args:
            cmd: Command dictionary from parser
            job_id: Optional job ID for tracking
            
        Returns:
            Popen object if background, None if foreground
        """
        command = cmd['command']
        args = cmd['args']
        redirects = cmd.get('redirects', {})
        background = cmd.get('background', False)
        
        # Build full command
        full_cmd = [command] + args
        
        # Setup redirections
        stdin, stdout, stderr = self._setup_redirects(redirects)
        
        try:
            # Start process
            process = subprocess.Popen(
                full_cmd,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                preexec_fn=os.setsid if background else None,
                env=os.environ.copy()
            )
            
            # Track process
            self.processes[process.pid] = {
                'process': process,
                'command': ' '.join(full_cmd),
                'job_id': job_id,
                'start_time': time.time(),
                'background': background
            }
            
            if background:
                print(f"[Job {job_id}] Started (PID: {process.pid})")
                return process
            else:
                # Wait for foreground process
                try:
                    process.wait()
                except KeyboardInterrupt:
                    # Send SIGINT to process group
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGINT)
                    except ProcessLookupError:
                        pass
                    process.wait()
                
                return None
                
        except FileNotFoundError:
            print(f"hpcshell: command not found: {command}")
            return None
        except PermissionError:
            print(f"hpcshell: permission denied: {command}")
            return None
        except Exception as e:
            print(f"hpcshell: error executing command: {e}")
            self.logger.error(f"Execution error: {e}")
            return None
        finally:
            # Close redirect files
            if stdin and stdin != subprocess.PIPE:
                stdin.close()
            if stdout and stdout != subprocess.PIPE:
                stdout.close()
            if stderr and stderr != subprocess.PIPE:
                stderr.close()
    
    def _setup_redirects(self, redirects: Dict):
        """Setup file redirections"""
        stdin = None
        stdout = None
        stderr = None
        
        for redir_type, filename in redirects.items():
            if redir_type == '<':
                # Input redirection
                try:
                    stdin = open(filename, 'r')
                except IOError as e:
                    print(f"hpcshell: cannot open {filename}: {e}")
                    stdin = subprocess.DEVNULL
            
            elif redir_type == '>':
                # Output redirection (overwrite)
                try:
                    stdout = open(filename, 'w')
                except IOError as e:
                    print(f"hpcshell: cannot create {filename}: {e}")
            
            elif redir_type == '>>':
                # Output redirection (append)
                try:
                    stdout = open(filename, 'a')
                except IOError as e:
                    print(f"hpcshell: cannot open {filename}: {e}")
            
            elif redir_type == '2>':
                # Error redirection
                try:
                    stderr = open(filename, 'w')
                except IOError as e:
                    print(f"hpcshell: cannot create {filename}: {e}")
            
            elif redir_type == '&>':
                # Both stdout and stderr
                try:
                    stdout = open(filename, 'w')
                    stderr = subprocess.STDOUT
                except IOError as e:
                    print(f"hpcshell: cannot create {filename}: {e}")
        
        return stdin, stdout, stderr
    
    def execute_with_resources(self, cmd: Dict, resources: Dict) -> Optional[subprocess.Popen]:
        """
        Execute command with resource constraints
        
        Args:
            cmd: Command dictionary
            resources: Resource limits (cores, memory, etc.)
        """
        command = cmd['command']
        args = cmd['args']
        full_cmd = [command] + args
        
        # Start process
        process = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        # Apply resource limits using psutil
        try:
            ps_process = psutil.Process(process.pid)
            
            # Set CPU affinity if cores specified
            if resources.get('cores'):
                cores = resources['cores']
                cpu_count = psutil.cpu_count()
                if cores <= cpu_count:
                    # Assign to first N cores
                    ps_process.cpu_affinity(list(range(cores)))
            
            # Set memory limit if specified
            if resources.get('memory'):
                memory_bytes = resources['memory']
                # Note: This requires appropriate permissions
                try:
                    import resource as res
                    # Set virtual memory limit
                    ps_process.rlimit(res.RLIMIT_AS, (memory_bytes, memory_bytes))
                except Exception as e:
                    self.logger.warning(f"Could not set memory limit: {e}")
            
            # Set process priority
            if resources.get('priority'):
                priority_map = {
                    'low': psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 10,
                    'normal': psutil.NORMAL_PRIORITY_CLASS if os.name == 'nt' else 0,
                    'high': psutil.ABOVE_NORMAL_PRIORITY_CLASS if os.name == 'nt' else -10,
                }
                priority = priority_map.get(resources['priority'], 0)
                ps_process.nice(priority)
        
        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            self.logger.warning(f"Could not apply resource limits: {e}")
        
        return process
    
    def get_process_stats(self, pid: int) -> Optional[Dict]:
        """Get resource usage statistics for a process"""
        try:
            process = psutil.Process(pid)
            
            with process.oneshot():
                cpu_percent = process.cpu_percent(interval=0.1)
                memory_info = process.memory_info()
                io_counters = process.io_counters() if hasattr(process, 'io_counters') else None
                
                stats = {
                    'pid': pid,
                    'cpu_percent': cpu_percent,
                    'memory_rss': memory_info.rss,
                    'memory_vms': memory_info.vms,
                    'memory_percent': process.memory_percent(),
                    'num_threads': process.num_threads(),
                    'status': process.status(),
                    'create_time': process.create_time(),
                }
                
                if io_counters:
                    stats.update({
                        'io_read_bytes': io_counters.read_bytes,
                        'io_write_bytes': io_counters.write_bytes,
                        'io_read_count': io_counters.read_count,
                        'io_write_count': io_counters.write_count,
                    })
                
                return stats
        
        except psutil.NoSuchProcess:
            return None
        except Exception as e:
            self.logger.error(f"Error getting process stats: {e}")
            return None
    
    def kill_process(self, pid: int, signal_num: int = signal.SIGTERM) -> bool:
        """Kill a process"""
        try:
            process = psutil.Process(pid)
            process.send_signal(signal_num)
            return True
        except psutil.NoSuchProcess:
            return False
        except Exception as e:
            self.logger.error(f"Error killing process: {e}")
            return False
    
    def is_process_running(self, pid: int) -> bool:
        """Check if process is still running"""
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except psutil.NoSuchProcess:
            return False