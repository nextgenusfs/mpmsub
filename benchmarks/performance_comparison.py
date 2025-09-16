#!/usr/bin/env python3
"""
Performance benchmarks comparing mpmsub vs naive parallel execution.

This script demonstrates the benefits of mpmsub's memory-aware scheduling
by comparing it against simple multiprocessing approaches.
"""

import time
import json
import psutil
import subprocess
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path to import mpmsub
sys.path.insert(0, str(Path(__file__).parent.parent))
import mpmsub


class PerformanceBenchmark:
    """Comprehensive performance benchmarking suite for mpmsub."""
    
    def __init__(self, output_dir="benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {}
        
    def create_memory_intensive_jobs(self, num_jobs=20, memory_per_job="500M"):
        """Create jobs that allocate significant memory."""
        jobs = []
        for i in range(num_jobs):
            # Python script that allocates memory and holds it
            script = f"""
import time
import sys

# Allocate {memory_per_job} of memory
mb_to_allocate = {mpmsub.parse_memory_string(memory_per_job) // (1024*1024)}
data = bytearray(mb_to_allocate * 1024 * 1024)

# Hold memory for a bit to simulate real work
time.sleep(2)

print(f"Job {{i}} completed with {{mb_to_allocate}}MB")
"""
            
            # Write script to temp file
            script_file = self.output_dir / f"memory_job_{i}.py"
            script_file.write_text(script)
            
            jobs.append({
                "cmd": [sys.executable, str(script_file)],
                "p": 1,
                "m": memory_per_job,
                "id": f"memory_job_{i}"
            })
        return jobs
    
    def create_cpu_intensive_jobs(self, num_jobs=10, duration=3):
        """Create CPU-intensive jobs."""
        jobs = []
        for i in range(num_jobs):
            script = f"""
import time
import math

# CPU-intensive calculation
start = time.time()
result = 0
while time.time() - start < {duration}:
    result += math.sqrt(time.time())

print(f"CPU job {{i}} completed: {{result:.2f}}")
"""
            
            script_file = self.output_dir / f"cpu_job_{i}.py"
            script_file.write_text(script)
            
            jobs.append({
                "cmd": [sys.executable, str(script_file)],
                "p": 2,  # Request 2 CPUs
                "m": "100M",
                "id": f"cpu_job_{i}"
            })
        return jobs
    
    def benchmark_mpmsub(self, jobs, max_cpus=None, max_memory=None):
        """Benchmark mpmsub execution."""
        if max_cpus is None:
            max_cpus = psutil.cpu_count()
        if max_memory is None:
            max_memory = f"{int(psutil.virtual_memory().total * 0.8 / (1024**3))}G"
            
        print(f"🚀 Running mpmsub benchmark with {len(jobs)} jobs...")
        print(f"   Resources: {max_cpus} CPUs, {max_memory} memory")
        
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        # Run with mpmsub
        cluster = mpmsub.cluster(p=max_cpus, m=max_memory, progress_bar=True)
        for job in jobs:
            cluster.jobs.append(job)
        
        results = cluster.run()
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        
        return {
            "method": "mpmsub",
            "total_time": end_time - start_time,
            "peak_memory_delta": max(0, end_memory - start_memory),
            "jobs_completed": len(cluster.completed_jobs),
            "jobs_failed": len(cluster.failed_jobs),
            "avg_job_time": sum(j.get('runtime', 0) for j in cluster.completed_jobs) / max(1, len(cluster.completed_jobs)),
            "memory_efficiency": cluster.completed_jobs[0].get('memory_used', 0) if cluster.completed_jobs else 0
        }
    
    def benchmark_naive_parallel(self, jobs, max_workers=None):
        """Benchmark naive parallel execution using ThreadPoolExecutor."""
        if max_workers is None:
            max_workers = psutil.cpu_count()
            
        print(f"⚡ Running naive parallel benchmark with {len(jobs)} jobs...")
        print(f"   Max workers: {max_workers}")
        
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        def run_job(job):
            try:
                result = subprocess.run(job["cmd"], capture_output=True, text=True, timeout=60)
                return {"success": result.returncode == 0, "job": job}
            except Exception as e:
                return {"success": False, "job": job, "error": str(e)}
        
        completed = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(run_job, jobs))
            
        for result in results:
            if result["success"]:
                completed += 1
            else:
                failed += 1
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        
        return {
            "method": "naive_parallel",
            "total_time": end_time - start_time,
            "peak_memory_delta": max(0, end_memory - start_memory),
            "jobs_completed": completed,
            "jobs_failed": failed,
            "avg_job_time": (end_time - start_time) / max(1, len(jobs)),
            "memory_efficiency": 0  # Can't measure individual job memory
        }
    
    def benchmark_sequential(self, jobs):
        """Benchmark sequential execution."""
        print(f"🐌 Running sequential benchmark with {len(jobs)} jobs...")
        
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        completed = 0
        failed = 0
        
        for job in jobs:
            try:
                result = subprocess.run(job["cmd"], capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    completed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        
        return {
            "method": "sequential",
            "total_time": end_time - start_time,
            "peak_memory_delta": max(0, end_memory - start_memory),
            "jobs_completed": completed,
            "jobs_failed": failed,
            "avg_job_time": (end_time - start_time) / max(1, len(jobs)),
            "memory_efficiency": 0
        }
    
    def run_memory_pressure_test(self):
        """Test performance under memory pressure."""
        print("\n" + "="*60)
        print("🧠 MEMORY PRESSURE TEST")
        print("="*60)
        
        # Create jobs that would exceed system memory if run naively
        available_memory = psutil.virtual_memory().available
        job_memory = "800M"  # Each job wants 800MB
        num_jobs = min(20, int(available_memory / mpmsub.parse_memory_string(job_memory)) + 5)  # Intentionally over-allocate
        
        print(f"Creating {num_jobs} jobs requiring {job_memory} each")
        print(f"Total requested: {num_jobs * 800}MB, Available: {available_memory // (1024**2)}MB")
        
        jobs = self.create_memory_intensive_jobs(num_jobs, job_memory)
        
        # Test mpmsub (should handle memory pressure gracefully)
        try:
            mpmsub_result = self.benchmark_mpmsub(jobs, max_memory="4G")  # Constrain memory
            self.results["memory_pressure_mpmsub"] = mpmsub_result
        except Exception as e:
            print(f"mpmsub failed: {e}")
            self.results["memory_pressure_mpmsub"] = {"error": str(e)}
        
        # Test naive parallel (likely to fail or be very slow)
        try:
            naive_result = self.benchmark_naive_parallel(jobs, max_workers=4)  # Limit workers
            self.results["memory_pressure_naive"] = naive_result
        except Exception as e:
            print(f"Naive parallel failed: {e}")
            self.results["memory_pressure_naive"] = {"error": str(e)}
    
    def run_mixed_workload_test(self):
        """Test with mixed CPU and memory intensive jobs."""
        print("\n" + "="*60)
        print("🔀 MIXED WORKLOAD TEST")
        print("="*60)
        
        # Create mixed workload
        memory_jobs = self.create_memory_intensive_jobs(8, "300M")
        cpu_jobs = self.create_cpu_intensive_jobs(6, duration=2)
        mixed_jobs = memory_jobs + cpu_jobs
        
        print(f"Mixed workload: {len(memory_jobs)} memory jobs + {len(cpu_jobs)} CPU jobs")
        
        # Test all methods
        methods = [
            ("mpmsub", lambda: self.benchmark_mpmsub(mixed_jobs)),
            ("naive_parallel", lambda: self.benchmark_naive_parallel(mixed_jobs)),
            ("sequential", lambda: self.benchmark_sequential(mixed_jobs))
        ]
        
        for method_name, benchmark_func in methods:
            try:
                result = benchmark_func()
                self.results[f"mixed_workload_{method_name}"] = result
            except Exception as e:
                print(f"{method_name} failed: {e}")
                self.results[f"mixed_workload_{method_name}"] = {"error": str(e)}
    
    def run_scalability_test(self):
        """Test scalability with increasing job counts."""
        print("\n" + "="*60)
        print("📈 SCALABILITY TEST")
        print("="*60)
        
        job_counts = [5, 10, 20, 30]
        
        for count in job_counts:
            print(f"\nTesting with {count} jobs...")
            jobs = self.create_memory_intensive_jobs(count, "200M")
            
            # Only test mpmsub and naive for scalability
            for method_name, benchmark_func in [
                ("mpmsub", lambda: self.benchmark_mpmsub(jobs)),
                ("naive_parallel", lambda: self.benchmark_naive_parallel(jobs))
            ]:
                try:
                    result = benchmark_func()
                    self.results[f"scalability_{count}jobs_{method_name}"] = result
                except Exception as e:
                    print(f"{method_name} with {count} jobs failed: {e}")
                    self.results[f"scalability_{count}jobs_{method_name}"] = {"error": str(e)}
    
    def generate_report(self):
        """Generate a comprehensive performance report."""
        report_file = self.output_dir / "performance_report.json"
        
        # Add system info
        self.results["system_info"] = {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "python_version": sys.version,
            "mpmsub_version": getattr(mpmsub, "__version__", "development")
        }
        
        # Save detailed results
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate summary
        self.print_summary()
        
        print(f"\n📊 Detailed results saved to: {report_file}")
    
    def print_summary(self):
        """Print a human-readable summary."""
        print("\n" + "="*60)
        print("📊 PERFORMANCE BENCHMARK SUMMARY")
        print("="*60)
        
        # Memory pressure comparison
        if "memory_pressure_mpmsub" in self.results and "memory_pressure_naive" in self.results:
            mpmsub_time = self.results["memory_pressure_mpmsub"].get("total_time", float('inf'))
            naive_time = self.results["memory_pressure_naive"].get("total_time", float('inf'))
            
            if mpmsub_time < float('inf') and naive_time < float('inf'):
                speedup = naive_time / mpmsub_time
                print(f"🧠 Memory Pressure Test:")
                print(f"   mpmsub: {mpmsub_time:.1f}s")
                print(f"   naive:  {naive_time:.1f}s")
                print(f"   Speedup: {speedup:.2f}x faster with mpmsub")
        
        # Mixed workload comparison
        mixed_results = {k: v for k, v in self.results.items() if k.startswith("mixed_workload_")}
        if mixed_results:
            print(f"\n🔀 Mixed Workload Test:")
            for method, result in mixed_results.items():
                method_name = method.replace("mixed_workload_", "")
                if "total_time" in result:
                    print(f"   {method_name:12}: {result['total_time']:.1f}s ({result['jobs_completed']} completed)")
        
        # Scalability trends
        scalability_results = {k: v for k, v in self.results.items() if k.startswith("scalability_")}
        if scalability_results:
            print(f"\n📈 Scalability Test (time vs job count):")
            job_counts = sorted(set(int(k.split('_')[1].replace('jobs', '')) for k in scalability_results.keys()))
            
            for count in job_counts:
                mpmsub_key = f"scalability_{count}jobs_mpmsub"
                naive_key = f"scalability_{count}jobs_naive_parallel"
                
                if mpmsub_key in scalability_results and naive_key in scalability_results:
                    mpmsub_time = scalability_results[mpmsub_key].get("total_time", 0)
                    naive_time = scalability_results[naive_key].get("total_time", 0)
                    print(f"   {count:2d} jobs: mpmsub {mpmsub_time:.1f}s vs naive {naive_time:.1f}s")


def main():
    """Run the complete benchmark suite."""
    print("🚀 mpmsub Performance Benchmark Suite")
    print("=" * 60)
    print("This benchmark compares mpmsub against naive parallel execution")
    print("to demonstrate the benefits of memory-aware scheduling.\n")
    
    benchmark = PerformanceBenchmark()
    
    try:
        # Run all benchmark tests
        benchmark.run_memory_pressure_test()
        benchmark.run_mixed_workload_test()
        benchmark.run_scalability_test()
        
        # Generate comprehensive report
        benchmark.generate_report()
        
    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup temp files
        for script_file in benchmark.output_dir.glob("*_job_*.py"):
            script_file.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
