#!/usr/bin/env python3
"""
Test profiling with jobs that actually use memory.
"""

import mpmsub


def main():
    print("Testing profiling with memory-using jobs")
    print("=" * 50)
    
    # Create cluster
    p = mpmsub.cluster(p=2, m="1G")
    
    # Add jobs that actually use memory and run for a bit
    p.jobs.append({
        "cmd": ["python3", "-c", """
import time
import sys

# Allocate 10MB of memory
data = bytearray(10 * 1024 * 1024)  # 10MB
print(f'Allocated {len(data)} bytes (~10MB)')

# Hold it for a moment so monitoring can catch it
time.sleep(0.5)

# Use the data to prevent optimization
checksum = sum(data[:1000])
print(f'Checksum: {checksum}')
print('Memory test job completed')
"""]
    })
    
    p.jobs.append({
        "cmd": ["python3", "-c", """
import time

# Allocate 5MB of memory
data = 'x' * (5 * 1024 * 1024)  # 5MB string
print(f'Allocated string of {len(data)} chars (~5MB)')

# Hold it for a moment
time.sleep(0.3)

print('String test job completed')
"""]
    })
    
    # Profile the jobs
    print("Running profiling...")
    results = p.profile()
    
    print(f"\nProfiled {len(results)} jobs")
    for result in results:
        print(f"Job {result.job_id}: Memory used = {result.memory_used:.1f}MB, Runtime = {result.runtime:.2f}s")


if __name__ == "__main__":
    main()
