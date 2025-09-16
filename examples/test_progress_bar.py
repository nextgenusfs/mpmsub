#!/usr/bin/env python3
"""
Test progress bar functionality in mpmsub.
"""

import sys
import os

# Add parent directory to path for local testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mpmsub

def test_progress_bar():
    """Test progress bar with various scenarios."""
    
    print("Testing mpmsub progress bar functionality\n")
    
    # Test 1: Progress bar enabled (default)
    print("=" * 50)
    print("Test 1: Progress bar enabled")
    print("=" * 50)
    
    p = mpmsub.cluster(p=2, m='1G', progress_bar=True)
    
    # Add some quick jobs
    for i in range(5):
        p.jobs.append({
            "cmd": ["sleep", "0.5"],
            "p": 1,
            "m": "100M"
        })
    
    print("Running 5 jobs with progress bar...")
    results = p.run()
    print(f"Completed {results['jobs']['completed']} jobs\n")
    
    # Test 2: Progress bar disabled
    print("=" * 50)
    print("Test 2: Progress bar disabled")
    print("=" * 50)
    
    p2 = mpmsub.cluster(p=2, m='1G', progress_bar=False)
    
    # Add some quick jobs
    for i in range(3):
        p2.jobs.append({
            "cmd": ["sleep", "0.3"],
            "p": 1,
            "m": "100M"
        })
    
    print("Running 3 jobs without progress bar...")
    results2 = p2.run()
    print(f"Completed {results2['jobs']['completed']} jobs\n")
    
    # Test 3: Progress bar with profiling
    print("=" * 50)
    print("Test 3: Progress bar with profiling")
    print("=" * 50)
    
    p3 = mpmsub.cluster(p=2, m='1G', progress_bar=True)
    
    # Add some jobs for profiling
    for i in range(3):
        p3.jobs.append({
            "cmd": ["sleep", "0.2"],
            "p": 1
        })
    
    print("Profiling 3 jobs with progress bar...")
    profile_results = p3.profile(verbose=False)
    print(f"Profiled {len(profile_results)} jobs\n")
    
    print("All progress bar tests completed successfully!")

if __name__ == "__main__":
    test_progress_bar()
