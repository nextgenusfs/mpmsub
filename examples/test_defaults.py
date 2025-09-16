#!/usr/bin/env python3
"""
Test the new default behavior for p and m parameters.
"""

import mpmsub


def main():
    print("Testing job defaults")
    print("=" * 30)
    
    # Create cluster
    p = mpmsub.cluster(p=4, m="1G")
    
    # Test 1: Job with no p or m specified
    print("Test 1: Job with no p or m specified")
    p.jobs.append({"cmd": ["echo", "test1"]})
    job1 = p.job_queue.pending_jobs[0]
    print(f"  p={job1['p']}, m={job1['m']}")
    
    # Test 2: Job with only p specified
    print("Test 2: Job with only p specified")
    p.jobs.append({"cmd": ["echo", "test2"], "p": 2})
    job2 = p.job_queue.pending_jobs[1]
    print(f"  p={job2['p']}, m={job2['m']}")
    
    # Test 3: Job with only m specified
    print("Test 3: Job with only m specified")
    p.jobs.append({"cmd": ["echo", "test3"], "m": "100M"})
    job3 = p.job_queue.pending_jobs[2]
    print(f"  p={job3['p']}, m={job3['m']}")
    
    # Test 4: Job with both p and m specified
    print("Test 4: Job with both p and m specified")
    p.jobs.append({"cmd": ["echo", "test4"], "p": 3, "m": "200M"})
    job4 = p.job_queue.pending_jobs[3]
    print(f"  p={job4['p']}, m={job4['m']}")
    
    print("\nExpected behavior:")
    print("  Test 1: p=1 (default), m=None (unlimited)")
    print("  Test 2: p=2 (specified), m=None (unlimited)")
    print("  Test 3: p=1 (default), m=100 (specified)")
    print("  Test 4: p=3 (specified), m=200 (specified)")
    
    # Run the jobs to make sure they work
    print("\nRunning jobs...")
    p.verbose = False
    p.run()
    
    print(f"All {len(p.completed_jobs)} jobs completed successfully!")
    for job in p.completed_jobs:
        print(f"  {job.job_id}: {job.stdout.strip()}")


if __name__ == "__main__":
    main()
