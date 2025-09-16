"""
Core Cluster class for mpmsub library.
"""

import os
import sys
import time
import subprocess
import threading
import psutil
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from collections import defaultdict
import logging

from .utils import (
    parse_memory_string,
    parse_cpu_string,
    get_system_resources,
    validate_job,
    format_memory,
    format_duration,
)


class ProgressBar:
    """Simple progress bar using only standard library."""

    def __init__(self, total: int, width: int = 40, show_percent: bool = True):
        self.total = total
        self.current = 0
        self.width = width
        self.show_percent = show_percent
        self.start_time = time.time()

    def update(self, increment: int = 1):
        """Update progress by increment."""
        self.current = min(self.current + increment, self.total)
        self._draw()

    def _draw(self):
        """Draw the progress bar."""
        if self.total == 0:
            return

        # Calculate progress
        progress = self.current / self.total
        filled_width = int(self.width * progress)

        # Create bar
        bar = "█" * filled_width + "░" * (self.width - filled_width)

        # Calculate stats
        elapsed = time.time() - self.start_time

        # Build progress line
        line = f"\r[{bar}] {self.current}/{self.total}"

        if self.show_percent:
            line += f" ({progress * 100:.1f}%)"

        if self.current > 0 and elapsed > 0:
            rate = self.current / elapsed
            if rate > 0:
                eta = (self.total - self.current) / rate
                line += f" ETA: {format_duration(eta)}"

        # Write to stderr to avoid interfering with stdout
        sys.stderr.write(line)
        sys.stderr.flush()

        # Add newline when complete
        if self.current >= self.total:
            sys.stderr.write("\n")
            sys.stderr.flush()

    def finish(self):
        """Ensure progress bar shows 100% completion."""
        self.current = self.total
        self._draw()


@dataclass
class JobResult:
    """Result of a completed job."""

    job_id: str
    cmd: List[str]
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    runtime: float = 0.0
    memory_used: float = 0.0  # Peak memory in MB
    cpu_used: int = 1
    start_time: float = 0.0
    end_time: float = 0.0
    success: bool = False
    error: Optional[str] = None


@dataclass
class ResourceUsage:
    """Track resource usage over time."""

    cpu_slots_used: int = 0
    memory_used: float = 0.0  # MB
    active_jobs: int = 0


class Job:
    """
    Object-oriented interface for job specification.

    Provides a more intuitive way to create jobs with IDE support,
    while maintaining compatibility with the dictionary interface.
    """

    def __init__(
        self,
        cmd: List[str],
        p: Union[int, str, None] = None,
        m: Union[str, int, None] = None,
        id: Optional[str] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ):
        """
        Create a new job.

        Args:
            cmd: Command to execute as list of strings
            p: Number of CPU cores needed (default: 1)
            m: Memory requirement (e.g., "1G", "512M", default: unlimited)
            id: Custom job identifier (auto-generated if None)
            cwd: Working directory for the job
            env: Environment variables for the job
            timeout: Timeout in seconds
        """
        self.cmd = cmd
        self.p = p
        self.m = m
        self.id = id
        self.cwd = cwd
        self.env = env
        self.timeout = timeout

    def cpu(self, cores: Union[int, str]) -> "Job":
        """Set CPU requirement (builder pattern)."""
        self.p = cores
        return self

    def memory(self, mem: Union[str, int]) -> "Job":
        """Set memory requirement (builder pattern)."""
        self.m = mem
        return self

    def working_dir(self, path: str) -> "Job":
        """Set working directory (builder pattern)."""
        self.cwd = path
        return self

    def environment(self, env_vars: Dict[str, str]) -> "Job":
        """Set environment variables (builder pattern)."""
        self.env = env_vars
        return self

    def with_timeout(self, seconds: float) -> "Job":
        """Set timeout (builder pattern)."""
        self.timeout = seconds
        return self

    def with_id(self, job_id: str) -> "Job":
        """Set custom job ID (builder pattern)."""
        self.id = job_id
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for internal use."""
        return {
            "cmd": self.cmd,
            "p": self.p,
            "m": self.m,
            "id": self.id,
            "cwd": self.cwd,
            "env": self.env,
            "timeout": self.timeout,
        }

    def __repr__(self) -> str:
        """String representation of the job."""
        cmd_str = " ".join(self.cmd[:3])
        if len(self.cmd) > 3:
            cmd_str += "..."
        return f"Job(cmd=[{cmd_str}], p={self.p}, m={self.m})"


class JobQueue:
    """Manage job queue with priority scheduling."""

    def __init__(self):
        self.pending_jobs = []
        self.running_jobs = {}
        self.completed_jobs = []
        self.failed_jobs = []
        self._job_counter = 0
        self._lock = threading.Lock()

    def add_job(self, job: Dict[str, Any]) -> str:
        """Add a job to the queue."""
        with self._lock:
            # Validate and normalize job
            normalized_job = validate_job(job)

            # Assign unique ID if not provided
            if normalized_job["id"] is None:
                self._job_counter += 1
                normalized_job["id"] = f"job_{self._job_counter:04d}"

            self.pending_jobs.append(normalized_job)
            return normalized_job["id"]

    def get_next_job(
        self, available_cpus: int, available_memory: float
    ) -> Optional[Dict]:
        """Get the next job that can run with available resources."""
        with self._lock:
            for i, job in enumerate(self.pending_jobs):
                # Check CPU constraint
                if job["p"] > available_cpus:
                    continue

                # Check memory constraint (None means no limit)
                if job["m"] is not None and job["m"] > available_memory:
                    continue

                return self.pending_jobs.pop(i)
            return None

    def mark_running(self, job: Dict[str, Any]):
        """Mark a job as running."""
        with self._lock:
            self.running_jobs[job["id"]] = job

    def mark_completed(self, result: JobResult):
        """Mark a job as completed."""
        with self._lock:
            job_id = result.job_id
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]

            if result.success:
                self.completed_jobs.append(result)
            else:
                self.failed_jobs.append(result)

    def get_stats(self) -> Dict[str, int]:
        """Get queue statistics."""
        with self._lock:
            return {
                "pending": len(self.pending_jobs),
                "running": len(self.running_jobs),
                "completed": len(self.completed_jobs),
                "failed": len(self.failed_jobs),
                "total": len(self.pending_jobs)
                + len(self.running_jobs)
                + len(self.completed_jobs)
                + len(self.failed_jobs),
            }


class MemoryMonitor:
    """Monitor memory usage of running processes."""

    def __init__(self, sampling_interval: float = 0.5):
        self.sampling_interval = sampling_interval
        self._monitoring = {}
        self._lock = threading.Lock()

    def start_monitoring(
        self, job_id: str, process: subprocess.Popen
    ) -> threading.Thread:
        """Start monitoring a process."""

        def monitor():
            try:
                psutil_process = psutil.Process(process.pid)
                peak_memory = 0.0

                while process.poll() is None:
                    try:
                        # Get memory info for process and all children
                        memory_info = psutil_process.memory_info()
                        current_memory = memory_info.rss / (
                            1024 * 1024
                        )  # Convert to MB

                        # Include children
                        for child in psutil_process.children(recursive=True):
                            try:
                                child_memory = child.memory_info()
                                current_memory += child_memory.rss / (1024 * 1024)
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass

                        peak_memory = max(peak_memory, current_memory)

                        with self._lock:
                            self._monitoring[job_id] = {
                                "current_memory": current_memory,
                                "peak_memory": peak_memory,
                            }

                        time.sleep(self.sampling_interval)

                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        break

            except Exception:
                # Process might have ended before we could monitor it
                pass

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread

    def get_peak_memory(self, job_id: str) -> float:
        """Get peak memory usage for a job."""
        with self._lock:
            if job_id in self._monitoring:
                return self._monitoring[job_id]["peak_memory"]
            return 0.0

    def cleanup(self, job_id: str):
        """Clean up monitoring data for a job."""
        with self._lock:
            self._monitoring.pop(job_id, None)


class Cluster:
    """
    Main cluster class for managing subprocess execution with memory awareness.
    """

    def __init__(
        self,
        cpus: Union[int, str, None] = None,
        memory: Union[str, int, None] = None,
        verbose: bool = True,
        progress_bar: bool = True,
    ):
        """
        Initialize a compute cluster.

        Args:
            cpus: Number of CPUs to use. If None, auto-detects.
            memory: Memory limit (e.g., "16G", "2048M"). If None, auto-detects.
            verbose: Whether to print progress information.
            progress_bar: Whether to show a progress bar during execution.
        """
        # Parse resource specifications
        self.max_cpus = parse_cpu_string(cpus)
        self.max_memory_mb = parse_memory_string(memory)

        # Auto-detect resources if not specified
        if self.max_cpus is None or self.max_memory_mb is None:
            system_resources = get_system_resources()
            if self.max_cpus is None:
                self.max_cpus = system_resources["cpus"]
            if self.max_memory_mb is None:
                # Use 90% of available memory
                self.max_memory_mb = int(system_resources["memory_mb"] * 0.9)

        self.verbose = verbose
        self.progress_bar = progress_bar

        # Initialize components
        self.job_queue = JobQueue()
        self.memory_monitor = MemoryMonitor()
        self.resource_usage = ResourceUsage()

        # Job management
        self.jobs = JobList(self.job_queue)

        # Execution state
        self._running = False
        self._executor = None

        # Statistics
        self.start_time = None
        self.end_time = None

        # Setup logging
        self.logger = logging.getLogger("mpmsub")
        if verbose and not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    @property
    def completed_jobs(self) -> List[JobResult]:
        """Get list of completed jobs."""
        return self.job_queue.completed_jobs

    @property
    def failed_jobs(self) -> List[JobResult]:
        """Get list of failed jobs."""
        return self.job_queue.failed_jobs

    @property
    def stats(self) -> Dict[str, Any]:
        """Get cluster statistics."""
        queue_stats = self.job_queue.get_stats()

        runtime = 0.0
        if self.start_time:
            end_time = self.end_time or time.time()
            runtime = end_time - self.start_time

        return {
            "cluster": {
                "max_cpus": self.max_cpus,
                "max_memory_mb": self.max_memory_mb,
                "max_memory": format_memory(self.max_memory_mb),
                "runtime": runtime,
                "runtime_formatted": format_duration(runtime),
            },
            "jobs": queue_stats,
            "resources": {
                "cpu_slots_used": self.resource_usage.cpu_slots_used,
                "memory_used": format_memory(self.resource_usage.memory_used),
                "active_jobs": self.resource_usage.active_jobs,
            },
        }

    def run(self, max_workers: Optional[int] = None) -> Dict[str, Any]:
        """
        Run all queued jobs with optimal scheduling.

        Args:
            max_workers: Maximum number of concurrent jobs. If None, uses cluster CPU limit.

        Returns:
            dict: Execution statistics and results.
        """
        if self._running:
            raise RuntimeError("Cluster is already running")

        self._running = True
        self.start_time = time.time()

        try:
            return self._execute_jobs(max_workers)
        finally:
            self._running = False
            self.end_time = time.time()

    def _execute_jobs(self, max_workers: Optional[int] = None) -> Dict[str, Any]:
        """Execute all jobs with resource-aware scheduling."""
        if max_workers is None:
            max_workers = self.max_cpus

        stats = self.job_queue.get_stats()
        if stats["pending"] == 0:
            if self.verbose:
                self.logger.info("No jobs to execute")
            return self.stats

        if self.verbose:
            self.logger.info(f"Starting execution of {stats['pending']} jobs")
            self.logger.info(
                f"Cluster resources: {self.max_cpus} CPUs, {format_memory(self.max_memory_mb)} memory"
            )

        # Initialize progress bar
        progress = None
        if self.progress_bar and stats["pending"] > 0:
            progress = ProgressBar(stats["pending"])

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            self._executor = executor
            futures = {}

            while True:
                # Check for completed jobs
                completed_futures = []
                for future in list(futures.keys()):
                    if future.done():
                        completed_futures.append(future)

                # Process completed jobs
                for future in completed_futures:
                    job = futures.pop(future)
                    try:
                        result = future.result()
                        self.job_queue.mark_completed(result)
                        memory_delta = -job["m"] if job["m"] is not None else None
                        self._update_resource_usage(-job["p"], memory_delta)

                        # Update progress bar
                        if progress:
                            progress.update()

                        if self.verbose:
                            status = "✓" if result.success else "✗"
                            self.logger.info(
                                f"{status} {result.job_id}: {' '.join(result.cmd[:3])}... "
                                f"({format_duration(result.runtime)}, {format_memory(result.memory_used)})"
                            )

                    except Exception as e:
                        self.logger.error(f"Error processing job result: {e}")

                # Try to start new jobs
                while len(futures) < max_workers:
                    available_cpus = self.max_cpus - self.resource_usage.cpu_slots_used
                    available_memory = (
                        self.max_memory_mb - self.resource_usage.memory_used
                    )

                    next_job = self.job_queue.get_next_job(
                        available_cpus, available_memory
                    )
                    if next_job is None:
                        break

                    # Start the job
                    future = executor.submit(self._execute_single_job, next_job)
                    futures[future] = next_job

                    self.job_queue.mark_running(next_job)
                    self._update_resource_usage(next_job["p"], next_job["m"])

                    if self.verbose:
                        self.logger.info(
                            f"→ Started {next_job['id']}: {' '.join(next_job['cmd'][:3])}..."
                        )

                # Check if we're done
                if not futures and self.job_queue.get_stats()["pending"] == 0:
                    break

                # Brief pause to avoid busy waiting
                time.sleep(0.1)

        # Finish progress bar
        if progress:
            progress.finish()

        # Final statistics
        final_stats = self.stats
        if self.verbose:
            job_stats = final_stats["jobs"]
            self.logger.info(
                f"Execution completed: {job_stats['completed']} succeeded, "
                f"{job_stats['failed']} failed, "
                f"runtime: {final_stats['cluster']['runtime']}"
            )

        return final_stats

    def _execute_single_job(self, job: Dict[str, Any]) -> JobResult:
        """Execute a single job and return results."""
        job_id = job["id"]
        cmd = job["cmd"]

        result = JobResult(
            job_id=job_id, cmd=cmd, cpu_used=job["p"], start_time=time.time()
        )

        try:
            # Prepare subprocess arguments
            subprocess_kwargs = {
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "text": True,
                "cwd": job.get("cwd"),
                "env": job.get("env"),
            }

            # Start the process
            process = subprocess.Popen(cmd, **subprocess_kwargs)

            # Start memory monitoring
            monitor_thread = self.memory_monitor.start_monitoring(job_id, process)

            # Wait for completion with optional timeout
            timeout = job.get("timeout")
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                result.stdout = stdout
                result.stderr = stderr
                result.returncode = process.returncode
                result.success = process.returncode == 0

            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                result.stdout = stdout
                result.stderr = stderr
                result.returncode = -1
                result.success = False
                result.error = f"Job timed out after {timeout} seconds"

            # Wait for monitoring thread to finish
            monitor_thread.join(timeout=1.0)

            # Get memory usage
            result.memory_used = self.memory_monitor.get_peak_memory(job_id)
            self.memory_monitor.cleanup(job_id)

        except Exception as e:
            result.success = False
            result.error = str(e)
            result.returncode = -1

        finally:
            result.end_time = time.time()
            result.runtime = result.end_time - result.start_time

        return result

    def _update_resource_usage(self, cpu_delta: int, memory_delta: Optional[float]):
        """Update resource usage tracking."""
        self.resource_usage.cpu_slots_used += cpu_delta
        if memory_delta is not None:
            self.resource_usage.memory_used += memory_delta

        if cpu_delta > 0:
            self.resource_usage.active_jobs += 1
        elif cpu_delta < 0:
            self.resource_usage.active_jobs = max(
                0, self.resource_usage.active_jobs - 1
            )

    def print_summary(self):
        """Print a summary of execution results."""
        stats = self.stats

        print("\n" + "=" * 60)
        print("MPMSUB EXECUTION SUMMARY")
        print("=" * 60)

        # Cluster info
        cluster_info = stats["cluster"]
        print(
            f"Cluster: {cluster_info['max_cpus']} CPUs, {cluster_info['max_memory']} memory"
        )
        print(f"Runtime: {cluster_info['runtime_formatted']}")

        # Job statistics
        job_stats = stats["jobs"]
        print(f"\nJobs: {job_stats['total']} total")
        print(f"  ✓ Completed: {job_stats['completed']}")
        print(f"  ✗ Failed: {job_stats['failed']}")

        if job_stats["completed"] > 0:
            # Performance statistics
            completed = self.completed_jobs
            runtimes = [job.runtime for job in completed]
            memories = [job.memory_used for job in completed]

            print("\nPerformance:")
            print(
                f"  Average runtime: {format_duration(sum(runtimes) / len(runtimes))}"
            )
            print(f"  Total CPU time: {format_duration(sum(runtimes))}")
            if memories:
                print(f"  Peak memory: {format_memory(max(memories))}")
                print(
                    f"  Average memory: {format_memory(sum(memories) / len(memories))}"
                )

        if job_stats["failed"] > 0:
            print("\nFailed jobs:")
            for job in self.failed_jobs[:5]:  # Show first 5 failures
                print(f"  ✗ {job.job_id}: {job.error or f'Exit code {job.returncode}'}")
            if len(self.failed_jobs) > 5:
                print(f"  ... and {len(self.failed_jobs) - 5} more")

        print("=" * 60)

    def profile(self, verbose: bool = True) -> List[JobResult]:
        """
        Profile jobs by running them sequentially to measure actual resource usage.

        This is useful for estimating memory requirements when you don't know them.
        Jobs are run one at a time (respecting CPU requirements) to get accurate
        memory measurements without interference.

        Args:
            verbose: Whether to print progress information.

        Returns:
            List[JobResult]: Results from profiling run with actual memory usage.
        """
        if self._running:
            raise RuntimeError("Cannot profile while cluster is running")

        stats = self.job_queue.get_stats()
        if stats["pending"] == 0:
            if verbose:
                print("No jobs to profile")
            return []

        if verbose:
            print("MPMSUB PROFILING MODE")
            print("=" * 40)
            print(f"Profiling {stats['pending']} jobs sequentially")
            print("This will measure actual memory usage for each job")
            print("Use these measurements to set 'm' values for efficient scheduling\n")

        self._running = True
        self.start_time = time.time()

        try:
            return self._profile_jobs(verbose)
        finally:
            self._running = False
            self.end_time = time.time()

    def _profile_jobs(self, verbose: bool) -> List[JobResult]:
        """Execute jobs sequentially for profiling."""
        profile_results = []

        # Get all pending jobs
        jobs_to_profile = []
        while True:
            # Get next job (ignoring memory constraints for profiling)
            next_job = None
            with self.job_queue._lock:
                for i, job in enumerate(self.job_queue.pending_jobs):
                    if job["p"] <= self.max_cpus:  # Only check CPU constraint
                        next_job = self.job_queue.pending_jobs.pop(i)
                        break

            if next_job is None:
                break

            jobs_to_profile.append(next_job)

        if verbose:
            print(f"Running {len(jobs_to_profile)} jobs for profiling...\n")

        # Initialize progress bar for profiling
        progress = None
        if self.progress_bar and len(jobs_to_profile) > 0:
            progress = ProgressBar(len(jobs_to_profile))

        # Execute jobs one by one
        for i, job in enumerate(jobs_to_profile, 1):
            if verbose:
                print(
                    f"[{i}/{len(jobs_to_profile)}] Profiling {job['id']}: {' '.join(job['cmd'][:3])}..."
                )

            # Mark as running
            self.job_queue.mark_running(job)

            # Execute the job
            result = self._execute_single_job(job)

            # Mark as completed
            self.job_queue.mark_completed(result)
            profile_results.append(result)

            # Update progress bar
            if progress:
                progress.update()

            if verbose:
                status = "✓" if result.success else "✗"
                memory_str = (
                    format_memory(result.memory_used)
                    if result.memory_used > 0
                    else "< 1M"
                )
                print(
                    f"  {status} Runtime: {format_duration(result.runtime)}, "
                    f"Memory: {memory_str}"
                )

                if not result.success and result.error:
                    print(f"    Error: {result.error}")
                print()

        # Finish progress bar
        if progress:
            progress.finish()

        if verbose:
            self._print_profile_summary(profile_results)

        return profile_results

    def _print_profile_summary(self, results: List[JobResult]):
        """Print profiling summary with memory recommendations."""
        print("\n" + "=" * 60)
        print("PROFILING SUMMARY")
        print("=" * 60)

        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        print(f"Jobs profiled: {len(results)}")
        print(f"Successful: {len(successful_results)}")
        print(f"Failed: {len(failed_results)}")

        if successful_results:
            print("\nMemory Usage Analysis:")
            print("-" * 30)

            memories = [r.memory_used for r in successful_results if r.memory_used > 0]
            if memories:
                print(f"Peak memory usage: {format_memory(max(memories))}")
                print(
                    f"Average memory usage: {format_memory(sum(memories) / len(memories))}"
                )
                print(f"Minimum memory usage: {format_memory(min(memories))}")

            print("\nRecommended Memory Settings:")
            print("-" * 30)

            for result in successful_results:
                if result.memory_used > 0:
                    # Add 20% buffer to measured memory
                    recommended = int(result.memory_used * 1.2)
                    recommended_str = format_memory(recommended)
                else:
                    recommended_str = "50M"  # Minimum for very light jobs

                print(f"{result.job_id}: 'm': '{recommended_str}'")

        print("=" * 60)


class JobList:
    """List-like interface for managing jobs."""

    def __init__(self, job_queue: JobQueue):
        self._queue = job_queue

    def append(self, job: Union[Dict[str, Any], Job]) -> str:
        """Add a job to the queue. Accepts both Job objects and dictionaries."""
        if isinstance(job, Job):
            job_dict = job.to_dict()
        else:
            job_dict = job
        return self._queue.add_job(job_dict)

    def extend(self, jobs: List[Union[Dict[str, Any], Job]]) -> List[str]:
        """Add multiple jobs to the queue. Accepts both Job objects and dictionaries."""
        return [self.append(job) for job in jobs]

    def __len__(self) -> int:
        """Get number of pending jobs."""
        return len(self._queue.pending_jobs)

    def __iter__(self):
        """Iterate over pending jobs."""
        return iter(self._queue.pending_jobs)
