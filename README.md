# mpmsub - Memory-Aware Multiprocessing Subprocess

A simple, intuitive Python library for running subprocess commands with intelligent memory-aware scheduling and resource management.

## Features

- **Simple API**: Easy-to-use interface for subprocess execution
- **Memory-aware scheduling**: Automatically manages memory constraints
- **Resource monitoring**: Tracks actual vs estimated resource usage
- **Job profiling**: Measure actual memory usage to optimize future runs
- **Progress tracking**: Optional progress bar with ETA for long-running jobs
- **Flexible defaults**: Jobs default to 1 CPU and unlimited memory if not specified
- **Parallel execution**: Optimizes job scheduling based on available resources
- **Comprehensive reporting**: Detailed statistics and performance metrics

## Installation

```bash
pip install mpmsub
```

Or install from source:

```bash
git clone https://github.com/nextgenusfs/mpmsub.git
cd mpmsub
pip install -e .
```

## Quick Start

```python
import mpmsub

# Create a cluster with 6 CPUs and 16GB memory limit
p = mpmsub.cluster(p=6, m="16G")

# Add jobs with different resource requirements (dictionary style)
p.jobs.append({"cmd": ["example", "subprocess", "cmd"], "p": 1, "m": "1G"})

# Or use the Job object interface
p.jobs.append(mpmsub.Job(["another", "command"]).cpu(2).memory("2G"))

# Run all jobs with optimal scheduling
p.run()

# Analyze results
for job in p.completed_jobs:
    print(f"Job: {job.cmd}")
    print(f"Runtime: {job.runtime:.2f}s")
    print(f"Memory used: {job.memory_used:.1f}MB")
```

## Performance Benchmarks

🚀 **See mpmsub's performance benefits in action:**

```bash
# Quick performance demonstration
python examples/benchmark_demo.py

# Comprehensive benchmark suite
python benchmarks/run_all_benchmarks.py
```

The benchmarks demonstrate:
- **1.2-2x speedup** in memory-constrained scenarios
- **10-30% better success rate** under memory pressure
- **Intelligent resource optimization** for mixed workloads
- **System stability** and crash prevention

See [`benchmarks/README.md`](benchmarks/README.md) for detailed performance analysis.

## Documentation

📚 **Complete documentation is available at: [https://nextgenusfs.github.io/mpmsub/](https://nextgenusfs.github.io/mpmsub/)**

The documentation includes:
- Detailed installation guide
- Comprehensive tutorials and examples
- Complete API reference with auto-generated docs
- Performance tips and troubleshooting
- Advanced usage patterns

## API Reference

### Creating a Cluster

```python
# Auto-detect system resources
p = mpmsub.cluster()

# Specify resources explicitly
p = mpmsub.cluster(p=4, m="8G")

# Control verbosity and progress bar
p = mpmsub.cluster(p=4, m="8G", verbose=True, progress_bar=True)
p = mpmsub.cluster(p=4, m="8G", progress_bar=False)  # Disable progress bar

# Memory can be specified in various formats
p = mpmsub.cluster(p=4, m="8192M")  # MB
p = mpmsub.cluster(p=4, m="8G")     # GB
p = mpmsub.cluster(p=4, m=8192)     # MB as integer
```

### Adding Jobs

mpmsub supports two ways to specify jobs: **dictionaries** (traditional) and **Job objects** (object-oriented).

#### Dictionary Interface (Traditional)

Jobs are specified as dictionaries with the following keys:

- `cmd` (required): List of command arguments
- `p` (optional): Number of CPU cores needed (default: 1)
- `m` (optional): Memory requirement (default: unlimited)
- `id` (optional): Custom job identifier
- `cwd` (optional): Working directory
- `env` (optional): Environment variables
- `timeout` (optional): Timeout in seconds

```python
# Simple job
p.jobs.append({"cmd": ["echo", "hello"]})

# Job with resource requirements
p.jobs.append({
    "cmd": ["my_program", "input.txt"],
    "p": 2,        # 2 CPU cores
    "m": "4G",     # 4GB memory
    "timeout": 300 # 5 minute timeout
})

# Job with custom environment
p.jobs.append({
    "cmd": ["python", "script.py"],
    "p": 1,
    "m": "1G",
    "cwd": "/path/to/workdir",
    "env": {"PYTHONPATH": "/custom/path"}
})
```

#### Job Object Interface (New)

The `Job` class provides a more intuitive, type-safe interface with IDE support:

```python
import mpmsub

# Simple job creation
job = mpmsub.Job(["echo", "hello"])
p.jobs.append(job)

# Builder pattern (fluent interface)
job = mpmsub.Job(["my_program", "input.txt"]) \
    .cpu(2) \
    .memory("4G") \
    .with_timeout(300) \
    .with_id("analysis_job")
p.jobs.append(job)

# Step-by-step building
job = mpmsub.Job(["python", "script.py"])
job.cpu(1)
job.memory("1G")
job.working_dir("/path/to/workdir")
job.environment({"PYTHONPATH": "/custom/path"})
p.jobs.append(job)

# Convenience function for quick job creation
job1 = mpmsub.job(["echo", "convenience"], p=1, m="100M")
job2 = mpmsub.job(["python", "script.py"], p=2, timeout=300)

# Mix all approaches
jobs = [
    {"cmd": ["echo", "dict job"], "p": 1, "m": "100M"},
    mpmsub.Job(["echo", "object job"]).cpu(1).memory("150M"),
    mpmsub.job(["echo", "convenience job"], p=1),
]
p.jobs.extend(jobs)
```

**Benefits of Job objects:**
- ✓ Type hints and IDE autocomplete
- ✓ Self-documenting method names
- ✓ Builder pattern for fluent construction
- ✓ Validation at creation time
- ✓ Full compatibility with dictionary interface
- ✓ Convenience function for quick creation

### Running Jobs

```python
# Run with default settings
results = p.run()

# Limit concurrent jobs
results = p.run(max_workers=2)
```

### Analyzing Results

```python
# Print summary
p.print_summary()

# Access completed jobs
for job in p.completed_jobs:
    print(f"Job {job.job_id}: {job.success}")
    print(f"Runtime: {job.runtime:.2f}s")
    print(f"Memory: {job.memory_used:.1f}MB")
    print(f"Output: {job.stdout}")

# Access failed jobs
for job in p.failed_jobs:
    print(f"Failed job {job.job_id}: {job.error}")

# Get statistics
stats = p.stats
```

### Job Profiling

When you don't know the memory requirements of your jobs, use profiling to measure actual usage:

```python
import mpmsub

# Create cluster and add jobs without memory specifications
p = mpmsub.cluster(p=4, m="8G")
p.jobs.append({"cmd": ["my_command", "arg1", "arg2"]})
p.jobs.append({"cmd": ["another_command", "arg1"]})

# Profile jobs to measure actual memory usage
# This runs jobs sequentially to get accurate measurements
profile_results = p.profile()

# The profiling output will show:
# - Actual memory usage for each job
# - Recommended memory settings with 20% buffer
# - Example code with optimized memory values

# Use the recommendations for efficient scheduling:
p2 = mpmsub.cluster(p=4, m="8G")
p2.jobs.append({"cmd": ["my_command", "arg1", "arg2"], "p": 1, "m": "150M"})
p2.jobs.append({"cmd": ["another_command", "arg1"], "p": 1, "m": "75M"})
p2.run()  # Now runs with optimized memory scheduling
print(f"Total jobs: {stats['jobs']['total']}")
print(f"Completed: {stats['jobs']['completed']}")
print(f"Failed: {stats['jobs']['failed']}")
```

### Progress Bar

mpmsub includes an optional progress bar that shows job completion progress with ETA:

```python
import mpmsub

# Progress bar enabled by default
p = mpmsub.cluster(p=4, m="8G")
p.jobs.extend([
    {"cmd": ["sleep", "1"], "p": 1, "m": "100M"},
    {"cmd": ["sleep", "2"], "p": 1, "m": "100M"},
    {"cmd": ["sleep", "1"], "p": 1, "m": "100M"},
])

# Shows: [████████████████████████████████████████] 3/3 (100.0%) ETA: 0.0s
p.run()

# Disable progress bar if needed
p_quiet = mpmsub.cluster(p=4, m="8G", progress_bar=False)
p_quiet.jobs.append({"cmd": ["echo", "hello"], "p": 1})
p_quiet.run()  # No progress bar shown

# Progress bar also works with profiling
p.profile()  # Shows progress during sequential profiling
```

The progress bar:
- Uses only standard library modules (no external dependencies)
- Shows current/total jobs, percentage, and estimated time remaining
- Writes to stderr to avoid interfering with stdout
- Works with both `run()` and `profile()` methods

## Memory Format Specifications

Memory can be specified in several formats:

- `"1024"` or `1024` - MB (default unit)
- `"1024M"` - Megabytes
- `"1G"` - Gigabytes  
- `"1024K"` - Kilobytes
- `"1T"` - Terabytes

## Examples

See the `examples/` directory for more detailed examples:

- `basic_example.py` - Simple usage demonstration
- `memory_intensive.py` - Memory-constrained job scheduling
- `cpu_intensive.py` - CPU-bound job management

## Requirements

- Python 3.8+
- psutil >= 5.8.0

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
