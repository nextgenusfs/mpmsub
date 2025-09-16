#!/usr/bin/env python3
"""
Demonstration of both dictionary and object-oriented job interfaces in mpmsub.
"""

import sys
import os

# Add parent directory to path for local testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mpmsub

def demo_dictionary_interface():
    """Demonstrate the traditional dictionary interface."""
    print("=" * 60)
    print("DICTIONARY INTERFACE (Traditional)")
    print("=" * 60)
    
    p = mpmsub.cluster(p=2, m='1G', progress_bar=False)
    
    # Add jobs using dictionaries
    p.jobs.append({
        "cmd": ["echo", "Hello from dict job 1"],
        "p": 1,
        "m": "100M"
    })
    
    p.jobs.append({
        "cmd": ["echo", "Hello from dict job 2"],
        "p": 1,
        "m": "150M",
        "id": "custom_dict_job"
    })
    
    print("Added jobs using dictionary interface:")
    for i, job in enumerate(p.jobs, 1):
        print(f"  Job {i}: {job['cmd']} (p={job['p']}, m={job['m']})")
    
    results = p.run()
    print(f"✓ Completed {results['jobs']['completed']} dictionary jobs\n")

def demo_object_interface():
    """Demonstrate the new object-oriented interface."""
    print("=" * 60)
    print("OBJECT-ORIENTED INTERFACE (New)")
    print("=" * 60)
    
    p = mpmsub.cluster(p=2, m='1G', progress_bar=False)
    
    # Method 1: Direct Job creation
    job1 = mpmsub.Job(
        cmd=["echo", "Hello from Job object 1"],
        p=1,
        m="100M"
    )
    p.jobs.append(job1)
    
    # Method 2: Builder pattern (fluent interface)
    job2 = mpmsub.Job(["echo", "Hello from Job object 2"]) \
        .cpu(1) \
        .memory("150M") \
        .with_id("custom_object_job")
    p.jobs.append(job2)
    
    # Method 3: Step-by-step building
    job3 = mpmsub.Job(["echo", "Hello from Job object 3"])
    job3.cpu(1)
    job3.memory("200M")
    job3.with_timeout(30.0)
    p.jobs.append(job3)
    
    print("Added jobs using object interface:")
    for i, job in enumerate(p.jobs, 1):
        print(f"  Job {i}: {job['cmd']} (p={job['p']}, m={job['m']})")
    
    results = p.run()
    print(f"✓ Completed {results['jobs']['completed']} object jobs\n")

def demo_mixed_interface():
    """Demonstrate mixing both interfaces."""
    print("=" * 60)
    print("MIXED INTERFACE (Dictionary + Object)")
    print("=" * 60)
    
    p = mpmsub.cluster(p=2, m='1G', progress_bar=False)
    
    # Mix dictionary and object approaches
    jobs_to_add = [
        # Dictionary job
        {"cmd": ["echo", "Mixed: dict job"], "p": 1, "m": "100M"},
        
        # Object job
        mpmsub.Job(["echo", "Mixed: object job"]).cpu(1).memory("150M"),
        
        # Another dictionary job
        {"cmd": ["echo", "Mixed: another dict"], "p": 1},
        
        # Another object job with more features
        mpmsub.Job(["echo", "Mixed: complex object"])
            .cpu(1)
            .memory("200M")
            .with_id("complex_mixed_job")
            .with_timeout(60.0)
    ]
    
    # Add all jobs at once
    p.jobs.extend(jobs_to_add)
    
    print("Added mixed jobs:")
    for i, job in enumerate(p.jobs, 1):
        job_type = "dict" if isinstance(jobs_to_add[i-1], dict) else "object"
        print(f"  Job {i} ({job_type}): {job['cmd']} (p={job['p']}, m={job['m']})")
    
    results = p.run()
    print(f"✓ Completed {results['jobs']['completed']} mixed jobs\n")

def demo_advanced_features():
    """Demonstrate advanced Job object features."""
    print("=" * 60)
    print("ADVANCED JOB OBJECT FEATURES")
    print("=" * 60)
    
    # Job with environment variables
    env_job = mpmsub.Job(["env"]) \
        .cpu(1) \
        .memory("50M") \
        .environment({"CUSTOM_VAR": "hello", "ANOTHER_VAR": "world"}) \
        .with_id("env_job")
    
    # Job with working directory
    pwd_job = mpmsub.Job(["pwd"]) \
        .cpu(1) \
        .memory("50M") \
        .working_dir("/tmp") \
        .with_id("pwd_job")
    
    # Job with timeout
    timeout_job = mpmsub.Job(["sleep", "0.1"]) \
        .cpu(1) \
        .memory("50M") \
        .with_timeout(5.0) \
        .with_id("timeout_job")
    
    print("Advanced job examples:")
    print(f"  Environment job: {env_job}")
    print(f"  Working dir job: {pwd_job}")
    print(f"  Timeout job: {timeout_job}")
    
    # Show dictionary conversion
    print("\nJob.to_dict() output:")
    print(f"  {env_job.to_dict()}")
    
    p = mpmsub.cluster(p=2, m='1G', progress_bar=False)
    p.jobs.extend([env_job, pwd_job, timeout_job])
    
    results = p.run()
    print(f"\n✓ Completed {results['jobs']['completed']} advanced jobs")

def demo_ide_support():
    """Show how the Job class provides better IDE support."""
    print("=" * 60)
    print("IDE SUPPORT DEMONSTRATION")
    print("=" * 60)
    
    print("The Job class provides:")
    print("  ✓ Type hints for all parameters")
    print("  ✓ Autocomplete for methods")
    print("  ✓ Documentation strings")
    print("  ✓ Builder pattern for fluent interface")
    print("  ✓ Clear parameter names (no cryptic 'p' and 'm')")
    print("  ✓ Validation at creation time")
    print()
    
    # Example of clear, self-documenting code
    analysis_job = mpmsub.Job(["python", "analyze_data.py", "input.csv"]) \
        .cpu(cores=4) \
        .memory(mem="8G") \
        .working_dir("/data/analysis") \
        .environment({"PYTHONPATH": "/custom/libs"}) \
        .with_timeout(seconds=3600) \
        .with_id("data_analysis")
    
    print("Example of self-documenting job creation:")
    print("  mpmsub.Job(['python', 'analyze_data.py', 'input.csv'])")
    print("    .cpu(cores=4)")
    print("    .memory(mem='8G')")
    print("    .working_dir('/data/analysis')")
    print("    .environment({'PYTHONPATH': '/custom/libs'})")
    print("    .with_timeout(seconds=3600)")
    print("    .with_id('data_analysis')")
    print()
    print(f"Result: {analysis_job}")

if __name__ == "__main__":
    print("mpmsub Job Interface Demonstration")
    print("This shows both dictionary and object-oriented approaches\n")
    
    demo_dictionary_interface()
    demo_object_interface()
    demo_mixed_interface()
    demo_advanced_features()
    demo_ide_support()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✓ Dictionary interface: Backward compatible, concise")
    print("✓ Object interface: Type-safe, IDE-friendly, self-documenting")
    print("✓ Mixed usage: Use what works best for each situation")
    print("✓ Builder pattern: Fluent, readable job construction")
    print("✓ Full compatibility: Both interfaces work seamlessly together")
