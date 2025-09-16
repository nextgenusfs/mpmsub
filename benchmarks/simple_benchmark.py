#!/usr/bin/env python3
"""
Simple performance demonstration showing mpmsub benefits.

This script creates a realistic scenario where mpmsub's memory-aware
scheduling provides clear advantages over naive parallel execution.
"""

import time
import sys
import psutil
import subprocess
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to import mpmsub
sys.path.insert(0, str(Path(__file__).parent.parent))
import mpmsub


def create_memory_hog_script(memory_mb, duration_sec):
    """Create a Python script that allocates memory and runs for a specified time."""
    script_content = f"""
import time
import sys

# Allocate {memory_mb}MB of memory
print(f"Allocating {memory_mb}MB of memory...")
data = bytearray({memory_mb} * 1024 * 1024)

# Simulate some work
print(f"Working for {duration_sec} seconds...")
time.sleep({duration_sec})

print(f"Job completed successfully!")
"""
    return script_content


def run_naive_parallel(jobs, max_workers=4):
    """Run jobs using naive ThreadPoolExecutor (no memory awareness)."""
    print(f"🔥 Running {len(jobs)} jobs with naive parallel execution...")
    print(f"   Max workers: {max_workers} (no memory limits)")

    def run_single_job(job_info):
        job_id, cmd = job_info
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            runtime = time.time() - start_time
            return {
                "id": job_id,
                "success": result.returncode == 0,
                "runtime": runtime,
                "output": result.stdout.strip(),
            }
        except subprocess.TimeoutExpired:
            return {"id": job_id, "success": False, "error": "timeout"}
        except Exception as e:
            return {"id": job_id, "success": False, "error": str(e)}

    start_time = time.time()
    start_memory = psutil.virtual_memory().used

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(run_single_job, enumerate(jobs)))

    total_time = time.time() - start_time
    peak_memory = psutil.virtual_memory().used

    successful = sum(1 for r in results if r.get("success", False))

    print(f"   ✅ Completed: {successful}/{len(jobs)} jobs")
    print(f"   ⏱️  Total time: {total_time:.1f}s")
    print(f"   🧠 Memory delta: {(peak_memory - start_memory) / (1024**2):.0f}MB")

    return {
        "method": "naive_parallel",
        "total_time": total_time,
        "successful_jobs": successful,
        "memory_delta_mb": (peak_memory - start_memory) / (1024**2),
    }


def run_mpmsub(jobs, max_memory="2G", memory_per_job=800):
    """Run jobs using mpmsub with memory awareness."""
    print(f"🚀 Running {len(jobs)} jobs with mpmsub...")
    print(f"   Memory limit: {max_memory}")

    start_time = time.time()
    start_memory = psutil.virtual_memory().used

    # Create mpmsub cluster
    cluster = mpmsub.cluster(p=psutil.cpu_count(), m=max_memory, progress_bar=True)

    # Add jobs
    for i, cmd in enumerate(jobs):
        cluster.jobs.append(
            {
                "cmd": cmd,
                "p": 1,
                "m": f"{memory_per_job + 100}M",  # Each job needs memory + buffer
                "id": f"job_{i}",
            }
        )

    # Run jobs
    cluster.run()

    total_time = time.time() - start_time
    peak_memory = psutil.virtual_memory().used

    successful = len(cluster.completed_jobs)

    print(f"   ✅ Completed: {successful}/{len(jobs)} jobs")
    print(f"   ⏱️  Total time: {total_time:.1f}s")
    print(f"   🧠 Memory delta: {(peak_memory - start_memory) / (1024**2):.0f}MB")

    return {
        "method": "mpmsub",
        "total_time": total_time,
        "successful_jobs": successful,
        "memory_delta_mb": (peak_memory - start_memory) / (1024**2),
    }


def main():
    """Run a simple but compelling performance comparison."""
    print("🎯 mpmsub Performance Demonstration")
    print("=" * 50)

    # Get system info
    total_memory_gb = psutil.virtual_memory().total / (1024**3)
    cpu_count = psutil.cpu_count()

    print(f"System: {cpu_count} CPUs, {total_memory_gb:.1f}GB RAM")
    print()

    # Create a scenario where memory matters
    # Scale based on available memory to ensure we create pressure
    available_gb = total_memory_gb * 0.7  # Use 70% of available memory
    memory_per_job = max(500, int(available_gb * 1024 / 6))  # MB per job
    num_jobs = max(
        6, int(available_gb * 1024 / memory_per_job * 1.5)
    )  # 1.5x oversubscribe
    job_duration = 3  # seconds

    print(
        f"Scenario: {num_jobs} jobs, each requiring {memory_per_job}MB for {job_duration}s"
    )
    print(
        f"Total memory if run simultaneously: {num_jobs * memory_per_job / 1024:.1f}GB"
    )
    print()

    # Create temporary scripts
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create job scripts
        jobs = []
        for i in range(num_jobs):
            script_content = create_memory_hog_script(memory_per_job, job_duration)
            script_file = temp_path / f"job_{i}.py"
            script_file.write_text(script_content)
            jobs.append([sys.executable, str(script_file)])

        print("🔬 Running benchmarks...\n")

        # Test 1: Naive parallel execution
        print("Test 1: Naive Parallel Execution")
        print("-" * 35)
        try:
            naive_result = run_naive_parallel(jobs, max_workers=4)
        except Exception as e:
            print(f"❌ Naive parallel failed: {e}")
            naive_result = None

        print()

        # Test 2: mpmsub with memory awareness
        print("Test 2: mpmsub Memory-Aware Execution")
        print("-" * 40)
        try:
            mpmsub_result = run_mpmsub(
                jobs, max_memory="2G", memory_per_job=memory_per_job
            )
        except Exception as e:
            print(f"❌ mpmsub failed: {e}")
            mpmsub_result = None

        print()

        # Compare results
        print("📊 COMPARISON RESULTS")
        print("=" * 25)

        if naive_result and mpmsub_result:
            naive_time = naive_result["total_time"]
            mpmsub_time = mpmsub_result["total_time"]

            if naive_time > 0 and mpmsub_time > 0:
                speedup = naive_time / mpmsub_time
                efficiency = (
                    mpmsub_result["successful_jobs"] / naive_result["successful_jobs"]
                    if naive_result["successful_jobs"] > 0
                    else float("inf")
                )

                print(f"⏱️  Execution Time:")
                print(f"   Naive parallel: {naive_time:.1f}s")
                print(f"   mpmsub:         {mpmsub_time:.1f}s")
                print(f"   Speedup:        {speedup:.2f}x")
                print()

                print(f"✅ Success Rate:")
                print(
                    f"   Naive parallel: {naive_result['successful_jobs']}/{num_jobs}"
                )
                print(
                    f"   mpmsub:         {mpmsub_result['successful_jobs']}/{num_jobs}"
                )
                print(f"   Efficiency:     {efficiency:.2f}x")
                print()

                print(f"🧠 Memory Usage:")
                print(
                    f"   Naive parallel: {naive_result['memory_delta_mb']:.0f}MB peak"
                )
                print(
                    f"   mpmsub:         {mpmsub_result['memory_delta_mb']:.0f}MB peak"
                )
                print()

                # Conclusion
                if speedup > 1.1 and efficiency >= 1.0:
                    print("🎉 CONCLUSION: mpmsub provides significant benefits!")
                    print(f"   • {speedup:.1f}x faster execution")
                    print(f"   • {efficiency:.1f}x better success rate")
                    print("   • Intelligent memory management prevents system overload")
                elif efficiency > 1.1:
                    print("🎉 CONCLUSION: mpmsub provides better reliability!")
                    print(f"   • {efficiency:.1f}x better success rate")
                    print("   • Prevents memory-related failures")
                else:
                    print("📝 CONCLUSION: Results are comparable")
                    print("   • mpmsub provides safety without performance penalty")

        else:
            print("❌ Could not complete comparison due to errors")

        print()
        print("💡 Key Benefits of mpmsub:")
        print("   • Prevents memory exhaustion and system crashes")
        print("   • Optimizes job scheduling based on available resources")
        print("   • Provides detailed performance metrics")
        print("   • Handles mixed CPU/memory workloads intelligently")


if __name__ == "__main__":
    main()
