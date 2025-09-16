#!/usr/bin/env python3
"""
Example demonstrating memory-aware scheduling with mpmsub.
"""

import sys
import os

# Add parent directory to path so we can import mpmsub
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mpmsub
from mpmsub.utils import format_memory, format_duration


def main():
    """Run memory-intensive example."""
    print("MPMSUB Memory-Aware Scheduling Example")
    print("=" * 50)
    
    # Create a cluster with limited memory to demonstrate scheduling
    p = mpmsub.cluster(p=4, m="1G")  # 1GB total memory limit
    
    print(f"Created cluster with {p.max_cpus} CPUs and {format_memory(p.max_memory_mb)} memory")
    
    # Add jobs with different memory requirements
    jobs = [
        # Small memory jobs
        {"cmd": ["python3", "-c", "import time; print('Small job 1'); time.sleep(0.5)"], 
         "p": 1, "m": "50M", "id": "small_1"},
        {"cmd": ["python3", "-c", "import time; print('Small job 2'); time.sleep(0.5)"], 
         "p": 1, "m": "50M", "id": "small_2"},
        
        # Medium memory jobs
        {"cmd": ["python3", "-c", "import time; print('Medium job 1'); time.sleep(1)"], 
         "p": 1, "m": "200M", "id": "medium_1"},
        {"cmd": ["python3", "-c", "import time; print('Medium job 2'); time.sleep(1)"], 
         "p": 1, "m": "200M", "id": "medium_2"},
        
        # Large memory job that should wait for others to complete
        {"cmd": ["python3", "-c", "import time; print('Large job - needs lots of memory'); time.sleep(1.5)"], 
         "p": 1, "m": "600M", "id": "large_1"},
        
        # Another large job
        {"cmd": ["python3", "-c", "import time; print('Large job 2'); time.sleep(1)"], 
         "p": 1, "m": "500M", "id": "large_2"},
    ]
    
    # Add jobs to the cluster
    for job in jobs:
        job_id = p.jobs.append(job)
        print(f"Added {job['id']}: {job['m']} memory, {job['p']} CPU")
    
    print(f"\nQueued {len(p.jobs)} jobs")
    print("Note: Jobs will be scheduled based on available memory")
    print("Large jobs may wait for smaller ones to complete\n")
    
    # Run all jobs
    print("Starting execution...")
    results = p.run()
    
    # Print summary
    p.print_summary()
    
    # Show scheduling analysis
    print("\nScheduling Analysis:")
    print("-" * 40)
    
    # Sort jobs by start time to show execution order
    completed_jobs = sorted(p.completed_jobs, key=lambda x: x.start_time)
    
    for i, job in enumerate(completed_jobs):
        print(f"{i+1}. {job.job_id}: started at {job.start_time:.1f}s, "
              f"ran for {format_duration(job.runtime)}")
    
    print(f"\nTotal execution time: {format_duration(results['cluster']['runtime'])}")
    print("Notice how large memory jobs were delayed until sufficient memory was available!")


if __name__ == "__main__":
    main()
