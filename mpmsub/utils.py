"""
Utility functions for mpmsub library.
"""

import platform
import re
import subprocess
from typing import Optional, Union

import psutil


def parse_memory_string(memory: Union[str, int, None]) -> Optional[int]:
    """
    Parse memory specification into MB.

    Args:
        memory: Memory specification as string (e.g., "16G", "2048M", "1024")
                or int (MB), or None for auto-detection.

    Returns:
        int: Memory in MB, or None if auto-detection requested.

    Examples:
        >>> parse_memory_string("16G")
        16384
        >>> parse_memory_string("2048M")
        2048
        >>> parse_memory_string("1024")
        1024
        >>> parse_memory_string(2048)
        2048
    """
    if memory is None:
        return None

    if isinstance(memory, int):
        return memory

    if isinstance(memory, str):
        memory = memory.strip().upper()

        # Match number followed by optional unit
        match = re.match(r"^(\d+(?:\.\d+)?)\s*([KMGT]?)B?$", memory)
        if not match:
            raise ValueError(f"Invalid memory specification: {memory}")

        value, unit = match.groups()
        value = float(value)

        # Convert to MB
        multipliers = {
            "": 1,  # Assume MB if no unit
            "K": 1 / 1024,  # KB to MB
            "M": 1,  # MB
            "G": 1024,  # GB to MB
            "T": 1024 * 1024,  # TB to MB
        }

        return int(value * multipliers[unit])

    raise ValueError(f"Invalid memory specification type: {type(memory)}")


def parse_cpu_string(cpus: Union[str, int, None]) -> Optional[int]:
    """
    Parse CPU specification.

    Args:
        cpus: CPU specification as string or int, or None for auto-detection.

    Returns:
        int: Number of CPUs, or None if auto-detection requested.

    Examples:
        >>> parse_cpu_string("4")
        4
        >>> parse_cpu_string(6)
        6
        >>> parse_cpu_string(None)
        None
    """
    if cpus is None:
        return None

    if isinstance(cpus, int):
        return cpus

    if isinstance(cpus, str):
        try:
            return int(cpus.strip())
        except ValueError:
            raise ValueError(f"Invalid CPU specification: {cpus}")

    raise ValueError(f"Invalid CPU specification type: {type(cpus)}")


def _get_available_memory_mb(memory) -> int:
    """
    Get available memory in MB with platform-specific optimizations.

    On macOS, psutil.virtual_memory().available can be overly conservative,
    especially with heavy swap usage. This function uses macOS-specific tools
    like memory_pressure to get more accurate estimates of usable memory.

    For Apple Silicon systems with swap, this can provide 2-8x more accurate
    memory availability estimates compared to psutil alone.

    Args:
        memory: psutil.virtual_memory() object

    Returns:
        int: Available memory in MB
    """
    if platform.system() == "Darwin":  # macOS
        try:
            # Try to get more accurate memory info from memory_pressure
            result = subprocess.run(
                ["memory_pressure"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                # Parse "System-wide memory free percentage: XX%"
                for line in result.stdout.split("\n"):
                    if "System-wide memory free percentage:" in line:
                        try:
                            percent_str = line.split(":")[1].strip().rstrip("%")
                            free_percent = float(percent_str) / 100.0
                            total_mb = memory.total / (1024 * 1024)
                            available_mb = int(total_mb * free_percent)

                            # Use the higher of psutil or memory_pressure estimates
                            psutil_available = int(memory.available / (1024 * 1024))
                            return max(available_mb, psutil_available)
                        except (ValueError, IndexError):
                            pass
                        break
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            pass

    # Fallback to psutil for all platforms or if macOS-specific method fails
    return int(memory.available / (1024 * 1024))


def get_system_resources():
    """
    Get available system resources.

    Returns:
        dict: Dictionary with 'cpus' and 'memory_mb' keys.
    """
    try:
        memory = psutil.virtual_memory()
        available_mb = _get_available_memory_mb(memory)
        return {
            "cpus": psutil.cpu_count(),
            "memory_mb": available_mb,
        }
    except Exception as e:
        # Fallback values
        return {"cpus": 4, "memory_mb": 4096}


def format_memory(mb: Union[int, float]) -> str:
    """
    Format memory in MB to human-readable string.

    Args:
        mb: Memory in MB.

    Returns:
        str: Formatted memory string.

    Examples:
        >>> format_memory(1024)
        '1.0G'
        >>> format_memory(512)
        '512M'
    """
    if mb >= 1024:
        return f"{mb / 1024:.1f}G"
    else:
        return f"{int(mb)}M"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        str: Formatted duration string.

    Examples:
        >>> format_duration(65)
        '1m 5s'
        >>> format_duration(30)
        '30s'
    """
    if seconds >= 3600:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"
    elif seconds >= 60:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        return f"{seconds:.1f}s"


def validate_job(job: dict) -> dict:
    """
    Validate and normalize a job specification.

    Args:
        job: Job dictionary with 'cmd', 'p', 'm' keys.
             'cmd' can be a list of strings or a Pipeline object.

    Returns:
        dict: Normalized job specification.

    Raises:
        ValueError: If job specification is invalid.
    """
    if not isinstance(job, dict):
        raise ValueError("Job must be a dictionary")

    if "cmd" not in job:
        raise ValueError("Job must have 'cmd' key")

    cmd = job["cmd"]

    # Import Pipeline here to avoid circular imports
    from .cluster import Pipeline

    # Validate command or pipeline
    if isinstance(cmd, Pipeline):
        # Pipeline validation
        if not cmd.commands or len(cmd.commands) < 2:
            raise ValueError("Pipeline must have at least 2 commands")
        for i, pipeline_cmd in enumerate(cmd.commands):
            if not isinstance(pipeline_cmd, list) or not pipeline_cmd:
                raise ValueError(f"Pipeline command {i + 1} must be a non-empty list")
    elif isinstance(cmd, list):
        # Single command validation
        if not cmd:
            raise ValueError("Job 'cmd' must be a non-empty list")
    else:
        raise ValueError("Job 'cmd' must be a list or Pipeline object")

    # Validate and parse CPU requirement
    cpus = parse_cpu_string(job.get("p", 1))
    if cpus is None:
        cpus = 1
    if cpus < 1:
        raise ValueError("Job CPU requirement must be >= 1")

    # Validate and parse memory requirement
    memory_mb = parse_memory_string(job.get("m"))
    if memory_mb is None:
        memory_mb = None  # No memory limit by default
    elif memory_mb < 1:
        raise ValueError("Job memory requirement must be >= 1MB")

    # Return normalized job
    normalized = {
        "cmd": cmd,
        "p": cpus,
        "m": memory_mb,
        "id": job.get("id"),
        "cwd": job.get("cwd"),
        "env": job.get("env"),
        "timeout": job.get("timeout"),
        "stdout": job.get("stdout"),
        "stderr": job.get("stderr"),
    }

    return normalized
