#!/usr/bin/env python3
"""
Example demonstrating the profiling feature of mpmsub.

This shows how to use p.profile() to measure actual memory usage
of jobs when you don't know their requirements beforehand.
"""

import mpmsub


def main():
    print("MPMSUB Profiling Example")
    print("=" * 50)
    
    # Create cluster
    p = mpmsub.cluster(p=4, m="2G")
    print(f"Created cluster with {p.max_cpus} CPUs and {mpmsub.format_memory(p.max_memory_mb)} memory\n")
    
    # Add jobs without memory specifications (will use defaults)
    print("Adding jobs without memory specifications:")
    
    # Simple commands
    p.jobs.append({"cmd": ["echo", "Hello from job 1"]})
    p.jobs.append({"cmd": ["python3", "-c", "print('Hello from Python job')"]})
    
    # Job that uses some memory
    p.jobs.append({
        "cmd": ["python3", "-c", 
               "import sys; data = 'x' * (1024*1024*5); print(f'Used ~5MB: {len(data)} chars')"]
    })
    
    # Job with CPU requirement but no memory spec
    p.jobs.append({
        "cmd": ["python3", "-c", "import time; time.sleep(0.1); print('CPU job done')"],
        "p": 2  # Requires 2 CPUs, memory unlimited
    })
    
    print(f"Added {len(p.jobs)} jobs")
    print("Notice: No 'm' (memory) values specified - using defaults\n")
    
    # Show job details before profiling
    print("Jobs before profiling:")
    for i, job in enumerate(p.jobs):
        memory_str = f"{job['m']}MB" if job['m'] is not None else "unlimited"
        print(f"  Job {i+1}: p={job['p']}, m={memory_str}")
    print()
    
    # Profile the jobs to measure actual memory usage
    print("Running profiling to measure actual memory usage...")
    print("-" * 50)
    
    profile_results = p.profile()
    
    # Show how to use the profiling results
    print("\nHow to use these measurements:")
    print("-" * 40)
    print("# Create a new cluster with measured memory values:")
    print("p = mpmsub.cluster(p=4, m='2G')")
    print()
    
    for result in profile_results:
        if result.success and result.memory_used > 0:
            # Add 20% buffer to measured memory
            recommended = int(result.memory_used * 1.2)
            recommended_str = mpmsub.format_memory(recommended)
            cmd_preview = ' '.join(result.cmd[:2])
            print(f"p.jobs.append({{'cmd': ['{cmd_preview}', ...], 'p': {result.cpu_used}, 'm': '{recommended_str}'}})")
        elif result.success:
            cmd_preview = ' '.join(result.cmd[:2])
            print(f"p.jobs.append({{'cmd': ['{cmd_preview}', ...], 'p': {result.cpu_used}, 'm': '50M'}})")
    
    print("\n# Then run with optimized scheduling:")
    print("p.run()")
    
    print("\n" + "=" * 50)
    print("Profiling complete! Use the measured values for efficient scheduling.")


if __name__ == "__main__":
    main()
