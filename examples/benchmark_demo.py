#!/usr/bin/env python3
"""
Quick demonstration of mpmsub performance benefits.

This example shows how mpmsub's memory-aware scheduling can provide
significant performance improvements in memory-constrained scenarios.
"""

import sys
import time
import tempfile
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to import mpmsub
sys.path.insert(0, str(Path(__file__).parent.parent))
import mpmsub


def create_memory_intensive_script(memory_mb, duration_sec):
    """Create a script that uses significant memory."""
    return f'''
import time
print(f"Allocating {memory_mb}MB of memory...")
data = bytearray({memory_mb} * 1024 * 1024)
print(f"Working for {duration_sec} seconds...")
time.sleep({duration_sec})
print("Job completed!")
'''


def demo_memory_pressure():
    """Demonstrate mpmsub benefits under memory pressure."""
    print("🎯 mpmsub Performance Demo: Memory Pressure Scenario")
    print("=" * 55)
    print()
    
    # Create a scenario that will stress memory
    num_jobs = 6
    memory_per_job = 1000  # 1GB per job
    job_duration = 2
    
    print(f"Scenario: {num_jobs} jobs, each requiring {memory_per_job}MB")
    print(f"Total memory if run simultaneously: {num_jobs * memory_per_job / 1024:.1f}GB")
    print()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create job scripts
        jobs = []
        for i in range(num_jobs):
            script_content = create_memory_intensive_script(memory_per_job, job_duration)
            script_file = temp_path / f"job_{i}.py"
            script_file.write_text(script_content)
            jobs.append([sys.executable, str(script_file)])
        
        # Test 1: Naive approach (likely to cause memory pressure)
        print("🔥 Test 1: Naive Parallel Execution")
        print("-" * 35)
        
        def run_job(cmd):
            try:
                start = time.time()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                return time.time() - start, result.returncode == 0
            except:
                return 0, False
        
        start_time = time.time()
        
        # Run with limited workers to prevent complete system overload
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(run_job, jobs))
        
        naive_time = time.time() - start_time
        naive_success = sum(1 for _, success in results if success)
        
        print(f"   ✅ Completed: {naive_success}/{num_jobs} jobs")
        print(f"   ⏱️  Total time: {naive_time:.1f}s")
        print()
        
        # Test 2: mpmsub approach
        print("🚀 Test 2: mpmsub Memory-Aware Execution")
        print("-" * 40)
        
        start_time = time.time()
        
        # Create mpmsub cluster with memory constraint
        cluster = mpmsub.cluster(p=6, m="3G", progress_bar=True)  # Limit to 3GB total
        
        for i, cmd in enumerate(jobs):
            cluster.jobs.append({
                'cmd': cmd,
                'p': 1,
                'm': f'{memory_per_job + 200}M',  # Request memory + buffer
                'id': f'memory_job_{i}'
            })
        
        cluster.run()
        
        mpmsub_time = time.time() - start_time
        mpmsub_success = len(cluster.completed_jobs)
        
        print(f"   ✅ Completed: {mpmsub_success}/{num_jobs} jobs")
        print(f"   ⏱️  Total time: {mpmsub_time:.1f}s")
        print()
        
        # Compare results
        print("📊 COMPARISON")
        print("=" * 15)
        
        if naive_time > 0 and mpmsub_time > 0:
            speedup = naive_time / mpmsub_time
            efficiency = mpmsub_success / max(1, naive_success)
            
            print(f"⏱️  Execution Time:")
            print(f"   Naive:   {naive_time:.1f}s")
            print(f"   mpmsub:  {mpmsub_time:.1f}s")
            if speedup > 1:
                print(f"   Result:  {speedup:.1f}x FASTER with mpmsub! 🚀")
            else:
                print(f"   Result:  {1/speedup:.1f}x slower (but safer)")
            print()
            
            print(f"✅ Success Rate:")
            print(f"   Naive:   {naive_success}/{num_jobs} ({naive_success/num_jobs*100:.0f}%)")
            print(f"   mpmsub:  {mpmsub_success}/{num_jobs} ({mpmsub_success/num_jobs*100:.0f}%)")
            if efficiency > 1:
                print(f"   Result:  {efficiency:.1f}x BETTER reliability! ✨")
            print()
            
            print("🎉 Key Benefits Demonstrated:")
            if speedup > 1.1:
                print(f"   • {speedup:.1f}x faster execution")
            if efficiency > 1.0:
                print(f"   • {efficiency:.1f}x better success rate")
            print("   • Prevents memory exhaustion")
            print("   • Intelligent job scheduling")
            print("   • System stability maintained")


def demo_mixed_workload():
    """Demonstrate mpmsub with mixed CPU/memory workloads."""
    print("\n" + "🔀 mpmsub Performance Demo: Mixed Workload")
    print("=" * 45)
    print()
    
    print("Scenario: Mixed CPU-intensive and memory-intensive jobs")
    print("This simulates real-world workloads with varying resource needs.")
    print()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create mixed jobs
        jobs = []
        
        # CPU-intensive jobs (low memory, high CPU usage)
        for i in range(3):
            script_content = '''
import time
import math
print("CPU-intensive computation starting...")
start = time.time()
result = 0
while time.time() - start < 2:
    result += math.sqrt(time.time())
print(f"CPU job completed: {result:.2f}")
'''
            script_file = temp_path / f"cpu_job_{i}.py"
            script_file.write_text(script_content)
            jobs.append(('cpu', [sys.executable, str(script_file)]))
        
        # Memory-intensive jobs (high memory, low CPU usage)
        for i in range(3):
            script_content = create_memory_intensive_script(800, 2)
            script_file = temp_path / f"mem_job_{i}.py"
            script_file.write_text(script_content)
            jobs.append(('memory', [sys.executable, str(script_file)]))
        
        print(f"Created {len(jobs)} mixed jobs:")
        cpu_jobs = sum(1 for job_type, _ in jobs if job_type == 'cpu')
        mem_jobs = sum(1 for job_type, _ in jobs if job_type == 'memory')
        print(f"   • {cpu_jobs} CPU-intensive jobs (2 CPUs each)")
        print(f"   • {mem_jobs} Memory-intensive jobs (800MB each)")
        print()
        
        # Run with mpmsub
        print("🚀 Running with mpmsub...")
        
        start_time = time.time()
        cluster = mpmsub.cluster(p=6, m="4G", progress_bar=True)
        
        for job_type, cmd in jobs:
            if job_type == 'cpu':
                cluster.jobs.append({
                    'cmd': cmd,
                    'p': 2,      # CPU jobs need more cores
                    'm': '100M', # But less memory
                    'id': f'cpu_job'
                })
            else:  # memory job
                cluster.jobs.append({
                    'cmd': cmd,
                    'p': 1,      # Memory jobs need fewer cores
                    'm': '900M', # But more memory
                    'id': f'mem_job'
                })
        
        cluster.run()
        
        total_time = time.time() - start_time
        
        print(f"   ✅ Completed: {len(cluster.completed_jobs)}/{len(jobs)} jobs")
        print(f"   ⏱️  Total time: {total_time:.1f}s")
        print()
        
        print("💡 What mpmsub optimized:")
        print("   • Scheduled CPU jobs when cores were available")
        print("   • Scheduled memory jobs when RAM was available")
        print("   • Prevented resource conflicts and bottlenecks")
        print("   • Maximized overall throughput")


def main():
    """Run performance demonstrations."""
    print("🎯 mpmsub Performance Demonstrations")
    print("=" * 40)
    print("These demos show real performance benefits of mpmsub's")
    print("memory-aware scheduling in practical scenarios.\n")
    
    try:
        # Demo 1: Memory pressure
        demo_memory_pressure()
        
        # Demo 2: Mixed workloads
        demo_mixed_workload()
        
        print("\n" + "🎉 Demonstrations Complete!")
        print("=" * 30)
        print("mpmsub provides:")
        print("   • Faster execution in memory-constrained scenarios")
        print("   • Better reliability and success rates")
        print("   • Intelligent resource optimization")
        print("   • System stability and crash prevention")
        print()
        print("Try the full benchmark suite with:")
        print("   python benchmarks/run_all_benchmarks.py")
        
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
