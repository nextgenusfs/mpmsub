"""
mpmsub - Memory-aware multiprocessing subprocess execution library

A simple, intuitive library for running subprocess commands with intelligent
memory-aware scheduling and resource management.

Example usage:
    import mpmsub

    # Create a cluster with 6 CPUs and 16GB memory limit
    p = mpmsub.cluster(p=6, m="16G")

    # Add jobs with different resource requirements
    p.jobs.append({"cmd": ["example", "subprocess", "cmd"], "p": 1, "m": "1G"})
    p.jobs.append({"cmd": ["another", "command"], "p": 2, "m": "2G"})

    # Run all jobs with optimal scheduling
    p.run()

    # Analyze results
    for job in p.completed_jobs:
        print(f"Job: {job['cmd']}")
        print(f"Runtime: {job['runtime']:.2f}s")
        print(f"Memory used: {job['memory_used']:.1f}MB")
"""

from typing import List, Optional, Union, Any

from .cluster import Cluster, Job, Pipeline
from .utils import parse_memory_string, parse_cpu_string, format_memory

# Version info
__version__ = "2025.01.0"
__author__ = "Jon Palmer"
__email__ = "nextgenusfs@gmail.com"


# Main API function
def cluster(p=None, m=None, verbose=True, progress_bar=True, describe=False):
    """
    Create a new compute cluster for job execution.

    Args:
        p: Number of CPUs (int) or CPU specification (str).
           If None, auto-detects available CPUs.
        m: Memory limit as string (e.g., "16G", "2048M") or int (MB).
           If None, auto-detects available memory.
        verbose: Whether to print progress information.
        progress_bar: Whether to show a progress bar during execution.
        describe: Whether to print cluster resource information.

    Returns:
        Cluster: A new cluster instance ready for job scheduling.

    Examples:
        >>> import mpmsub
        >>> p = mpmsub.cluster(p=4, m="8G")
        >>> p = mpmsub.cluster()  # Auto-detect resources
        >>> p = mpmsub.cluster(describe=True)  # Show available resources
    """
    cluster_obj = Cluster(cpus=p, memory=m, verbose=verbose, progress_bar=progress_bar)

    if describe:
        cluster_obj.describe_resources()

    return cluster_obj


def job(
    cmd: List[str],
    p: Optional[Union[int, str]] = None,
    m: Optional[Union[str, int]] = None,
    **kwargs: Any,
) -> Job:
    """
    Create a new Job object with a concise interface.

    Args:
        cmd: Command to execute as list of strings
        p: Number of CPU cores needed (default: 1)
        m: Memory requirement (e.g., "1G", "512M", default: unlimited)
        **kwargs: Additional job parameters (id, cwd, env, timeout)

    Returns:
        Job: A new job instance.

    Examples:
        >>> import mpmsub
        >>> j = mpmsub.job(["echo", "hello"], p=1, m="100M")
        >>> j = mpmsub.job(["python", "script.py"], p=2, m="1G", timeout=300)
    """
    return Job(cmd=cmd, p=p, m=m, **kwargs)


def pipeline(
    commands: List[List[str]],
    p: Optional[Union[int, str]] = None,
    m: Optional[Union[str, int]] = None,
    **kwargs: Any,
) -> Job:
    """
    Create a new Job with a pipeline of commands.

    Args:
        commands: List of commands to pipe together
        p: Number of CPU cores needed (default: 1)
        m: Memory requirement (e.g., "1G", "512M", default: unlimited)
        **kwargs: Additional job parameters (id, cwd, env, timeout)

    Returns:
        Job: A new job instance with a pipeline.

    Examples:
        >>> import mpmsub
        >>> j = mpmsub.pipeline([
        ...     ["cat", "file.txt"],
        ...     ["grep", "pattern"],
        ...     ["sort"]
        ... ], p=1, m="100M")
    """
    return Job(cmd=Pipeline(commands), p=p, m=m, **kwargs)


# Convenience exports
__all__ = [
    "cluster",
    "job",
    "pipeline",
    "Cluster",
    "Job",
    "Pipeline",
    "parse_memory_string",
    "parse_cpu_string",
    "format_memory",
    "__version__",
]
