"""
Built-in shell commands
"""

import os
import random
import sys
from pathlib import Path
from typing import List, Dict

from utils.logger import get_logger

class BuiltinCommands:
    """Built-in commands for HPCShell"""
    
    def __init__(self, shell):
        self.shell = shell
        self.logger = get_logger(__name__)
        
        # Register built-in commands
        self.commands = {
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            'cd': self.cmd_cd,
            'pwd': self.cmd_pwd,
            'echo': self.cmd_echo,
            'export': self.cmd_export,
            'env': self.cmd_env,
            'alias': self.cmd_alias,
            'unalias': self.cmd_unalias,
            'history': self.cmd_history,
            'help': self.cmd_help,
            'tutorial': self.cmd_tutorial,
            'jobs': self.cmd_jobs,
            'kill': self.cmd_kill,
            'fg': self.cmd_fg,
            'bg': self.cmd_bg,
            'run': self.cmd_run,
            'submit': self.cmd_submit,
            'monitor': self.cmd_monitor,
            'queue': self.cmd_queue,
            'benchmark': self.cmd_benchmark,
            'profile': self.cmd_profile,
            'parallel': self.cmd_parallel,
            'cern-data': self.cmd_cern_data,
            'root-analyze': self.cmd_root_analyze,
            'geant4-sim': self.cmd_geant4_sim,
            'cern-job': self.cmd_cern_job,
            'grid-submit': self.cmd_grid_submit,
            'cern-benchmark': self.cmd_cern_benchmark,
        }
    
    def is_builtin(self, command: str) -> bool:
        """Check if command is built-in"""
        return command in self.commands
    
    def get_commands(self) -> List[str]:
        """Get list of built-in commands"""
        return list(self.commands.keys())
    
    def execute(self, command: str, args: List[str], cmd_dict: Dict):
        """Execute a built-in command"""
        if command in self.commands:
            try:
                self.commands[command](args, cmd_dict)
            except Exception as e:
                print(f"Error in {command}: {e}")
                self.logger.error(f"Builtin command error: {e}")
    
    # ===== Basic Commands =====
    
    def cmd_exit(self, args, cmd_dict):
        """Exit the shell"""
        exit_code = 0
        if args:
            try:
                exit_code = int(args[0])
            except ValueError:
                pass
        self.shell.stop()
        sys.exit(exit_code)
    
    def cmd_cd(self, args, cmd_dict):
        """Change directory"""
        if not args:
            # Go to home directory
            target = str(Path.home())
        else:
            target = args[0]
            
            # Expand ~ to home
            if target.startswith('~'):
                target = str(Path.home()) + target[1:]
        
        try:
            os.chdir(target)
        except FileNotFoundError:
            print(f"cd: no such file or directory: {target}")
        except PermissionError:
            print(f"cd: permission denied: {target}")
        except Exception as e:
            print(f"cd: {e}")
    
    def cmd_pwd(self, args, cmd_dict):
        """Print working directory"""
        print(os.getcwd())
    
    def cmd_echo(self, args, cmd_dict):
        """Echo arguments"""
        print(' '.join(args))
    
    def cmd_export(self, args, cmd_dict):
        """Export environment variable"""
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                os.environ[key] = value
                self.shell.env[key] = value
            else:
                print(f"export: invalid syntax: {arg}")
    
    def cmd_env(self, args, cmd_dict):
        """Print environment variables"""
        for key, value in sorted(os.environ.items()):
            print(f"{key}={value}")
    
    def cmd_alias(self, args, cmd_dict):
        """Create command alias"""
        if not args:
            # List all aliases
            for name, value in self.shell.aliases.items():
                print(f"{name}='{value}'")
        else:
            for arg in args:
                if '=' in arg:
                    name, value = arg.split('=', 1)
                    self.shell.aliases[name] = value.strip("'\"")
                else:
                    # Show specific alias
                    if arg in self.shell.aliases:
                        print(f"{arg}='{self.shell.aliases[arg]}'")
    
    def cmd_unalias(self, args, cmd_dict):
        """Remove alias"""
        for arg in args:
            if arg in self.shell.aliases:
                del self.shell.aliases[arg]
            else:
                print(f"unalias: {arg}: not found")
    
    def cmd_history(self, args, cmd_dict):
        """Show command history"""
        start = 0
        count = len(self.shell.history)
        
        if args:
            try:
                count = int(args[0])
                start = max(0, len(self.shell.history) - count)
            except ValueError:
                pass
        
        for i, cmd in enumerate(self.shell.history[start:], start=start+1):
            print(f"{i:5d}  {cmd}")
    
    def cmd_help(self, args, cmd_dict):
        """Show help information"""
        if not args:
            print("""
LHCShell - CERN High-Energy Physics Computing Shell

Basic Commands:
  cd [dir]              Change directory
  pwd                   Print working directory
  exit, quit            Exit shell
  echo [args]           Print arguments
  export VAR=value      Set environment variable
  env                   Show environment variables
  history [n]           Show command history
  
CERN Physics Commands:
  cern-data <id>        Access CERN Open Data Portal
  root-analyze script   Run ROOT analysis scripts
  geant4-sim config     Run Geant4 simulation
  cern-job [opts] cmd   Run with CERN-specific settings
  grid-submit script    Submit to CERN grid
  cern-benchmark        Run physics-specific benchmarks

HPC Commands:
  run [opts] command    Run command with resource allocation
  submit [opts] script  Submit batch job
  jobs                  List running jobs
  monitor <job-id>      Monitor job resources
  queue                 Show job queue
  kill <job-id>         Kill a job
  benchmark             Run system benchmarks
  profile command       Profile command performance
  parallel command      Run command in parallel

Options for run/submit:
  --cores N             Allocate N CPU cores
  --memory SIZE         Allocate memory (e.g., 8GB)
  --time DURATION       Set time limit (e.g., 2h)
  --priority LEVEL      Set priority (low/normal/high)
  --queue NAME          Submit to specific queue
  --gpu N               Allocate N GPUs

CERN Examples:
  cern-data CMS/2012/CSV ./data
  root-analyze analysis.C
  geant4-sim detector_config.xml
  grid-submit --vo cms --memory 4GB analysis_job.sh
  cern-benchmark

For detailed help on a specific command: help <command>

""")
        else:
            command = args[0]
            if command in self.commands:
                doc = self.commands[command].__doc__
                print(f"\n{command}: {doc}\n")
            else:
                print(f"No help available for: {command}")
    
    def cmd_tutorial(self, args, cmd_dict):
        """Show tutorial"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                  HPCShell Quick Tutorial                      ║
╚══════════════════════════════════════════════════════════════╝

1. BASIC USAGE
   - Just like bash: ls, cd, pwd, etc.
   - Pipes work: ls | grep txt
   - Redirections: command > output.txt

2. RUNNING JOBS WITH RESOURCE ALLOCATION
   
   hpc> run --cores 4 --memory 8GB python script.py
   
   This runs your script with:
   - 4 CPU cores dedicated
   - 8GB memory limit
   - Real-time resource monitoring

3. BACKGROUND JOBS
   
   hpc> run python long_task.py &
   [Job 1] Started (PID: 12345)
   
   Check status:
   hpc> jobs
   hpc> monitor 1

4. SUBMITTING BATCH JOBS
   
   hpc> submit --queue long --time 24h job.sh
   
   This queues your job to run when resources available.

5. BENCHMARKING
   
   hpc> benchmark
   
   Tests your system: CPU, memory, disk performance

6. PERFORMANCE PROFILING
   
   hpc> profile python expensive_task.py
   
   Shows where time is spent, memory usage, etc.

7. PARALLEL EXECUTION
   
   hpc> parallel --cores 8 process ::: file1 file2 file3
   
   Runs 'process' on each file in parallel.

Try it now: run --cores 2 echo "Hello HPC!"
""")
    
    # ===== Job Control Commands =====
    
    def cmd_jobs(self, args, cmd_dict):
        """List all jobs"""
        if not self.shell.jobs:
            print("No jobs")
            return
        
        print("\n╔════╦═══════════════════════╦══════════╦═══════════╗")
        print("║ ID ║ Command               ║ Status   ║ Runtime   ║")
        print("╠════╬═══════════════════════╬══════════╬═══════════╣")
        
        for job_id, job_info in self.shell.jobs.items():
            cmd = job_info.get('command', '')[:20]
            status = job_info.get('status', 'UNKNOWN')
            runtime = job_info.get('runtime', '00:00:00')
            print(f"║ {job_id:2d} ║ {cmd:21s} ║ {status:8s} ║ {runtime:9s} ║")
        
        print("╚════╩═══════════════════════╩══════════╩═══════════╝\n")
    
    def cmd_kill(self, args, cmd_dict):
        """Kill a job"""
        if not args:
            print("Usage: kill <job-id>")
            return
        
        try:
            job_id = int(args[0])
            if job_id in self.shell.jobs:
                pid = self.shell.jobs[job_id].get('pid')
                if pid and self.shell.executor.kill_process(pid):
                    print(f"[Job {job_id}] Terminated")
                    self.shell.jobs[job_id]['status'] = 'KILLED'
                else:
                    print(f"Failed to kill job {job_id}")
            else:
                print(f"Job {job_id} not found")
        except ValueError:
            print(f"Invalid job ID: {args[0]}")
    
    def cmd_fg(self, args, cmd_dict):
        """Bring job to foreground"""
        print("fg: not yet implemented")
    
    def cmd_bg(self, args, cmd_dict):
        """Resume job in background"""
        print("bg: not yet implemented")
    
    # ===== HPC Commands =====
    
    def cmd_run(self, args, cmd_dict):
        """Run command with resource allocation"""
        if not args:
            print("Usage: run [options] command [args]")
            return
        
        # Parse HPC options
        parsed = self.shell.parser.parse_hpc_options(args)
        options = parsed['options']
        remaining_args = parsed['args']
        
        if not remaining_args:
            print("No command specified")
            return
        
        # Create command dict
        new_cmd = {
            'command': remaining_args[0],
            'args': remaining_args[1:],
            'redirects': cmd_dict.get('redirects', {}),
            'background': True,  # Always run in background for monitoring
        }
        
        # Create job
        job_id = self.shell.next_job_id
        self.shell.next_job_id += 1
        
        # Execute with resources
        process = self.shell.executor.execute_with_resources(new_cmd, options)
        
        if process:
            self.shell.jobs[job_id] = {
                'job_id': job_id,
                'pid': process.pid,
                'command': ' '.join(remaining_args),
                'status': 'RUNNING',
                'resources': options,
                'start_time': __import__('time').time(),
            }
            
            print(f"\n[Job {job_id}] Started")
            print(f"  PID: {process.pid}")
            print(f"  Cores: {options.get('cores', 'unlimited')}")
            print(f"  Memory: {self._format_bytes(options.get('memory', 0))}")
            print(f"  Priority: {options.get('priority', 'normal').upper()}")
            print()
    
    def cmd_submit(self, args, cmd_dict):
        """Submit batch job"""
        print("Submitting job to queue...")
        print("(Queue system not yet implemented)")
    
    def cmd_monitor(self, args, cmd_dict):
        """Monitor job resources"""
        if not args:
            print("Usage: monitor <job-id>")
            return
        
        try:
            job_id = int(args[0])
            if job_id not in self.shell.jobs:
                print(f"Job {job_id} not found")
                return
            
            job = self.shell.jobs[job_id]
            pid = job.get('pid')

            if not pid:
                print(f"Job {job_id} has no PID")
                return

            stats = self.shell.executor.get_process_stats(pid)

            if not stats:
                print(f"Job {job_id} is not running")
                job['status'] = 'COMPLETED'
                return

            # Calculate runtime
            runtime = __import__('time').time() - job['start_time']

            print(f"\nJob {job_id}: {job['command']}")
            print(f"├─ Runtime: {self._format_time(runtime)}")
            print(f"├─ CPU Usage: {stats.get('cpu_percent', 0):.1f}%")
            print(f"├─ Memory: {self._format_bytes(stats.get('memory_rss', 0))} ({stats.get('memory_percent', 0):.1f}%)")
            print(f"├─ Threads: {stats.get('num_threads', 0)}")
            print(f"├─ Status: {stats.get('status', 'UNKNOWN')}")

            if 'io_read_bytes' in stats:
                print(f"├─ I/O Read: {self._format_bytes(stats.get('io_read_bytes', 0))}")
                print(f"└─ I/O Write: {self._format_bytes(stats.get('io_write_bytes', 0))}")
            else:
                print(f"└─ I/O: N/A")
            print()

        except ValueError:
            print(f"Invalid job ID: {args[0]}")
    
    def cmd_queue(self, args, cmd_dict):
        """Show job queue"""
        print("Job queue (not yet implemented)")
    
    def cmd_benchmark(self, args, cmd_dict):
        """Run system benchmarks"""
        from benchmark.cpu import CPUBenchmark
        from benchmark.memory import MemoryBenchmark
        from benchmark.disk import DiskBenchmark
        
        print("\n╔══════════════════════════════════════╗")
        print("║      SYSTEM BENCHMARK RESULTS        ║")
        print("╚══════════════════════════════════════╝\n")
        
        # CPU Benchmark
        print("Running CPU benchmark...")
        cpu_bench = CPUBenchmark()
        cpu_results = cpu_bench.run()
        
        print("\nCPU Performance:")
        print(f"  └─ FLOPS: {cpu_results.get('flops', 0)/1e9:.2f} GFLOPS")
        print(f"  └─ Score: {cpu_results.get('score', 0):.1f}/10")
        
        # Memory Benchmark
        print("\nRunning memory benchmark...")
        mem_bench = MemoryBenchmark()
        mem_results = mem_bench.run()
        
        print("\nMemory Performance:")
        print(f"  └─ Bandwidth: {mem_results.get('bandwidth', 0)/1e9:.2f} GB/s")
        print(f"  └─ Score: {mem_results.get('score', 0):.1f}/10")
        
        # Disk Benchmark
        print("\nRunning disk benchmark...")
        disk_bench = DiskBenchmark()
        disk_results = disk_bench.run()
        
        print("\nDisk Performance:")
        print(f"  └─ Sequential Read: {disk_results.get('seq_read', 0)/1e6:.0f} MB/s")
        print(f"  └─ Sequential Write: {disk_results.get('seq_write', 0)/1e6:.0f} MB/s")
        print(f"  └─ Score: {disk_results.get('score', 0):.1f}/10")
        print()
    
    def cmd_profile(self, args, cmd_dict):
        """Profile command performance"""
        print("Performance profiling (not yet fully implemented)")
    
    def cmd_parallel(self, args, cmd_dict):
        """Run command in parallel"""
        print("Parallel execution (not yet implemented)")
    
    def cmd_cern_data(self, args, cmd_dict):
        """Access CERN Open Data Portal datasets"""
        if not args:
            print("Usage: cern-data <dataset-id> [destination]")
            return
    
        dataset_id = args[0]
        destination = args[1] if len(args) > 1 else f"./{dataset_id}"
    
        print(f"Accessing CERN Open Data Portal for dataset: {dataset_id}")
        print(f"Destination: {destination}")

        # Implementation would connect to CERN's Open Data Portal API
        # For now, just show a placeholder
        print("(CERN data access not yet implemented)")
    def cmd_root_analyze(self, args, cmd_dict):
        """Run ROOT analysis scripts with proper environment"""
        if not args:
            print("Usage: root-analyze <script.C> [options]")
            return
    
        script = args[0]
        options = args[1:] if len(args) > 1 else []
    
        # Check if ROOT is available
        try:
            import ROOT
            print(f"Running ROOT analysis script: {script}")
        
            # Create command dict for ROOT execution
            new_cmd = {
                'command': 'root',
                'args': ['-l', '-b', '-q'] + [script] + options,
                'redirects': cmd_dict.get('redirects', {}),
                'background': cmd_dict.get('background', False),
            }
        
            # Execute with the standard executor
            self.shell.executor.execute(new_cmd)
        
        except ImportError:
            print("ROOT not found. Please install ROOT framework.")
            print("Visit: https://root.cern/install/")

    def cmd_geant4_sim(self, args, cmd_dict):
        """Run a Geant4 simulation (placeholder)"""
        if not args:
            print("Usage: geant4-sim <macro> [options]")
            return

        macro = args[0]
        options = args[1:]
        print(f"Geant4 simulation requested: {macro} {' '.join(options)}")
        print("(Geant4 integration not implemented in this build)")

    def cmd_cern_job(self, args, cmd_dict):
        """Submit or manage CERN-specific jobs (placeholder)"""
        if not args:
            print("Usage: cern-job <submit|status|cancel> [args]")
            return

        subcmd = args[0]
        if subcmd == 'submit':
            print("Submitting job to CERN systems (not implemented)")
        elif subcmd == 'status':
            print("Checking CERN job status (not implemented)")
        elif subcmd == 'cancel':
            print("Cancelling CERN job (not implemented)")
        else:
            print(f"Unknown cern-job subcommand: {subcmd}")

    def cmd_cern_benchmark(self, args, cmd_dict):
        """Run CERN-specific benchmarks for particle physics workloads"""
        print("\n╔══════════════════════════════════════╗")
        print("║      CERN PHYSICS BENCHMARKS        ║")
        print("╚══════════════════════════════════════╝\n")
    
        # Standard benchmarks
        from benchmark.cpu import CPUBenchmark
        from benchmark.memory import MemoryBenchmark
        from benchmark.disk import DiskBenchmark
    
        # Run standard benchmarks
        print("Running standard benchmarks...")
        cpu_bench = CPUBenchmark()
        cpu_results = cpu_bench.run()
    
        mem_bench = MemoryBenchmark()
        mem_results = mem_bench.run()
    
        disk_bench = DiskBenchmark()
        disk_results = disk_bench.run()
    
        # CERN-specific benchmarks
        print("\nRunning CERN-specific benchmarks...")
    
        # 1. Four-vector operations (common in particle physics)
        print("Benchmarking four-vector operations...")
        four_vector_score = self._benchmark_four_vectors()
    
        # 2. Histogram operations (ROOT-style)
        print("Benchmarking histogram operations...")
        histogram_score = self._benchmark_histograms()
    
        # 3. Event generation simulation
        print("Benchmarking event generation...")
        event_score = self._benchmark_event_generation()
    
        # Display results
        print("\nCERN Physics Performance:")
        print(f"  └─ Four-vector ops: {four_vector_score:.2f} ops/s")
        print(f"  └─ Histogram ops: {histogram_score:.2f} ops/s")
        print(f"  └─ Event generation: {event_score:.2f} events/s")
    
        # Calculate CERN-specific score
        cern_score = self._calculate_cern_score(cpu_results, mem_results, disk_results, 
                                          four_vector_score, histogram_score, event_score)
    
        print(f"\nOverall CERN Performance Score: {cern_score:.1f}/10")
        print()

    def _benchmark_four_vectors(self):
        """Benchmark four-vector operations common in particle physics"""
        import random
        import math
        import time
    
        iterations = 0
        duration = 2.0  # Shorter duration for this specific benchmark
    
        # Create random four-vectors (px, py, pz, E)
        vectors = [(random.uniform(-100, 100), random.uniform(-100, 100), 
                random.uniform(-100, 100), random.uniform(100, 500)) 
               for _ in range(1000)]
    
        start = time.time()
        end_time = start + duration
    
        while time.time() < end_time:
            for i in range(len(vectors)):
                px, py, pz, E = vectors[i]
            
                # Calculate invariant mass
                mass_sq = E*E - px*px - py*py - pz*pz
                mass = math.sqrt(abs(mass_sq)) if mass_sq > 0 else 0
            
                # Calculate rapidity
                pt = math.sqrt(px*px + py*py)
                p = math.sqrt(px*px + py*py + pz*pz)
                rapidity = 0.5 * math.log((E + pz) / (E - pz)) if (E - pz) != 0 else 0
            
                # Calculate transverse momentum
                pt = math.sqrt(px*px + py*py)
            
                # Calculate phi
                phi = math.atan2(py, px)
            
                # Calculate theta
                theta = math.acos(pz / p) if p != 0 else 0
            
                # Store results back
                vectors[i] = (px, py, pz, E, mass, rapidity, pt, phi, theta)
        
            iterations += len(vectors)
    
        elapsed = time.time() - start
        ops_per_sec = (iterations * 6) / elapsed  # 6 operations per vector
        return ops_per_sec

    def _benchmark_histograms(self):
        """Benchmark histogram operations similar to ROOT"""
        import time
        import random
    
        iterations = 0
        duration = 2.0
    
        # Create a simple histogram
        bins = 100
        min_val = 0
        max_val = 100
        hist = [0] * (bins + 2)  # Include underflow and overflow
    
        start = time.time()
        end_time = start + duration
    
        while time.time() < end_time:
            # Fill histogram with random values
            for _ in range(10000):
                value = random.uniform(min_val, max_val)

                # Calculate bin index
                bin_idx = int((value - min_val) / (max_val - min_val) * bins) + 1

                # Handle edge cases
                if bin_idx < 1:
                    bin_idx = 0  # Underflow
                elif bin_idx > bins:
                    bin_idx = bins + 1  # Overflow

                # Fill histogram
                hist[bin_idx] += 1

            # Scale histogram
            total = sum(hist)
            if total:
                scale = 1.0 / total
                for i in range(len(hist)):
                    hist[i] *= scale

            iterations += 10000

        elapsed = time.time() - start
        ops_per_sec = (iterations * 2) / elapsed  # Fill and scale operations
        return ops_per_sec

    def _benchmark_event_generation(self):
        """Benchmark simple event generation simulation"""
        import time
        import random
        import math

        iterations = 0
        duration = 2.0

        start = time.time()
        end_time = start + duration

        while time.time() < end_time:
            # Generate a simple event with particles
            for _ in range(1000):
                # Number of particles in this event (Poisson-like distribution)
                n_particles = max(0, int(random.gauss(50, 10)))

                # Generate particles
                particles = []
                for i in range(n_particles):
                    # Random momentum components
                    px = random.gauss(0, 50)
                    py = random.gauss(0, 50)
                    pz = random.gauss(0, 100)

                    # Calculate transverse momentum
                    pt = math.sqrt(px * px + py * py)

                    # Calculate energy (assuming massless particles)
                    E = math.sqrt(px * px + py * py + pz * pz)

                    # Calculate eta (pseudorapidity)
                    denom = px * px + py * py + pz * pz
                    theta = math.acos(pz / math.sqrt(denom)) if denom > 0 else 0
                    eta = -math.log(math.tan(theta / 2)) if 0 < theta < math.pi else 0

                    # Calculate phi
                    phi = math.atan2(py, px)

                    particles.append((px, py, pz, E, pt, eta, phi))

                # Simple analysis: count high pt particles
                high_pt_count = sum(1 for p in particles if p[4] > 50)  # pt > 50

            iterations += 1000

        elapsed = time.time() - start
        events_per_sec = iterations / elapsed if elapsed > 0 else 0
        return events_per_sec

    def _calculate_cern_score(self, cpu_results, mem_results, disk_results,
                              four_vector_score, histogram_score, event_score):
        """Calculate CERN-specific performance score"""
        # Base scores from standard benchmarks
        cpu_score = cpu_results.get('score', 0)
        mem_score = mem_results.get('score', 0)
        disk_score = disk_results.get('score', 0)

        # Normalize CERN-specific benchmarks (using arbitrary reference points)
        four_vector_norm = min(10, four_vector_score / 1000000)  # 1M ops/s = score 10
        histogram_norm = min(10, histogram_score / 500000)      # 500k ops/s = score 10
        event_norm = min(10, event_score / 1000)                # 1k events/s = score 10

        # Weighted average (giving more weight to CERN-specific benchmarks)
        cern_score = (cpu_score * 0.15 +
                      mem_score * 0.1 +
                      disk_score * 0.1 +
                      four_vector_norm * 0.25 +
                      histogram_norm * 0.25 +
                      event_norm * 0.15)

        return cern_score

# In builtin.py, add:
    def cmd_grid_submit(self, args, cmd_dict):
        """Submit job to CERN grid computing infrastructure"""
        if not args:
            print("Usage: grid-submit [options] script.sh")
            print("Options:")
            print("  --vo <virtual-organization>  Specify VO (default: cms)")
            print("  --queue <queue>              Specify queue")
            print("  --memory <size>              Memory requirement")
            print("  --cores <n>                  CPU cores required")
            return
    
        # Parse grid-specific options
        vo = "cms"  # Default VO
        queue = "default"
        memory = "2GB"
        cores = 1
    
        i = 0
        while i < len(args) - 1:  # Leave the last arg as the script
            arg = args[i]
        
            if arg == "--vo" and i + 1 < len(args):
                vo = args[i + 1]
                i += 2
            elif arg == "--queue" and i + 1 < len(args):
                queue = args[i + 1]
                i += 2
            elif arg == "--memory" and i + 1 < len(args):
                memory = args[i + 1]
                i += 2
            elif arg == "--cores" and i + 1 < len(args):
                try:
                    cores = int(args[i + 1])
                except ValueError:
                    print(f"Invalid cores value: {args[i + 1]}")
                i += 2
            else:
                i += 1
    
        script = args[-1]
    
        print(f"Submitting to CERN Grid:")
        print(f"  Script: {script}")
        print(f"  VO: {vo}")
        print(f"  Queue: {queue}")
        print(f"  Memory: {memory}")
        print(f"  Cores: {cores}")
        print("(Grid submission not yet implemented)")


    # ===== Helper Methods =====
    def _format_bytes(self, bytes_val):
        """Format bytes in human-readable form"""
        if not bytes_val:
            return "0 B"

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"

    def _format_time(self, seconds):
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"