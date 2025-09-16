# Adding Jobs

mpmsub provides multiple flexible interfaces for creating and managing jobs, including support for subprocess pipelines and output redirection. Choose the approach that best fits your coding style and requirements.

## Job Interfaces Overview

| Interface | Best For | Syntax Style |
|-----------|----------|--------------|
| **Dictionary** | Simple jobs, existing code | `{"cmd": [...], "p": 1}` |
| **Job Object** | Complex jobs, IDE support | `Job([...]).cpu(1).memory("1G")` |
| **Convenience Function** | Quick creation | `job([...], p=1, m="1G")` |
| **Pipeline** | Chained commands | `pipeline([["cat"], ["grep"]], ...)` |

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

# Job with environment and output redirection
p.jobs.append({
    "cmd": ["python", "analysis.py"],
    "p": 1,
    "m": "2G",
    "cwd": "/data/analysis",
    "env": {"PYTHONPATH": "/custom/libs"},
    "id": "analysis_job",
    "stdout": "analysis_output.txt",
    "stderr": "analysis_errors.txt"
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

# Builder pattern (fluent interface) with output redirection
job = mpmsub.Job(["python", "script.py"]) \
    .cpu(2) \
    .memory("1G") \
    .with_timeout(300) \
    .with_id("analysis") \
    .stdout_to("output.txt") \
    .stderr_to("errors.txt")

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

# Quick job creation (flexible API)
job1 = mpmsub.job(["echo", "hello"], cpu=1, memory="100M")
job2 = mpmsub.job(["python", "script.py"], cpus=2, memory="1G", timeout=300, stdout="output.txt")

p.jobs.extend([job1, job2])

# With additional parameters and output redirection
job3 = mpmsub.job(
    ["python", "analysis.py"],
    cpu=1, memory="2G",
    cwd="/data/analysis",
    env={"PYTHONPATH": "/custom/libs"},
    id="analysis_job",
    stdout="analysis_output.txt",
    stderr="analysis_errors.txt"
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

## Pipeline Interface

Chain subprocess commands together with automatic piping, similar to shell pipes (`cmd1 | cmd2 | cmd3`):

```python
import mpmsub

p = mpmsub.cluster(cpu=4, memory="8G")

# Method 1: Pipeline convenience function
pipeline_job = mpmsub.pipeline([
    ["cat", "data.txt"],
    ["grep", "pattern"],
    ["sort"],
    ["uniq"]
], cpu=1, memory="500M", id="data_processing", stdout="results.txt")

p.jobs.append(pipeline_job)

# Method 2: Job with Pipeline object
pipeline_obj = mpmsub.Pipeline([
    ["echo", "hello world"],
    ["tr", "a-z", "A-Z"],
    ["sed", "s/HELLO/GREETINGS/g"]
])
job = mpmsub.Job(cmd=pipeline_obj).cpu(1).memory("100M").stdout_to("output.txt")

p.jobs.append(job)

# Method 3: Builder pattern with pipe_to()
job = mpmsub.Job(["cat", "input.txt"]) \
    .pipe_to(["grep", "important"]) \
    .pipe_to(["sort"]) \
    .pipe_to(["head", "-10"]) \
    .cpu(1).memory("200M") \
    .stdout_to("top_results.txt")

p.jobs.append(job)
```

**Pipeline Features:**
- ✅ Automatic subprocess piping (equivalent to shell `|`)
- ✅ Error handling for individual commands in the pipeline
- ✅ Memory monitoring across the entire pipeline
- ✅ Output redirection for the final command
- ✅ Multiple creation interfaces for flexibility
- ✅ Full integration with resource scheduling

**Pros:**
- ✅ Natural shell-like command chaining
- ✅ Automatic process management
- ✅ Resource monitoring for entire pipeline
- ✅ Multiple creation methods

**Cons:**
- ❌ More complex than single commands
- ❌ Debugging can be challenging

## Job Parameters

All interfaces support the same parameters:

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `cmd` | `List[str]` or `Pipeline` | Command and arguments to execute, or Pipeline object |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `p`/`cpu`/`cpus` | `int` or `str` | `1` | Number of CPU cores |
| `m`/`memory` | `str` or `int` | `None` | Memory limit |
| `id` | `str` | Auto-generated | Custom job identifier |
| `cwd` | `str` | `None` | Working directory |
| `env` | `Dict[str, str]` | `None` | Environment variables |
| `timeout` | `float` | `None` | Timeout in seconds |
| `stdout` | `str` | `None` | File path for stdout redirection |
| `stderr` | `str` | `None` | File path for stderr redirection |

### Parameter Details

#### CPU Cores (`p`/`cpu`/`cpus`)
```python
# Multiple parameter names supported (flexible API)
p=1         # Traditional
cpu=1       # Alternative
cpus=4      # Alternative

# String (converted to int)
cpu="2"     # 2 cores
```

#### Memory (`m`/`memory`)
```python
# Multiple parameter names supported (flexible API)
m="1G"         # Traditional
memory="1G"    # Alternative

# String formats
memory="1G"     # 1 gigabyte
memory="512M"   # 512 megabytes
memory="2048K"  # 2048 kilobytes

# Integer (megabytes)
memory=1024     # 1024 MB
```

#### Environment Variables (`env`)
```python
env={
    "PYTHONPATH": "/custom/libs",
    "DATA_PATH": "/data/input",
    "TMPDIR": "/fast/tmp"
}
```

#### Output Redirection (`stdout`/`stderr`)
```python
# Redirect stdout and stderr to files
stdout="output.txt"      # Capture stdout
stderr="errors.txt"      # Capture stderr

# Both can be used together
job = mpmsub.job(
    ["python", "script.py"],
    cpu=1, memory="1G",
    stdout="results.txt",
    stderr="errors.txt"
)

# Using Job object builder pattern
job = mpmsub.Job(["python", "script.py"]) \
    .cpu(1).memory("1G") \
    .stdout_to("results.txt") \
    .stderr_to("errors.txt")
```

## Mixed Interface Usage

You can freely mix all interfaces including pipelines:

```python
import mpmsub

p = mpmsub.cluster(cpu=4, memory="8G")

# Mix different approaches
jobs = [
    # Dictionary with output redirection
    {"cmd": ["echo", "dict job"], "cpu": 1, "memory": "100M", "stdout": "dict_output.txt"},

    # Job object with builder pattern
    mpmsub.Job(["echo", "object job"]).cpu(1).memory("150M").stderr_to("object_errors.txt"),

    # Convenience function (flexible API)
    mpmsub.job(["echo", "convenience job"], cpus=1, memory="200M"),

    # Pipeline
    mpmsub.pipeline([
        ["cat", "data.txt"],
        ["grep", "pattern"],
        ["sort"]
    ], cpu=1, memory="300M", stdout="pipeline_results.txt"),
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
