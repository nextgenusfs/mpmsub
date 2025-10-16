# mpmsub - Memory-Aware Multiprocessing Subprocess

A Python library for running subprocess commands with intelligent memory-aware scheduling and resource management.

## Features

- Memory-aware scheduling with automatic resource management
- Pipeline support for chaining commands
- Multiple job interfaces (dictionary, object-oriented, convenience functions)
- Output redirection and progress tracking
- Job profiling for memory optimization
- Flexible API with multiple parameter names

## Installation

```bash
pip install mpmsub
```

## Quick Start

```python
import mpmsub

# Create cluster and add jobs
p = mpmsub.cluster(cpu=4, memory="8G")

# Dictionary interface
p.jobs.append({"cmd": ["echo", "hello"], "p": 1, "m": "1G"})

# Object interface
p.jobs.append(mpmsub.Job(["python", "script.py"]).cpu(2).memory("2G"))

# Pipeline interface
p.jobs.append(mpmsub.pipeline([
    ["cat", "data.txt"],
    ["grep", "pattern"]
], cpu=1, memory="500M"))

# Run and analyze
results = p.run()
print(f"Completed: {results['jobs']['completed']}/{results['jobs']['total']}")
```

## Performance

Run benchmarks to see performance benefits:

```bash
python examples/benchmark_demo.py
python benchmarks/run_all_benchmarks.py
```

Benefits include 1.2-2x speedup in memory-constrained scenarios and better system stability. See [`benchmarks/README.md`](benchmarks/README.md) for details.

## Documentation

**Complete documentation:** [https://nextgenusfs.github.io/mpmsub/](https://nextgenusfs.github.io/mpmsub/)

Includes tutorials, API reference, examples, and performance tips.

## Key Features

### Multiple Job Interfaces

```python
# Dictionary interface
p.jobs.append({"cmd": ["echo", "hello"], "p": 1, "m": "1G"})

# Object interface with builder pattern
job = mpmsub.Job(["python", "script.py"]) \
    .cpu(2).memory("4G") \
    .stdout_to("output.txt")

# Pipeline interface
pipeline = mpmsub.pipeline([
    ["cat", "data.txt"],
    ["grep", "pattern"],
    ["sort"]
], cpu=1, memory="500M")
```

### Job Profiling

```python
# Measure actual memory usage
profile_results = p.profile()

# Use recommendations for optimized scheduling
p.jobs.append({"cmd": ["my_command"], "p": 1, "m": "150M"})
```

### Memory Formats

- `"1G"` - Gigabytes
- `"1024M"` - Megabytes
- `1024` - MB (integer)

## Examples

See the `examples/` directory for usage demonstrations and the documentation for comprehensive tutorials.

## Development

```bash
# Clone and install in development mode
git clone https://github.com/nextgenusfs/mpmsub.git
cd mpmsub
pip install -e .[dev]

# Install pre-commit hooks (optional)
pre-commit install
```

### CI/CD

The project uses GitHub Actions for:
- **Tests**: Run on Python 3.8-3.12, Ubuntu/macOS
- **Code Quality**: Linting, formatting, type checking
- **Publishing**: Manual workflow for TestPyPI/PyPI, automatic PyPI on releases
- **Documentation**: Auto-deploy to GitHub Pages

## Requirements

- Python 3.8+
- psutil >= 5.8.0

## License

MIT License
