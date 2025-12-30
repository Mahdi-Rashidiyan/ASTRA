"""
CPU Benchmarking
Tests: FLOPS, integer operations, matrix multiplication
"""

import time
import math
import multiprocessing
from typing import Dict

class CPUBenchmark:
    """CPU performance benchmarking"""
    
    def __init__(self, duration: int = 5):
        self.duration = duration
        self.cpu_count = multiprocessing.cpu_count()
    
    def run(self) -> Dict:
        """Run CPU benchmarks"""
        results = {}
        
        # Single-precision FLOPS
        results['flops_single'] = self._benchmark_flops_single()
        
        # Double-precision FLOPS
        results['flops_double'] = self._benchmark_flops_double()
        
        # Integer operations
        results['integer_ops'] = self._benchmark_integer()
        
        # Matrix multiplication
        results['matrix_mult'] = self._benchmark_matrix()
        
        # Calculate overall score
        results['score'] = self._calculate_score(results)
        results['flops'] = results['flops_double']  # Use double as standard
        
        return results
    
    def _benchmark_flops_single(self) -> float:
        """Benchmark single-precision floating point operations"""
        iterations = 0
        a, b, c = 1.5, 2.5, 3.5
        
        start = time.time()
        end_time = start + self.duration
        
        while time.time() < end_time:
            # Each loop does 8 FLOPs
            for _ in range(10000):
                a = a * b + c
                b = b * c + a
                c = c * a + b
                a = a * b - c
                b = b * c - a
                c = c * a - b
                a = a / b + c
                b = b / c + a
            iterations += 10000
        
        elapsed = time.time() - start
        flops = (iterations * 8) / elapsed
        return flops
    
    def _benchmark_flops_double(self) -> float:
        """Benchmark double-precision floating point operations"""
        iterations = 0
        a, b, c = 1.5, 2.5, 3.5
        
        start = time.time()
        end_time = start + self.duration
        
        while time.time() < end_time:
            for _ in range(10000):
                a = a * b + c
                b = b * c + a
                c = c * a + b
                a = a * b - c
                b = b * c - a
                c = c * a - b
            iterations += 10000
        
        elapsed = time.time() - start
        flops = (iterations * 6) / elapsed
        return flops
    
    def _benchmark_integer(self) -> float:
        """Benchmark integer operations"""
        iterations = 0
        a, b, c = 100, 200, 300
        
        start = time.time()
        end_time = start + self.duration
        
        while time.time() < end_time:
            for _ in range(10000):
                a = (a * b + c) & 0xFFFFFFFF
                b = (b * c + a) & 0xFFFFFFFF
                c = (c * a + b) & 0xFFFFFFFF
                a = (a << 1) | (a >> 31)
                b = (b << 1) | (b >> 31)
                c = (c << 1) | (c >> 31)
            iterations += 10000
        
        elapsed = time.time() - start
        ops = (iterations * 12) / elapsed
        return ops
    
    def _benchmark_matrix(self) -> float:
        """Benchmark matrix multiplication"""
        try:
            import numpy as np
            
            size = 500
            iterations = 0
            
            A = np.random.random((size, size))
            B = np.random.random((size, size))
            
            start = time.time()
            end_time = start + self.duration
            
            while time.time() < end_time:
                C = np.dot(A, B)
                iterations += 1
            
            elapsed = time.time() - start
            
            # FLOPS for matrix multiply: 2 * n^3
            flops_per_mult = 2 * size ** 3
            total_flops = iterations * flops_per_mult
            flops = total_flops / elapsed
            
            return flops
        
        except ImportError:
            # Numpy not available, use simple Python implementation
            return self._benchmark_matrix_python()
    
    def _benchmark_matrix_python(self) -> float:
        """Simple matrix multiplication without numpy"""
        size = 100
        iterations = 0
        
        # Create matrices
        A = [[float(i * j) for j in range(size)] for i in range(size)]
        B = [[float(i + j) for j in range(size)] for i in range(size)]
        
        start = time.time()
        end_time = start + min(self.duration, 2)  # Shorter for Python version
        
        while time.time() < end_time:
            C = [[0.0] * size for _ in range(size)]
            for i in range(size):
                for j in range(size):
                    for k in range(size):
                        C[i][j] += A[i][k] * B[k][j]
            iterations += 1
        
        elapsed = time.time() - start
        flops_per_mult = 2 * size ** 3
        total_flops = iterations * flops_per_mult
        flops = total_flops / elapsed
        
        return flops
    
    def _calculate_score(self, results: Dict) -> float:
        """Calculate overall CPU score (0-10)"""
        # Baseline: 10 GFLOPS = score of 5
        # Scale logarithmically
        flops = results.get('flops_double', 0)
        if flops == 0:
            return 0.0
        
        baseline = 10e9  # 10 GFLOPS
        score = 5.0 + math.log10(flops / baseline) * 2
        return max(0.0, min(10.0, score))
    
    def benchmark_parallel(self, cores: int = None) -> Dict:
        """Benchmark with parallel execution"""
        if cores is None:
            cores = self.cpu_count
        
        # Not yet implemented - would use multiprocessing
        return {'message': 'Parallel benchmarking not yet implemented'}