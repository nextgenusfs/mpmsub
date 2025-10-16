# Adding Jobs

mpmsub provides multiple interfaces for creating and managing jobs. Choose the approach that best fits your needs.

## Job Interfaces

| Interface | Best For | Example |
|-----------|----------|---------|
| **Dictionary** | Simple jobs, existing code | `{"cmd": [...], "p": 1}` |
| **Job Object** | Complex jobs, IDE support | `Job([...]).cpu(1).memory("1G")` |
| **Convenience Function** | Quick creation | `job([...], p=1, m="1G")` |
| **Pipeline** | Chained commands | `pipeline([["cat"], ["grep"]], ...)` |

## Dictionary Interface

```python
import mpmsub

p = mpmsub.cluster(p=4, m="8G")

# Simple job
p.jobs.append({"cmd": ["echo", "hello"]})

# Job with resources and output redirection
p.jobs.append({
    "cmd": ["python", "analysis.py"],
    "p": 2, "m": "1G", "timeout": 300,
    "cwd": "/data/analysis",
    "env": {"PYTHONPATH": "/custom/libs"},
    "stdout": "output.txt", "stderr": "errors.txt"
})
```

## Job Object Interface

Object-oriented approach with builder pattern:

```python
import mpmsub

# Builder pattern (fluent interface)
job = mpmsub.Job(["python", "script.py"]) \
    .cpu(2).memory("1G").with_timeout(300) \
    .stdout_to("output.txt").stderr_to("errors.txt")

# Step-by-step building
job = mpmsub.Job(["python", "analysis.py"])
job.cpu(1).memory("2G").working_dir("/data/analysis")
job.environment({"PYTHONPATH": "/custom/libs"})

p = mpmsub.cluster(p=4, m="8G")
p.jobs.extend([job1, job2])
```

## Convenience Function

Quick job creation with a functional approach:

```python
import mpmsub

# Quick job creation
job1 = mpmsub.job(["echo", "hello"], cpu=1, memory="100M")
job2 = mpmsub.job(["python", "script.py"], cpus=2, memory="1G",
                  timeout=300, stdout="output.txt")

p = mpmsub.cluster(p=4, m="8G")
p.jobs.extend([job1, job2])
```

## Pipeline Interface

Chain subprocess commands together with automatic piping:

```python
import mpmsub

p = mpmsub.cluster(cpu=4, memory="8G")

# Pipeline convenience function
pipeline_job = mpmsub.pipeline([
    ["cat", "data.txt"],
    ["grep", "pattern"],
    ["sort"]
], cpu=1, memory="500M", stdout="results.txt")

# Builder pattern with pipe_to()
job = mpmsub.Job(["cat", "input.txt"]) \
    .pipe_to(["grep", "important"]) \
    .pipe_to(["sort"]) \
    .cpu(1).memory("200M") \
    .stdout_to("results.txt")

p.jobs.extend([pipeline_job, job])
```

## Job Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cmd` | `List[str]` or `Pipeline` | Required | Command and arguments to execute |
| `p`/`cpu`/`cpus` | `int` or `str` | `1` | Number of CPU cores |
| `m`/`memory` | `str` or `int` | `None` | Memory limit (e.g., "1G", "512M", 1024) |
| `id` | `str` | Auto-generated | Custom job identifier |
| `cwd` | `str` | `None` | Working directory |
| `env` | `Dict[str, str]` | `None` | Environment variables |
| `timeout` | `float` | `None` | Timeout in seconds |
| `stdout` | `str` | `None` | File path for stdout redirection |
| `stderr` | `str` | `None` | File path for stderr redirection |

### Memory Formats

```python
# String formats
"1G"     # 1 gigabyte
"512M"   # 512 megabytes
"2048K"  # 2048 kilobytes

# Integer (always MB)
1024     # 1024 megabytes
```

### Output Redirection

```python
# Dictionary interface
{"cmd": ["python", "script.py"], "stdout": "output.txt", "stderr": "errors.txt"}

# Job object interface
mpmsub.Job(["python", "script.py"]).stdout_to("output.txt").stderr_to("errors.txt")
```

## Mixed Interface Usage

You can freely mix all interfaces:

```python
import mpmsub

p = mpmsub.cluster(cpu=4, memory="8G")

jobs = [
    {"cmd": ["echo", "dict job"], "cpu": 1, "memory": "100M"},
    mpmsub.Job(["echo", "object job"]).cpu(1).memory("150M"),
    mpmsub.job(["echo", "convenience job"], cpus=1, memory="200M"),
    mpmsub.pipeline([["cat", "data.txt"], ["grep", "pattern"]], cpu=1)
]

p.jobs.extend(jobs)
results = p.run()
```

## Defaults and Validation

**Default Values:**
- `p`: 1 (one CPU core)
- `m`: None (unlimited memory)
- `id`: Auto-generated
- Other parameters inherit from parent process

Jobs are validated when added - invalid commands, CPU counts, or memory formats will raise `ValueError`.

## Best Practices

- **Simple jobs**: Use dictionary or convenience function
- **Complex jobs**: Use Job objects with builder pattern
- **Batch creation**: Use list comprehensions
- **Resource specification**: Be specific about CPU and memory needs
- **Profiling**: Use `p.profile()` to optimize resource allocation
- **Error prevention**: Set reasonable timeouts and validate inputs
- **Job tracking**: Use custom IDs for important jobs

## Examples

```python
# Simple batch processing
jobs = [mpmsub.job(["process", f"file_{i}.txt"], p=1, m="500M")
        for i in range(100)]

# Complex analysis with tracking
job = mpmsub.Job(["python", "analysis.py"]) \
    .cpu(4).memory("8G") \
    .working_dir("/data") \
    .with_timeout(3600) \
    .with_id("main_analysis")

# Manual job dependencies
p1 = mpmsub.cluster(p=4, m="8G")
p1.jobs.extend(preprocessing_jobs)
results1 = p1.run()

if results1['jobs']['failed'] == 0:
    p2 = mpmsub.cluster(p=4, m="8G")
    p2.jobs.extend(analysis_jobs)
    results2 = p2.run()
```
