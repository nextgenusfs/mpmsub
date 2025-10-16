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

::: mpmsub.parse_memory_string
::: mpmsub.parse_cpu_string
::: mpmsub.format_memory

## Quick Reference

### Creating Clusters

```python
import mpmsub

# Auto-detect resources
p = mpmsub.cluster()

# Specify resources
p = mpmsub.cluster(cpu=4, memory="8G")    # Alternative syntax
p = mpmsub.cluster(p=4, m="8G")           # Traditional syntax
```

### Creating Jobs

```python
# Dictionary interface
job = {"cmd": ["echo", "hello"], "p": 1, "m": "100M"}

# Object interface
job = mpmsub.Job(["echo", "hello"]).cpu(1).memory("100M")

# Convenience function
job = mpmsub.job(["echo", "hello"], cpu=1, memory="100M")
```

### Creating Pipelines

```python
# Pipeline convenience function
pipeline_job = mpmsub.pipeline([
    ["cat", "data.txt"],
    ["grep", "pattern"]
], cpu=1, memory="500M")

# Builder pattern
job = mpmsub.Job(["cat", "input.txt"]) \
    .pipe_to(["grep", "important"]) \
    .cpu(1).memory("200M")
```

### Job Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `cmd` | `List[str]` or `Pipeline` | Command to execute (required) |
| `p`/`cpu`/`cpus` | `int` or `str` | CPU cores needed |
| `m`/`memory` | `str` or `int` | Memory requirement |
| `id` | `str` | Custom job identifier |
| `cwd` | `str` | Working directory |
| `env` | `Dict[str, str]` | Environment variables |
| `timeout` | `float` | Timeout in seconds |
| `stdout` | `str` | File path for stdout redirection |
| `stderr` | `str` | File path for stderr redirection |

### Memory Formats

- `"1G"` - 1 gigabyte
- `"512M"` - 512 megabytes
- `"2048K"` - 2048 kilobytes
- `1024` - 1024 megabytes (integer)

### Results

```python
results = p.run()
# Returns: {"runtime": 45.2, "jobs": {"total": 10, "completed": 8, "failed": 2}, ...}

# Access completed/failed jobs
for job in p.completed_jobs:
    print(f"{job.id}: {job.runtime:.2f}s, {job.memory_used:.1f}MB")

for job in p.failed_jobs:
    print(f"Failed {job.id}: {job.error}")
```

## Error Handling

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
```

## Best Practices

- Specify realistic resource limits
- Use profiling (`p.profile()`) to optimize memory allocation
- Always check results for failed jobs
- Set appropriate timeouts for long-running tasks
- Use output redirection to capture results
