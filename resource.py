"""
Real-time resource monitoring
Tracks CPU, memory, disk, and network usage
"""

import psutil
import time
from typing import Dict, List
from collections import deque

class ResourceMonitor:
    """Monitor system and process resources"""
    
    def __init__(self, history_size: int = 3600):
        self.history_size = history_size  # Keep 1 hour of data
        self.history = {
            'cpu': deque(maxlen=history_size),
            'memory': deque(maxlen=history_size),
            'disk': deque(maxlen=history_size),
            'network': deque(maxlen=history_size),
        }
        self.last_net_io = None
        self.last_disk_io = None
    
    def get_system_stats(self) -> Dict:
        """Get current system resource statistics"""
        stats = {}
        
        # CPU
        stats['cpu_percent'] = psutil.cpu_percent(interval=0.1)
        stats['cpu_count'] = psutil.cpu_count()
        stats['cpu_freq'] = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        
        # Per-core CPU
        stats['cpu_per_core'] = psutil.cpu_percent(interval=0.1, percpu=True)
        
        # Memory
        mem = psutil.virtual_memory()
        stats['memory'] = {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
        }
        
        # Swap
        swap = psutil.swap_memory()
        stats['swap'] = {
            'total': swap.total,
            'used': swap.used,
            'free': swap.free,
            'percent': swap.percent,
        }
        
        # Disk
        disk = psutil.disk_usage('/')
        stats['disk'] = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent,
        }
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        if disk_io:
            if self.last_disk_io:
                read_bytes = disk_io.read_bytes - self.last_disk_io.read_bytes
                write_bytes = disk_io.write_bytes - self.last_disk_io.write_bytes
                stats['disk_io'] = {
                    'read_bytes': read_bytes,
                    'write_bytes': write_bytes,
                }
            self.last_disk_io = disk_io
        
        # Network I/O
        net_io = psutil.net_io_counters()
        if self.last_net_io:
            sent_bytes = net_io.bytes_sent - self.last_net_io.bytes_sent
            recv_bytes = net_io.bytes_recv - self.last_net_io.bytes_recv
            stats['network_io'] = {
                'sent_bytes': sent_bytes,
                'recv_bytes': recv_bytes,
            }
        self.last_net_io = net_io
        
        # Load average (Unix only)
        try:
            stats['load_avg'] = psutil.getloadavg()
        except AttributeError:
            stats['load_avg'] = None
        
        # Timestamp
        stats['timestamp'] = time.time()
        
        # Add to history
        self._add_to_history(stats)
        
        return stats
    
    def get_process_stats(self, pid: int) -> Dict:
        """Get statistics for a specific process"""
        try:
            process = psutil.Process(pid)
            
            with process.oneshot():
                stats = {
                    'pid': pid,
                    'name': process.name(),
                    'status': process.status(),
                    'cpu_percent': process.cpu_percent(interval=0.1),
                    'memory_info': process.memory_info()._asdict(),
                    'memory_percent': process.memory_percent(),
                    'num_threads': process.num_threads(),
                    'create_time': process.create_time(),
                }
                
                # CPU affinity
                try:
                    stats['cpu_affinity'] = process.cpu_affinity()
                except:
                    pass
                
                # I/O counters
                try:
                    io = process.io_counters()
                    stats['io_counters'] = io._asdict()
                except:
                    pass
                
                # Open files
                try:
                    stats['open_files'] = len(process.open_files())
                except:
                    stats['open_files'] = 0
                
                # Connections
                try:
                    stats['connections'] = len(process.connections())
                except:
                    stats['connections'] = 0
                
                return stats
        
        except psutil.NoSuchProcess:
            return None
    
    def _add_to_history(self, stats: Dict):
        """Add current stats to history"""
        timestamp = stats['timestamp']
        
        self.history['cpu'].append({
            'timestamp': timestamp,
            'percent': stats['cpu_percent'],
            'per_core': stats.get('cpu_per_core', []),
        })
        
        self.history['memory'].append({
            'timestamp': timestamp,
            'percent': stats['memory']['percent'],
            'used': stats['memory']['used'],
        })
        
        if 'disk_io' in stats:
            self.history['disk'].append({
                'timestamp': timestamp,
                'read_bytes': stats['disk_io']['read_bytes'],
                'write_bytes': stats['disk_io']['write_bytes'],
            })
        
        if 'network_io' in stats:
            self.history['network'].append({
                'timestamp': timestamp,
                'sent_bytes': stats['network_io']['sent_bytes'],
                'recv_bytes': stats['network_io']['recv_bytes'],
            })
    
    def get_history(self, metric: str, duration: int = 60) -> List[Dict]:
        """Get historical data for a metric"""
        if metric not in self.history:
            return []
        
        # Get data from last 'duration' seconds
        current_time = time.time()
        cutoff_time = current_time - duration
        
        return [
            entry for entry in self.history[metric]
            if entry['timestamp'] >= cutoff_time
        ]
    
    def get_system_info(self) -> Dict:
        """Get static system information"""
        info = {}
        
        # CPU info
        info['cpu'] = {
            'count': psutil.cpu_count(logical=False),
            'count_logical': psutil.cpu_count(logical=True),
        }
        
        try:
            freq = psutil.cpu_freq()
            if freq:
                info['cpu']['freq_current'] = freq.current
                info['cpu']['freq_min'] = freq.min
                info['cpu']['freq_max'] = freq.max
        except:
            pass
        
        # Memory info
        mem = psutil.virtual_memory()
        info['memory'] = {
            'total': mem.total,
        }
        
        # Disk partitions
        info['disks'] = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info['disks'].append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                })
            except:
                pass
        
        # Network interfaces
        info['network'] = {}
        addrs = psutil.net_if_addrs()
        for interface, addr_list in addrs.items():
            info['network'][interface] = [
                {
                    'family': addr.family.name,
                    'address': addr.address,
                }
                for addr in addr_list
            ]
        
        return info
    
    def monitor_continuously(self, interval: float = 1.0, callback=None):
        """Continuously monitor system resources"""
        try:
            while True:
                stats = self.get_system_stats()
                if callback:
                    callback(stats)
                time.sleep(interval)
        except KeyboardInterrupt:
            pass