# mpmsub Documentation

**Memory-aware multiprocessing subprocess execution library**

mpmsub provides a simple interface for running subprocess commands with intelligent memory-aware scheduling and resource management.

## Key Features

- **Simple API**: Easy-to-use interface for subprocess execution
- **Memory-aware scheduling**: Automatically manages memory constraints
- **Pipeline support**: Chain subprocess commands with automatic piping
- **Output redirection**: Redirect stdout/stderr to files automatically
- **Flexible API**: Multiple parameter names (p/cpu/cpus, m/memory) for convenience
- **Resource monitoring**: Tracks actual vs estimated resource usage
- **Job profiling**: Measure actual memory usage to optimize future runs
- **Progress tracking**: Optional progress bar with ETA for long-running jobs
- **Multiple interfaces**: Dictionary, object-oriented, and convenience function APIs

## Quick Example

```python
import mpmsub

# Create a cluster with 6 CPUs and 16GB memory limit
p = mpmsub.cluster(cpu=6, memory="16G")

# Add jobs using different interfaces
p.jobs.append({"cmd": ["echo", "dict job"], "p": 1, "m": "1G"})
p.jobs.append(mpmsub.Job(["echo", "object job"]).cpu(2).memory("2G"))
p.jobs.append(mpmsub.job(["echo", "convenience job"], cpu=1, memory="500M"))

# Add a pipeline that chains commands together
p.jobs.append(mpmsub.pipeline([
    ["cat", "data.txt"],
    ["grep", "pattern"],
    ["sort"]
], cpu=1, memory="200M"))

# Run all jobs with optimal scheduling
results = p.run()
```

## Installation

```bash
pip install mpmsub
```

## Why mpmsub?

Traditional multiprocessing libraries focus on CPU parallelism but ignore memory constraints. mpmsub solves this by:

- Intelligent scheduling that prevents memory exhaustion
- Pipeline support for chaining subprocess commands
- Automatic output redirection to files
- Real-time resource monitoring and tracking
- Multiple flexible interfaces (dictionary, object-oriented, convenience functions)

## Documentation

- **[Adding Jobs](guide/jobs.md)** - Learn about the job interfaces and how to use them
- **[Advanced Features](guide/advanced.md)** - Pipelines, output redirection, and flexible API usage
- **[API Reference](api/overview.md)** - Complete API documentation

## Links

- [GitHub Repository](https://github.com/nextgenusfs/mpmsub)
- [PyPI Package](https://pypi.org/project/mpmsub/)
- [License](https://github.com/nextgenusfs/mpmsub/blob/main/LICENSE)
