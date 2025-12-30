# disk.py
"""
Disk I/O Benchmarking
Tests: Sequential read/write, random read/write, IOPS
"""

import os
import time
import tempfile
import random
from typing import Dict
import math

class DiskBenchmark:
    """Disk performance benchmarking"""
    
    def __init__(self, duration: int = 5, file_size: int = 100*1024*1024):
        self.duration = duration
        self.file_size = file_size  # Default 100MB
        self.temp_dir = tempfile.gettempdir()
    
    def run(self) -> Dict:
        """Run disk benchmarks"""
        results = {}
        
        # Sequential write
        results['seq_write'] = self._benchmark_seq_write()
        
        # Sequential read
        results['seq_read'] = self._benchmark_seq_read()
        
        # Random write
        results['rand_write'] = self._benchmark_rand_write()
        
        # Random read
        results['rand_read'] = self._benchmark_rand_read()
        
        # Calculate overall score
        results['score'] = self._calculate_score(results)
        
        return results
    
    def _benchmark_seq_write(self) -> float:
        """Benchmark sequential write"""
        file_path = os.path.join(self.temp_dir, 'hpc_bench_seq_write.tmp')
        
        # Create data to write
        data = b'0' * 1024 * 1024  # 1MB chunks
        chunks = self.file_size // (1024 * 1024)
        
        start = time.time()
        
        with open(file_path, 'wb') as f:
            for _ in range(chunks):
                f.write(data)
        
        elapsed = time.time() - start
        bytes_written = chunks * 1024 * 1024
        mb_per_sec = (bytes_written / (1024 * 1024)) / elapsed
        
        # Clean up
        try:
            os.remove(file_path)
        except:
            pass
        
        return mb_per_sec * 1024 * 1024  # Return bytes/sec
    
    def _benchmark_seq_read(self) -> float:
        """Benchmark sequential read"""
        file_path = os.path.join(self.temp_dir, 'hpc_bench_seq_read.tmp')
        
        # Create test file first
        data = b'0' * 1024 * 1024  # 1MB chunks
        chunks = self.file_size // (1024 * 1024)
        
        with open(file_path, 'wb') as f:
            for _ in range(chunks):
                f.write(data)
        
        # Now benchmark reading
        start = time.time()
        
        with open(file_path, 'rb') as f:
            while f.read(1024 * 1024):  # Read 1MB at a time
                pass
        
        elapsed = time.time() - start
        bytes_read = chunks * 1024 * 1024
        mb_per_sec = (bytes_read / (1024 * 1024)) / elapsed
        
        # Clean up
        try:
            os.remove(file_path)
        except:
            pass
        
        return mb_per_sec * 1024 * 1024  # Return bytes/sec
    
    def _benchmark_rand_write(self) -> float:
        """Benchmark random write"""
        file_path = os.path.join(self.temp_dir, 'hpc_bench_rand_write.tmp')
        
        # Create a sparse file of the desired size
        with open(file_path, 'wb') as f:
            f.seek(self.file_size - 1)
            f.write(b'0')
        
        # Random write operations
        block_size = 4096  # 4KB blocks
        num_operations = min(10000, self.file_size // block_size)
        
        start = time.time()
        
        with open(file_path, 'r+b') as f:
            for _ in range(num_operations):
                # Random position
                pos = random.randint(0, (self.file_size - block_size) // block_size) * block_size
                f.seek(pos)
                
                # Write random data
                f.write(os.urandom(block_size))
        
        elapsed = time.time() - start
        bytes_written = num_operations * block_size
        mb_per_sec = (bytes_written / (1024 * 1024)) / elapsed
        
        # Clean up
        try:
            os.remove(file_path)
        except:
            pass
        
        return mb_per_sec * 1024 * 1024  # Return bytes/sec
    
    def _benchmark_rand_read(self) -> float:
        """Benchmark random read"""
        file_path = os.path.join(self.temp_dir, 'hpc_bench_rand_read.tmp')
        
        # Create test file with random data
        with open(file_path, 'wb') as f:
            f.write(os.urandom(self.file_size))
        
        # Random read operations
        block_size = 4096  # 4KB blocks
        num_operations = min(10000, self.file_size // block_size)
        
        start = time.time()
        
        with open(file_path, 'rb') as f:
            for _ in range(num_operations):
                # Random position
                pos = random.randint(0, (self.file_size - block_size) // block_size) * block_size
                f.seek(pos)
                
                # Read data
                f.read(block_size)
        
        elapsed = time.time() - start
        bytes_read = num_operations * block_size
        mb_per_sec = (bytes_read / (1024 * 1024)) / elapsed
        
        # Clean up
        try:
            os.remove(file_path)
        except:
            pass
        
        return mb_per_sec * 1024 * 1024  # Return bytes/sec
    
    def _calculate_score(self, results: Dict) -> float:
        """Calculate overall disk score (0-10)"""
        # Baseline: 100 MB/s sequential = score of 5
        # Scale logarithmically
        seq_read = results.get('seq_read', 0)
        if seq_read == 0:
            return 0.0
        
        baseline = 100 * 1024 * 1024  # 100 MB/s in bytes/s
        score = 5.0 + math.log10(seq_read / baseline) * 2
        return max(0.0, min(10.0, score))