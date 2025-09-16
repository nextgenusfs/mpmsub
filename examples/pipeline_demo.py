#!/usr/bin/env python3
"""
Demonstration of mpmsub pipeline features and new enhancements.

This example shows:
1. CalVer versioning
2. Resource description
3. Pipeline support for chaining subprocess calls
4. Both dictionary and object-oriented interfaces for pipelines
"""

import mpmsub
import tempfile
import os


def demo_version_and_resources():
    """Demonstrate version info and resource description."""
    print("=" * 60)
    print("VERSION AND RESOURCE INFORMATION")
    print("=" * 60)
    
    print(f"mpmsub version: {mpmsub.__version__}")
    print()
    
    # Create cluster with resource description
    p = mpmsub.cluster(p=2, m='1G', describe=True, verbose=False)
    
    return p


def demo_simple_pipeline():
    """Demonstrate basic pipeline functionality."""
    print("=" * 60)
    print("SIMPLE PIPELINE DEMO")
    print("=" * 60)
    
    # Create a temporary file with some data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("apple\nbanana\ncherry\napricot\nblueberry\navocado\n")
        temp_file = f.name
    
    try:
        p = mpmsub.cluster(p=2, m='1G', verbose=False, progress_bar=False)
        
        # Method 1: Using the pipeline() convenience function
        pipeline_job = mpmsub.pipeline([
            ["cat", temp_file],
            ["grep", "a"],  # Lines containing 'a'
            ["sort"]        # Sort the results
        ], p=1, m="50M", id="grep_sort_pipeline")
        
        p.jobs.append(pipeline_job)
        
        print("Added pipeline job:")
        print(f"  {pipeline_job}")
        
        results = p.run()
        
        # Show results
        for job in p.completed_jobs:
            print(f"\nPipeline output:")
            print(job.stdout.strip())
            
        print(f"\n✓ Completed {results['jobs']['completed']} pipeline jobs")
        
    finally:
        os.unlink(temp_file)


def demo_object_pipeline():
    """Demonstrate object-oriented pipeline creation."""
    print("\n" + "=" * 60)
    print("OBJECT-ORIENTED PIPELINE DEMO")
    print("=" * 60)
    
    # Create test data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("line 1: hello world\nline 2: foo bar\nline 3: hello foo\nline 4: world bar\n")
        temp_file = f.name
    
    try:
        p = mpmsub.cluster(p=2, m='1G', verbose=False, progress_bar=False)
        
        # Method 2: Using Job with Pipeline object
        pipeline_obj = mpmsub.Pipeline([
            ["cat", temp_file],
            ["grep", "hello"],
            ["wc", "-l"]
        ])
        
        job = mpmsub.Job(cmd=pipeline_obj) \
            .cpu(1) \
            .memory("50M") \
            .with_id("count_hello_lines")
        
        p.jobs.append(job)
        
        # Method 3: Using Job with pipe_to() builder pattern
        job2 = mpmsub.Job(["cat", temp_file]) \
            .pipe_to(["grep", "foo"]) \
            .pipe_to(["wc", "-l"]) \
            .cpu(1) \
            .memory("50M") \
            .with_id("count_foo_lines")
        
        p.jobs.append(job2)
        
        print("Added object-oriented pipeline jobs:")
        print(f"  Job 1: {job}")
        print(f"  Job 2: {job2}")
        
        results = p.run()
        
        # Show results
        for job in p.completed_jobs:
            print(f"\n{job.job_id} output: {job.stdout.strip()}")
            
        print(f"\n✓ Completed {results['jobs']['completed']} object pipeline jobs")
        
    finally:
        os.unlink(temp_file)


def demo_complex_pipeline():
    """Demonstrate complex pipeline with error handling."""
    print("\n" + "=" * 60)
    print("COMPLEX PIPELINE WITH ERROR HANDLING")
    print("=" * 60)
    
    p = mpmsub.cluster(p=2, m='1G', verbose=False, progress_bar=False)
    
    # Pipeline that should succeed
    success_pipeline = mpmsub.pipeline([
        ["echo", "success test"],
        ["tr", "a-z", "A-Z"],  # Convert to uppercase
        ["sed", "s/SUCCESS/VICTORY/g"]  # Replace SUCCESS with VICTORY
    ], p=1, m="50M", id="success_pipeline")
    
    # Pipeline that should fail (invalid command)
    fail_pipeline = mpmsub.pipeline([
        ["echo", "failure test"],
        ["nonexistent_command"],  # This will fail
        ["cat"]
    ], p=1, m="50M", id="fail_pipeline")
    
    p.jobs.extend([success_pipeline, fail_pipeline])
    
    print("Added complex pipelines:")
    print(f"  Success: {success_pipeline}")
    print(f"  Failure: {fail_pipeline}")
    
    results = p.run()
    
    # Show results
    print(f"\nResults:")
    for job in p.completed_jobs:
        print(f"  ✓ {job.job_id}: {job.stdout.strip()}")
    
    for job in p.failed_jobs:
        print(f"  ✗ {job.job_id}: {job.error}")
    
    print(f"\n✓ Completed {results['jobs']['completed']} jobs, {results['jobs']['failed']} failed")


def demo_mixed_jobs():
    """Demonstrate mixing single commands and pipelines."""
    print("\n" + "=" * 60)
    print("MIXED SINGLE COMMANDS AND PIPELINES")
    print("=" * 60)
    
    p = mpmsub.cluster(p=3, m='1G', verbose=False, progress_bar=False)
    
    # Mix of single commands and pipelines
    jobs = [
        # Single command
        mpmsub.job(["echo", "Single command"], p=1, m="50M", id="single_cmd"),
        
        # Pipeline using convenience function
        mpmsub.pipeline([
            ["echo", "Pipeline output"],
            ["tr", "a-z", "A-Z"]
        ], p=1, m="50M", id="simple_pipeline"),
        
        # Another single command
        mpmsub.job(["date"], p=1, m="50M", id="date_cmd"),
        
        # Complex pipeline using object interface
        mpmsub.Job(["echo", "Complex pipeline"]) \
            .pipe_to(["sed", "s/Complex/Advanced/g"]) \
            .pipe_to(["tr", "a-z", "A-Z"]) \
            .cpu(1) \
            .memory("50M") \
            .with_id("complex_pipeline")
    ]
    
    p.jobs.extend(jobs)
    
    print("Added mixed job types:")
    for job in jobs:
        print(f"  {job}")
    
    results = p.run()
    
    # Show results
    print(f"\nResults:")
    for job in p.completed_jobs:
        output = job.stdout.strip() if job.stdout else "(no output)"
        print(f"  {job.job_id}: {output}")
    
    print(f"\n✓ Completed {results['jobs']['completed']} mixed jobs")


def main():
    """Run all pipeline demonstrations."""
    print("🚀 MPMSUB PIPELINE AND ENHANCEMENT DEMO")
    print("=" * 60)
    
    # Demo 1: Version and resources
    cluster = demo_version_and_resources()
    
    # Demo 2: Simple pipeline
    demo_simple_pipeline()
    
    # Demo 3: Object-oriented pipelines
    demo_object_pipeline()
    
    # Demo 4: Complex pipelines with error handling
    demo_complex_pipeline()
    
    # Demo 5: Mixed job types
    demo_mixed_jobs()
    
    print("\n" + "=" * 60)
    print("🎉 ALL PIPELINE DEMOS COMPLETED!")
    print("=" * 60)
    print()
    print("Key features demonstrated:")
    print("  ✓ CalVer versioning (2025.01.0)")
    print("  ✓ Resource description with describe=True")
    print("  ✓ Pipeline support for chaining commands")
    print("  ✓ Multiple pipeline creation methods:")
    print("    - mpmsub.pipeline() convenience function")
    print("    - Job with Pipeline object")
    print("    - Job with pipe_to() builder pattern")
    print("  ✓ Error handling in pipelines")
    print("  ✓ Mixed single commands and pipelines")
    print("  ✓ Backward compatibility maintained")


if __name__ == "__main__":
    main()
