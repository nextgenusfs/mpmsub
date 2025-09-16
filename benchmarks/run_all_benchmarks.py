#!/usr/bin/env python3
"""
Run all mpmsub performance benchmarks.

This script executes all available benchmarks and provides a comprehensive
performance comparison between mpmsub and naive parallel execution.
"""

import sys
import time
import subprocess
from pathlib import Path


def run_benchmark(script_name, description):
    """Run a single benchmark script and capture results."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Running: {script_name}")
    print()
    
    script_path = Path(__file__).parent / script_name
    
    try:
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,  # Show output in real-time
            text=True,
            timeout=1800  # 30 minute timeout
        )
        runtime = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n✅ {description} completed successfully in {runtime:.1f}s")
            return True
        else:
            print(f"\n❌ {description} failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n⏰ {description} timed out after 30 minutes")
        return False
    except Exception as e:
        print(f"\n💥 {description} crashed: {e}")
        return False


def main():
    """Run all benchmarks in sequence."""
    print("🎯 mpmsub Performance Benchmark Suite")
    print("=" * 50)
    print("This will run all available performance benchmarks to demonstrate")
    print("the benefits of mpmsub's memory-aware scheduling.\n")
    
    # Check if we're in the right directory
    benchmark_dir = Path(__file__).parent
    if not (benchmark_dir / "simple_benchmark.py").exists():
        print("❌ Error: Benchmark scripts not found!")
        print(f"   Expected location: {benchmark_dir}")
        print("   Please run this script from the mpmsub repository root.")
        sys.exit(1)
    
    # List of benchmarks to run
    benchmarks = [
        ("simple_benchmark.py", "Simple Performance Demonstration"),
        ("bioinformatics_benchmark.py", "Bioinformatics Pipeline Benchmark"),
        ("performance_comparison.py", "Comprehensive Performance Analysis")
    ]
    
    # Check that all benchmark scripts exist
    missing_scripts = []
    for script_name, _ in benchmarks:
        if not (benchmark_dir / script_name).exists():
            missing_scripts.append(script_name)
    
    if missing_scripts:
        print("❌ Error: Missing benchmark scripts:")
        for script in missing_scripts:
            print(f"   • {script}")
        sys.exit(1)
    
    print(f"Found {len(benchmarks)} benchmark scripts:")
    for i, (script_name, description) in enumerate(benchmarks, 1):
        print(f"   {i}. {description} ({script_name})")
    
    print(f"\nEstimated total runtime: 15-25 minutes")
    print("Press Ctrl+C at any time to stop.\n")
    
    # Ask for confirmation
    try:
        response = input("Continue with all benchmarks? [Y/n]: ").strip().lower()
        if response and response not in ['y', 'yes']:
            print("Benchmark suite cancelled.")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nBenchmark suite cancelled.")
        sys.exit(0)
    
    # Run benchmarks
    start_time = time.time()
    results = []
    
    for script_name, description in benchmarks:
        try:
            success = run_benchmark(script_name, description)
            results.append((description, success))
        except KeyboardInterrupt:
            print(f"\n⚠️  Benchmark suite interrupted by user")
            break
    
    total_time = time.time() - start_time
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 BENCHMARK SUITE SUMMARY")
    print(f"{'='*60}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"⏱️  Total runtime: {total_time/60:.1f} minutes")
    print(f"✅ Successful benchmarks: {successful}/{total}")
    print()
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status}: {description}")
    
    if successful == total:
        print(f"\n🎉 All benchmarks completed successfully!")
        print("   The results demonstrate mpmsub's performance benefits")
        print("   over naive parallel execution approaches.")
    elif successful > 0:
        print(f"\n⚠️  {total - successful} benchmark(s) failed")
        print("   Check the output above for error details.")
    else:
        print(f"\n❌ All benchmarks failed")
        print("   This may indicate a system or installation issue.")
    
    print(f"\n💡 For more details, see:")
    print(f"   • benchmarks/README.md")
    print(f"   • Individual benchmark scripts")
    print(f"   • mpmsub documentation")


if __name__ == "__main__":
    main()
