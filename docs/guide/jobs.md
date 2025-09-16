# Adding Jobs

mpmsub provides three flexible interfaces for creating and managing jobs, allowing you to choose the approach that best fits your coding style and requirements.

## Job Interfaces Overview

| Interface | Best For | Syntax Style |
|-----------|----------|--------------|
| **Dictionary** | Simple jobs, existing code | `{"cmd": [...], "p": 1}` |
| **Job Object** | Complex jobs, IDE support | `Job([...]).cpu(1).memory("1G")` |
| **Convenience Function** | Quick creation | `job([...], p=1, m="1G")` |

## Dictionary Interface

The traditional approach using Python dictionaries:

```python
import mpmsub

p = mpmsub.cluster(p=4, m="8G")

# Simple job
p.jobs.append({"cmd": ["echo", "hello"]})

# Job with resources
p.jobs.append({
    "cmd": ["python", "script.py"],
    "p": 2,        # 2 CPU cores
    "m": "1G",     # 1GB memory
    "timeout": 300 # 5 minute timeout
})

# Job with environment
p.jobs.append({
    "cmd": ["python", "analysis.py"],
    "p": 1,
    "m": "2G",
    "cwd": "/data/analysis",
    "env": {"PYTHONPATH": "/custom/libs"},
    "id": "analysis_job"
})
```

**Pros:**
- ✅ Familiar Python syntax
- ✅ Compact for simple jobs
- ✅ Easy to serialize/deserialize

**Cons:**
- ❌ No IDE autocomplete
- ❌ No type checking
- ❌ Cryptic parameter names (`p`, `m`)

## Job Object Interface

Object-oriented approach with builder pattern:

```python
import mpmsub

p = mpmsub.cluster(p=4, m="8G")

# Simple job creation
job = mpmsub.Job(["echo", "hello"])
p.jobs.append(job)

# Builder pattern (fluent interface)
job = mpmsub.Job(["python", "script.py"]) \
    .cpu(2) \
    .memory("1G") \
    .with_timeout(300) \
    .with_id("analysis")

p.jobs.append(job)

# Step-by-step building
job = mpmsub.Job(["python", "analysis.py"])
job.cpu(1)
job.memory("2G")
job.working_dir("/data/analysis")
job.environment({"PYTHONPATH": "/custom/libs"})
job.with_id("analysis_job")

p.jobs.append(job)
```

**Pros:**
- ✅ IDE autocomplete and type hints
- ✅ Self-documenting method names
- ✅ Builder pattern for fluent construction
- ✅ Validation at creation time

**Cons:**
- ❌ More verbose for simple jobs
- ❌ Requires object-oriented thinking

## Convenience Function

Quick job creation with a functional approach:

```python
import mpmsub

p = mpmsub.cluster(p=4, m="8G")

# Quick job creation
job1 = mpmsub.job(["echo", "hello"], p=1, m="100M")
job2 = mpmsub.job(["python", "script.py"], p=2, m="1G", timeout=300)

p.jobs.extend([job1, job2])

# With additional parameters
job3 = mpmsub.job(
    ["python", "analysis.py"],
    p=1, m="2G",
    cwd="/data/analysis",
    env={"PYTHONPATH": "/custom/libs"},
    id="analysis_job"
)

p.jobs.append(job3)
```

**Pros:**
- ✅ Concise syntax
- ✅ Type hints and IDE support
- ✅ Familiar function call syntax

**Cons:**
- ❌ Less fluent than builder pattern
- ❌ All parameters in one call

## Job Parameters

All interfaces support the same parameters:

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `cmd` | `List[str]` | Command and arguments to execute |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `p` | `int` or `str` | `1` | Number of CPU cores |
| `m` | `str` or `int` | `None` | Memory limit |
| `id` | `str` | Auto-generated | Custom job identifier |
| `cwd` | `str` | `None` | Working directory |
| `env` | `Dict[str, str]` | `None` | Environment variables |
| `timeout` | `float` | `None` | Timeout in seconds |

### Parameter Details

#### CPU Cores (`p`)
```python
# Integer
p=1    # 1 core
p=4    # 4 cores

# String (converted to int)
p="2"  # 2 cores
```

#### Memory (`m`)
```python
# String formats
m="1G"     # 1 gigabyte
m="512M"   # 512 megabytes
m="2048K"  # 2048 kilobytes

# Integer (megabytes)
m=1024     # 1024 MB
```

#### Environment Variables (`env`)
```python
env={
    "PYTHONPATH": "/custom/libs",
    "DATA_PATH": "/data/input",
    "TMPDIR": "/fast/tmp"
}
```

## Mixed Interface Usage

You can freely mix all three interfaces:

```python
import mpmsub

p = mpmsub.cluster(p=4, m="8G")

# Mix different approaches
jobs = [
    # Dictionary
    {"cmd": ["echo", "dict job"], "p": 1, "m": "100M"},
    
    # Job object
    mpmsub.Job(["echo", "object job"]).cpu(1).memory("150M"),
    
    # Convenience function
    mpmsub.job(["echo", "convenience job"], p=1, m="200M"),
]

p.jobs.extend(jobs)
results = p.run()
```

## Job Defaults

When parameters are omitted, mpmsub applies sensible defaults:

```python
# These are equivalent
p.jobs.append({"cmd": ["echo", "hello"]})
p.jobs.append({"cmd": ["echo", "hello"], "p": 1, "m": None})

# Job objects also get defaults
job = mpmsub.Job(["echo", "hello"])
# Equivalent to: Job(["echo", "hello"], p=1, m=None)
```

**Default Values:**
- `p`: 1 (one CPU core)
- `m`: None (unlimited memory)
- `id`: Auto-generated (e.g., "job_0001")
- `cwd`: None (inherit from parent process)
- `env`: None (inherit from parent process)
- `timeout`: None (no timeout)

## Job Validation

mpmsub validates job parameters when they're added:

```python
# These will raise ValueError
p.jobs.append({"cmd": []})                    # Empty command
p.jobs.append({"cmd": ["echo"], "p": 0})      # Invalid CPU count
p.jobs.append({"cmd": ["echo"], "m": "XYZ"})  # Invalid memory format

# Job objects validate at creation time
try:
    job = mpmsub.Job([]).cpu(-1)  # Invalid parameters
except ValueError as e:
    print(f"Validation error: {e}")
```

## Best Practices

### Choose the Right Interface

```python
# Simple jobs: Use dictionary or convenience function
{"cmd": ["echo", "hello"]}
mpmsub.job(["echo", "hello"])

# Complex jobs: Use Job objects
mpmsub.Job(["python", "complex_analysis.py"]) \
    .cpu(4) \
    .memory("8G") \
    .working_dir("/data/analysis") \
    .environment({"PYTHONPATH": "/libs"}) \
    .with_timeout(3600) \
    .with_id("complex_analysis")

# Batch creation: Use list comprehensions
jobs = [mpmsub.job(["process", f"file_{i}.txt"], p=1, m="500M") 
        for i in range(100)]
```

### Resource Specification

```python
# Be specific about resource needs
mpmsub.job(["memory_intensive_app"], p=1, m="8G")    # High memory
mpmsub.job(["cpu_intensive_app"], p=8, m="1G")       # High CPU
mpmsub.job(["balanced_app"], p=2, m="4G")            # Balanced

# Use profiling to optimize
profile_results = p.profile()
# Adjust based on actual usage
```

### Error Prevention

```python
# Set reasonable timeouts
mpmsub.job(["long_running_task"], timeout=3600)  # 1 hour

# Validate inputs
if os.path.exists(input_file):
    job = mpmsub.job(["process", input_file])
    p.jobs.append(job)
```

## Advanced Job Management

### Job IDs and Tracking

```python
# Custom IDs for tracking
job1 = mpmsub.job(["step1.py"], id="preprocessing")
job2 = mpmsub.job(["step2.py"], id="analysis")
job3 = mpmsub.job(["step3.py"], id="postprocessing")

p.jobs.extend([job1, job2, job3])
results = p.run()

# Find specific jobs
for job in p.completed_jobs:
    if job.id == "analysis":
        print(f"Analysis completed in {job.runtime:.2f}s")
```

### Dynamic Job Creation

```python
import glob

# Create jobs based on available files
input_files = glob.glob("data/*.txt")
for file in input_files:
    job = mpmsub.Job(["process_file.py", file]) \
        .cpu(1) \
        .memory("1G") \
        .with_id(f"process_{os.path.basename(file)}")
    p.jobs.append(job)
```

### Job Dependencies (Manual)

```python
# While mpmsub doesn't have built-in dependencies,
# you can implement them manually:

# Phase 1: Preprocessing
preprocessing_jobs = [
    mpmsub.job(["preprocess", f"file_{i}.txt"], id=f"prep_{i}")
    for i in range(5)
]

p1 = mpmsub.cluster(p=4, m="8G")
p1.jobs.extend(preprocessing_jobs)
results1 = p1.run()

# Only proceed if all preprocessing succeeded
if results1['jobs']['failed'] == 0:
    # Phase 2: Analysis
    analysis_jobs = [
        mpmsub.job(["analyze", f"preprocessed_{i}.txt"], id=f"analysis_{i}")
        for i in range(5)
    ]
    
    p2 = mpmsub.cluster(p=4, m="8G")
    p2.jobs.extend(analysis_jobs)
    results2 = p2.run()
```

This comprehensive job management system gives you the flexibility to handle simple scripts to complex computational pipelines with ease.
