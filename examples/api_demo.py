#!/usr/bin/env python3
"""
Complete API demonstration for mpmsub library.
Shows all the key features mentioned in your original request.
"""

import sys
import os

# Add parent directory to path so we can import mpmsub
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mpmsub


def main():
    """Demonstrate the exact API you requested."""
    print("MPMSUB API Demonstration")
    print("=" * 40)
    print("This shows the exact API you requested:\n")
    
    # Step 1: Initialize a multiprocessing object
    print("# Create cluster with 6 CPUs and 16GB memory")
    print("p = mpmsub.cluster(p=6, m='16G')")
    p = mpmsub.cluster(p=6, m="16G")
    print(f"✓ Created cluster with {p.max_cpus} CPUs and {p.max_memory_mb}MB memory\n")
    
    # Step 2: Add jobs with different requirements
    print("# Add jobs with different resource requirements")
    
    jobs_to_add = [
        {"cmd": ["echo", "Job 1: Light task"], "p": 1, "m": "100M"},
        {"cmd": ["python3", "-c", "import time; print('Job 2: Python task'); time.sleep(1)"], "p": 1, "m": "200M"},
        {"cmd": ["echo", "Job 3: Another light task"], "p": 1, "m": "50M"},
        {"cmd": ["python3", "-c", "import time; print('Job 4: CPU intensive'); time.sleep(2)"], "p": 2, "m": "300M"},
        {"cmd": ["echo", "Job 5: Final task"], "p": 1, "m": "100M"},
    ]
    
    for i, job in enumerate(jobs_to_add, 1):
        print(f"p.jobs.append({job})")
        job_id = p.jobs.append(job)
        print(f"✓ Added job {job_id}: {job['cmd'][0]} command, {job['p']} CPU, {job['m']} memory\n")
    
    print(f"Total jobs queued: {len(p.jobs)}\n")
    
    # Step 3: Run with optimal scheduling
    print("# Run all jobs with optimal scheduling")
    print("results = p.run()")
    print("Running...\n")
    
    results = p.run()
    
    print("\n" + "="*60)
    print("EXECUTION COMPLETED")
    print("="*60)
    
    # Step 4: Analyze results - estimated vs actual
    print("\n# Analyze estimated vs actual resource usage")
    print("for job in p.completed_jobs:")
    print("    print(f'Job: {job.cmd}')")
    print("    print(f'Runtime: {job.runtime:.2f}s')")
    print("    print(f'Memory used: {job.memory_used:.1f}MB')")
    print()
    
    for job in p.completed_jobs:
        print(f"Job: {' '.join(job.cmd[:3])}...")
        print(f"  Runtime: {job.runtime:.2f}s")
        print(f"  Memory used: {job.memory_used:.1f}MB")
        print(f"  Success: {job.success}")
        if job.stdout.strip():
            print(f"  Output: {job.stdout.strip()}")
        print()
    
    # Show summary statistics
    print("# Summary statistics")
    stats = p.stats
    print(f"Total jobs: {stats['jobs']['total']}")
    print(f"Completed: {stats['jobs']['completed']}")
    print(f"Failed: {stats['jobs']['failed']}")
    print(f"Total runtime: {stats['cluster']['runtime_formatted']}")
    
    print("\n" + "="*60)
    print("API DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nKey features demonstrated:")
    print("✓ Simple cluster initialization: mpmsub.cluster(p=6, m='16G')")
    print("✓ Easy job addition: p.jobs.append({'cmd': [...], 'p': 1, 'm': '1g'})")
    print("✓ Intelligent scheduling: p.run()")
    print("✓ Runtime and memory tracking")
    print("✓ Performance analysis and comparison")


if __name__ == "__main__":
    main()
