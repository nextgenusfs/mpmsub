# API Reference

Complete API documentation for mpmsub.

## Core Functions

### cluster()

::: mpmsub.cluster

### job()

::: mpmsub.job

### pipeline()

::: mpmsub.pipeline

## Core Classes

### Cluster

::: mpmsub.Cluster

### Job

::: mpmsub.Job

### Pipeline

::: mpmsub.Pipeline

## Utility Functions

### Memory Parsing

::: mpmsub.parse_memory_string

### CPU Parsing

::: mpmsub.parse_cpu_string

### Memory Formatting

::: mpmsub.format_memory

## Quick Reference

### Creating Clusters

```python
import mpmsub

# Auto-detect resources
p = mpmsub.cluster()

# Specify resources (flexible API)
p = mpmsub.cluster(p=4, m="8G")           # Traditional
p = mpmsub.cluster(cpu=4, memory="8G")    # Alternative
p = mpmsub.cluster(cpus=4, memory="8G")   # Alternative

# Control output
p = mpmsub.cluster(p=4, m="8G", verbose=False, progress_bar=False)
```

### Creating Jobs

```python
# Dictionary interface with output redirection
job = {"cmd": ["echo", "hello"], "p": 1, "m": "100M", "stdout": "output.txt"}

# Object interface with builder pattern
job = mpmsub.Job(["echo", "hello"]).cpu(1).memory("100M").stdout_to("output.txt")

# Convenience function (flexible API)
job = mpmsub.job(["echo", "hello"], cpu=1, memory="100M", stdout="output.txt")
```

### Creating Pipelines

```python
# Pipeline convenience function
pipeline_job = mpmsub.pipeline([
    ["cat", "data.txt"],
    ["grep", "pattern"],
    ["sort"]
], cpu=1, memory="500M", stdout="results.txt")

# Pipeline object with Job
pipeline_obj = mpmsub.Pipeline([
    ["echo", "hello world"],
    ["tr", "a-z", "A-Z"]
])
job = mpmsub.Job(cmd=pipeline_obj).cpu(1).stdout_to("output.txt")

# Builder pattern with pipe_to()
job = mpmsub.Job(["cat", "input.txt"]) \
    .pipe_to(["grep", "important"]) \
    .pipe_to(["sort"]) \
    .cpu(1).memory("200M") \
    .stdout_to("results.txt")
```

### Job Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `cmd` | `List[str]` or `Pipeline` | Command to execute (required) | `["python", "script.py"]` |
| `p`/`cpu`/`cpus` | `int` or `str` | CPU cores needed | `2`, `"2"` |
| `m`/`memory` | `str` or `int` | Memory requirement | `"1G"`, `1024` |
| `id` | `str` | Custom job identifier | `"analysis_job"` |
| `cwd` | `str` | Working directory | `"/path/to/workdir"` |
| `env` | `Dict[str, str]` | Environment variables | `{"PATH": "/custom/bin"}` |
| `timeout` | `float` | Timeout in seconds | `300.0` |
| `stdout` | `str` | File path for stdout redirection | `"output.txt"` |
| `stderr` | `str` | File path for stderr redirection | `"errors.txt"` |

### Memory Formats

```python
# String formats
"1G"     # 1 gigabyte
"512M"   # 512 megabytes
"2048K"  # 2048 kilobytes

# Integer (always MB)
1024     # 1024 megabytes
```

### Execution Results

```python
results = p.run()

# Results structure
{
    "runtime": 45.2,           # Total execution time
    "jobs": {
        "total": 10,           # Total jobs
        "completed": 8,        # Successfully completed
        "failed": 2            # Failed jobs
    },
    "resources": {
        "cpu_efficiency": 0.85, # CPU utilization
        "memory_peak": 6144     # Peak memory usage (MB)
    }
}
```

### Job Result Objects

```python
# Completed jobs
for job in p.completed_jobs:
    job.id              # Job identifier
    job.cmd             # Command executed
    job.runtime         # Execution time (seconds)
    job.memory_used     # Peak memory usage (MB)
    job.memory_limit    # Memory limit (MB or None)
    job.cpu_count       # CPU cores used
    job.success         # True for successful jobs
    job.exit_code       # Process exit code
    job.stdout          # Standard output (if captured)
    job.stderr          # Standard error (if captured)

# Failed jobs
for job in p.failed_jobs:
    job.error           # Error message
    job.exit_code       # Non-zero exit code
    # ... other attributes same as completed jobs
```

## Type Hints

mpmsub includes comprehensive type hints for better IDE support:

```python
from typing import List, Dict, Any, Optional, Union
import mpmsub

# Function signatures
def cluster(
    p: Optional[Union[int, str]] = None,
    m: Optional[Union[str, int]] = None,
    verbose: bool = True,
    progress_bar: bool = True
) -> mpmsub.Cluster: ...

def job(
    cmd: List[str],
    p: Optional[Union[int, str]] = None,
    m: Optional[Union[str, int]] = None,
    **kwargs: Any
) -> mpmsub.Job: ...
```

## Error Handling

Common exceptions and how to handle them:

```python
import mpmsub

try:
    p = mpmsub.cluster(p=4, m="8G")
    p.jobs.append({"cmd": ["invalid_command"]})
    results = p.run()
except ValueError as e:
    print(f"Invalid parameter: {e}")
except RuntimeError as e:
    print(f"Execution error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### Resource Specification

```python
# Good: Specify realistic limits
p = mpmsub.cluster(p=4, m="8G")
job = mpmsub.job(["python", "script.py"], p=1, m="1G")

# Avoid: Over-allocating resources
job = mpmsub.job(["echo", "hello"], p=8, m="32G")  # Wasteful

# Good: Use profiling to optimize
profile_results = p.profile()
# Adjust based on actual usage
```

### Error Handling

```python
# Always check results
results = p.run()
if results['jobs']['failed'] > 0:
    for job in p.failed_jobs:
        print(f"Failed: {job.cmd}, Error: {job.error}")
```

### Memory Management

```python
# Use appropriate memory limits
small_jobs = [mpmsub.job(cmd, p=1, m="100M") for cmd in small_commands]
large_jobs = [mpmsub.job(cmd, p=1, m="4G") for cmd in large_commands]

# Profile to optimize
profile_results = p.profile()
```
