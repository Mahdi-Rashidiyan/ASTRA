"""
Advanced HPC Job Management Features
Implements: checkpointing, job templates, distributed computing
"""

import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import time

@dataclass
class Checkpoint:
    """Job checkpoint for recovery"""
    job_id: int
    timestamp: float
    state: Dict[str, Any]
    iteration: int = 0
    progress: float = 0.0
    
    def save(self, filepath: Path):
        """Save checkpoint to disk"""
        with open(filepath, 'wb') as f:
            pickle.dump(asdict(self), f)
    
    @staticmethod
    def load(filepath: Path) -> 'Checkpoint':
        """Load checkpoint from disk"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        return Checkpoint(**data)

class CheckpointManager:
    """Manage job checkpoints for recovery"""
    
    def __init__(self, checkpoint_dir: Path = Path('checkpoints')):
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.checkpoints = {}
    
    def save_checkpoint(self, job_id: int, state: Dict, iteration: int = 0, progress: float = 0.0):
        """Save job checkpoint"""
        checkpoint = Checkpoint(
            job_id=job_id,
            timestamp=time.time(),
            state=state,
            iteration=iteration,
            progress=progress
        )
        
        filepath = self.checkpoint_dir / f"job_{job_id}_iter_{iteration}.pkl"
        checkpoint.save(filepath)
        self.checkpoints[job_id] = checkpoint
        
        return filepath
    
    def load_latest_checkpoint(self, job_id: int) -> Optional[Checkpoint]:
        """Load latest checkpoint for job"""
        checkpoints = list(self.checkpoint_dir.glob(f"job_{job_id}_*.pkl"))
        
        if not checkpoints:
            return None
        
        # Get latest by modification time
        latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
        return Checkpoint.load(latest)
    
    def cleanup_old_checkpoints(self, job_id: int, keep_count: int = 3):
        """Remove old checkpoints, keeping most recent"""
        checkpoints = sorted(
            self.checkpoint_dir.glob(f"job_{job_id}_*.pkl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for old_checkpoint in checkpoints[keep_count:]:
            old_checkpoint.unlink()

@dataclass
class JobTemplate:
    """Template for common job patterns"""
    name: str
    description: str
    command: str
    default_cores: int = 4
    default_memory_gb: float = 8.0
    default_time_hours: float = 1.0
    default_queue: str = 'default'
    environment_vars: Dict[str, str] = None
    input_files: list = None
    output_files: list = None
    
    def __post_init__(self):
        if self.environment_vars is None:
            self.environment_vars = {}
        if self.input_files is None:
            self.input_files = []
        if self.output_files is None:
            self.output_files = []
    
    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(asdict(self), indent=2)
    
    @staticmethod
    def from_json(json_str: str) -> 'JobTemplate':
        """Create from JSON"""
        data = json.loads(json_str)
        return JobTemplate(**data)

class TemplateManager:
    """Manage job templates"""
    
    def __init__(self, template_dir: Path = Path('templates')):
        self.template_dir = template_dir
        self.template_dir.mkdir(exist_ok=True)
        self.templates = {}
        self._load_templates()
    
    def register_template(self, template: JobTemplate):
        """Register a new template"""
        self.templates[template.name] = template
        self._save_template(template)
    
    def get_template(self, name: str) -> Optional[JobTemplate]:
        """Get template by name"""
        return self.templates.get(name)
    
    def list_templates(self) -> list:
        """List all available templates"""
        return list(self.templates.keys())
    
    def _save_template(self, template: JobTemplate):
        """Save template to disk"""
        filepath = self.template_dir / f"{template.name}.json"
        with open(filepath, 'w') as f:
            f.write(template.to_json())
    
    def _load_templates(self):
        """Load templates from disk"""
        for filepath in self.template_dir.glob("*.json"):
            try:
                with open(filepath, 'r') as f:
                    template = JobTemplate.from_json(f.read())
                self.templates[template.name] = template
            except Exception as e:
                print(f"Error loading template {filepath}: {e}")

class DistributedJobExecutor:
    """Execute jobs across multiple nodes"""
    
    def __init__(self, nodes: list):
        self.nodes = nodes  # List of node hostnames/IPs
        self.job_locations = {}
    
    def distribute_job(self, job_id: int, command: str, num_nodes: int = 1) -> Dict:
        """Distribute job across nodes"""
        if num_nodes > len(self.nodes):
            return {'success': False, 'error': 'Not enough nodes available'}
        
        selected_nodes = self.nodes[:num_nodes]
        
        # In production, would use SSH/RPC to execute remotely
        distribution = {
            'job_id': job_id,
            'command': command,
            'nodes': selected_nodes,
            'mpi_enabled': num_nodes > 1,
        }
        
        self.job_locations[job_id] = distribution
        return {'success': True, 'distribution': distribution}
    
    def get_job_distribution(self, job_id: int) -> Optional[Dict]:
        """Get distribution info for job"""
        return self.job_locations.get(job_id)

# Example usage and demonstrations
def demonstrate_advanced_features():
    """Demonstrate advanced HPC features"""
    
    print("\n" + "=" * 70)
    print("ADVANCED HPC JOB MANAGEMENT FEATURES")
    print("=" * 70)
    
    # 1. Checkpoint Management
    print("\n1. CHECKPOINT MANAGEMENT")
    print("-" * 70)
    
    checkpoint_mgr = CheckpointManager()
    
    # Save checkpoint
    state = {
        'iteration': 100,
        'model_weights': [1.0, 2.0, 3.0],
        'loss': 0.45,
        'learning_rate': 0.001
    }
    
    filepath = checkpoint_mgr.save_checkpoint(
        job_id=1,
        state=state,
        iteration=100,
        progress=0.45
    )
    print(f"Checkpoint saved: {filepath}")
    
    # Load checkpoint
    loaded = checkpoint_mgr.load_latest_checkpoint(job_id=1)
    if loaded:
        print(f"Loaded checkpoint: iteration={loaded.iteration}, progress={loaded.progress:.0%}")
        print(f"State keys: {list(loaded.state.keys())}")
    
    # 2. Job Templates
    print("\n2. JOB TEMPLATES")
    print("-" * 70)
    
    template_mgr = TemplateManager()
    
    # Create and register templates
    templates = [
        JobTemplate(
            name='ml_training',
            description='Machine learning model training',
            command='python train.py',
            default_cores=8,
            default_memory_gb=16.0,
            default_time_hours=4.0,
            environment_vars={'TF_CPP_MIN_LOG_LEVEL': '2'},
            input_files=['data/train.csv'],
            output_files=['model.pkl']
        ),
        JobTemplate(
            name='data_processing',
            description='Data preprocessing and cleaning',
            command='python preprocess.py',
            default_cores=4,
            default_memory_gb=8.0,
            default_time_hours=2.0,
        ),
        JobTemplate(
            name='simulation',
            description='Physics simulation',
            command='./run_simulation',
            default_cores=16,
            default_memory_gb=32.0,
            default_time_hours=8.0,
            default_queue='gpu',
        ),
    ]
    
    for template in templates:
        template_mgr.register_template(template)
    
    print("\nRegistered Templates:")
    for name in template_mgr.list_templates():
        template = template_mgr.get_template(name)
        print(f"  {name}:")
        print(f"    Command: {template.command}")
        print(f"    Default: {template.default_cores} cores, {template.default_memory_gb} GB RAM")
    
    # 3. Distributed Execution
    print("\n3. DISTRIBUTED JOB EXECUTION")
    print("-" * 70)
    
    nodes = ['node01.hpc.local', 'node02.hpc.local', 'node03.hpc.local', 'node04.hpc.local']
    dist_executor = DistributedJobExecutor(nodes)
    
    # Single-node job
    result = dist_executor.distribute_job(1, 'python analysis.py', num_nodes=1)
    print(f"\nSingle-node job: {result['success']}")
    if result['success']:
        dist = result['distribution']
        print(f"  Nodes: {dist['nodes']}")
        print(f"  MPI: {dist['mpi_enabled']}")
    
    # Multi-node job
    result = dist_executor.distribute_job(2, 'mpirun -n 4 ./simulation', num_nodes=4)
    print(f"\nMulti-node job: {result['success']}")
    if result['success']:
        dist = result['distribution']
        print(f"  Nodes: {', '.join(dist['nodes'])}")
        print(f"  MPI: {dist['mpi_enabled']}")
    
    # 4. Advanced Features Summary
    print("\n" + "-" * 70)
    print("ADVANCED FEATURES SUMMARY")
    print("-" * 70)
    
    features = {
        'Checkpointing': {
            'save': 'Save job state at intervals',
            'load': 'Resume from last checkpoint',
            'cleanup': 'Remove old checkpoints',
        },
        'Job Templates': {
            'predefined': 'Pre-configured job patterns',
            'parameters': 'Customize with parameters',
            'environment': 'Include environment setup',
        },
        'Distributed Execution': {
            'multi_node': 'Run across multiple nodes',
            'mpi': 'MPI support for parallelism',
            'load_balance': 'Distribute work across nodes',
        },
    }
    
    for feature, capabilities in features.items():
        print(f"\n{feature}:")
        for cap, desc in capabilities.items():
            print(f"  • {desc}")

if __name__ == '__main__':
    demonstrate_advanced_features()
