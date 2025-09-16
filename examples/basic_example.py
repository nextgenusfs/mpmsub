#!/usr/bin/env python3
"""
Basic example of using mpmsub library.
"""

import sys
import os

# Add parent directory to path so we can import mpmsub
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mpmsub
from mpmsub.utils import format_memory, format_duration


def main():
    """Run a basic example with some simple commands."""
    print("MPMSUB Basic Example")
    print("=" * 40)

    # Create a cluster with 4 CPUs and 2GB memory
    p = mpmsub.cluster(p=4, m="2G")

    print(
        f"Created cluster with {p.max_cpus} CPUs and {format_memory(p.max_memory_mb)} memory"
    )

    # Add some simple jobs
    jobs = [
        {"cmd": ["echo", "Hello from job 1"], "p": 1, "m": "10M"},
        {"cmd": ["sleep", "1"], "p": 1, "m": "5M"},
        {"cmd": ["echo", "Hello from job 2"], "p": 1, "m": "10M"},
        {
            "cmd": [
                "python3",
                "-c",
                "print('Python job'); import time; time.sleep(0.5)",
            ],
            "p": 1,
            "m": "50M",
        },
        {"cmd": ["ls", "-la"], "p": 1, "m": "5M"},
    ]

    # Add jobs to the cluster
    for job in jobs:
        job_id = p.jobs.append(job)
        print(f"Added job {job_id}: {' '.join(job['cmd'][:3])}")

    print(f"\nQueued {len(p.jobs)} jobs")

    # Run all jobs
    print("\nStarting execution...")
    results = p.run()

    # Print summary
    p.print_summary()

    # Show individual results
    print("\nDetailed Results:")
    print("-" * 40)
    for job in p.completed_jobs:
        print(f"Job {job.job_id}:")
        print(f"  Command: {' '.join(job.cmd)}")
        print(f"  Runtime: {format_duration(job.runtime)}")
        print(f"  Memory: {format_memory(job.memory_used)}")
        print(f"  Success: {job.success}")
        if job.stdout.strip():
            print(f"  Output: {job.stdout.strip()}")
        print()


if __name__ == "__main__":
    main()
