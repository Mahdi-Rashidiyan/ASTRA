"""
Job queue management with priority scheduling
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
from utils.logger import get_logger

class Priority(Enum):
    """Job priority levels"""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0

@dataclass
class Job:
    """Represents a scheduled job"""
    job_id: int
    command: str
    args: List[str]
    priority: Priority = Priority.NORMAL
    queue: str = 'default'
    cores: int = 1
    memory: str = '1GB'
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: str = 'queued'  # queued, running, completed, failed, cancelled
    process_id: Optional[int] = None
    return_code: Optional[int] = None

class JobQueue:
    """Manages job scheduling with priority queues"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        
        # Job storage
        self.jobs: Dict[int, Job] = {}
        self.queues: Dict[str, List[int]] = {}  # queue_name -> [job_ids]
        self.next_job_id = 1
        
        # Initialize queues from config
        queue_names = config.get('scheduler', 'queues') or ['default']
        if isinstance(queue_names, dict):
            queue_names = ['default']
        for queue_name in queue_names:
            self.queues[queue_name] = []
    
    def submit_job(self, command: str, args: List[str], queue: str = 'default',
                   priority: str = 'normal', cores: int = 1, memory: str = '1GB') -> int:
        """Submit a job to the queue"""
        
        # Convert priority string to enum
        try:
            priority_enum = Priority[priority.upper()]
        except KeyError:
            priority_enum = Priority.NORMAL
        
        # Create job
        job = Job(
            job_id=self.next_job_id,
            command=command,
            args=args,
            priority=priority_enum,
            queue=queue,
            cores=cores,
            memory=memory
        )
        
        # Store job
        self.jobs[self.next_job_id] = job
        
        # Add to queue
        if queue not in self.queues:
            self.queues[queue] = []
        self.queues[queue].append(self.next_job_id)
        
        # Sort by priority
        self._sort_queue(queue)
        
        job_id = self.next_job_id
        self.next_job_id += 1
        
        self.logger.info(f"Job {job_id} submitted to {queue} queue")
        return job_id
    
    def get_next_job(self, queue: str = 'default') -> Optional[Job]:
        """Get the next job to run from a queue"""
        if queue not in self.queues or not self.queues[queue]:
            return None
        
        job_id = self.queues[queue][0]
        job = self.jobs[job_id]
        
        if job.status == 'queued':
            return job
        
        return None
    
    def start_job(self, job_id: int) -> bool:
        """Mark a job as started"""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        job.status = 'running'
        job.started_at = time.time()
        self.logger.info(f"Job {job_id} started")
        return True
    
    def complete_job(self, job_id: int, return_code: int = 0) -> bool:
        """Mark a job as completed"""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        job.status = 'completed'
        job.completed_at = time.time()
        job.return_code = return_code
        
        # Remove from queue
        for queue_name, job_ids in self.queues.items():
            if job_id in job_ids:
                job_ids.remove(job_id)
        
        self.logger.info(f"Job {job_id} completed with return code {return_code}")
        return True
    
    def cancel_job(self, job_id: int) -> bool:
        """Cancel a job"""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        
        # Only cancel if not already running
        if job.status in ('running', 'completed'):
            return False
        
        job.status = 'cancelled'
        
        # Remove from queue
        for queue_name, job_ids in self.queues.items():
            if job_id in job_ids:
                job_ids.remove(job_id)
        
        self.logger.info(f"Job {job_id} cancelled")
        return True
    
    def get_job(self, job_id: int) -> Optional[Job]:
        """Get job details"""
        return self.jobs.get(job_id)
    
    def get_jobs(self, queue: Optional[str] = None, status: Optional[str] = None) -> List[Job]:
        """Get all jobs, optionally filtered by queue or status"""
        jobs = list(self.jobs.values())
        
        if queue:
            jobs = [j for j in jobs if j.queue == queue]
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        return jobs
    
    def get_queue_stats(self, queue: str = 'default') -> Dict:
        """Get queue statistics"""
        jobs = [self.jobs[jid] for jid in self.queues.get(queue, [])]
        
        return {
            'queue': queue,
            'total_jobs': len(jobs),
            'queued': sum(1 for j in jobs if j.status == 'queued'),
            'running': sum(1 for j in jobs if j.status == 'running'),
            'completed': sum(1 for j in jobs if j.status == 'completed'),
            'failed': sum(1 for j in jobs if j.status == 'failed'),
            'cancelled': sum(1 for j in jobs if j.status == 'cancelled'),
        }
    
    def _sort_queue(self, queue: str):
        """Sort queue by priority"""
        if queue not in self.queues:
            return
        
        job_ids = self.queues[queue]
        # Sort by priority (lower value = higher priority), then by submission time
        job_ids.sort(key=lambda jid: (
            self.jobs[jid].priority.value,
            self.jobs[jid].created_at
        ))
