# mpmsub Documentation

**Memory-aware multiprocessing subprocess execution library**

Welcome to the mpmsub documentation! This library provides a simple, intuitive interface for running subprocess commands with intelligent memory-aware scheduling and resource management.

## ✨ Key Features

- **🚀 Simple API**: Easy-to-use interface for subprocess execution
- **🧠 Memory-aware scheduling**: Automatically manages memory constraints  
- **📊 Resource monitoring**: Tracks actual vs estimated resource usage
- **🔍 Job profiling**: Measure actual memory usage to optimize future runs
- **📈 Progress tracking**: Optional progress bar with ETA for long-running jobs
- **⚙️ Flexible defaults**: Jobs default to 1 CPU and unlimited memory if not specified
- **⚡ Parallel execution**: Optimizes job scheduling based on available resources
- **📋 Comprehensive reporting**: Detailed statistics and performance metrics
- **🎯 Multiple interfaces**: Dictionary, object-oriented, and convenience function APIs

## 🚀 Quick Example

```python
import mpmsub

# Create a cluster with 6 CPUs and 16GB memory limit
p = mpmsub.cluster(p=6, m="16G")

# Add jobs using different interfaces
p.jobs.append({"cmd": ["echo", "dict job"], "p": 1, "m": "1G"})
p.jobs.append(mpmsub.Job(["echo", "object job"]).cpu(2).memory("2G"))
p.jobs.append(mpmsub.job(["echo", "convenience job"], p=1, m="500M"))

# Run all jobs with optimal scheduling
results = p.run()

# Analyze results
for job in p.completed_jobs:
    print(f"Job: {job.cmd}")
    print(f"Runtime: {job.runtime:.2f}s")
    print(f"Memory used: {job.memory_used:.1f}MB")
```

## 📦 Installation

```bash
pip install mpmsub
```

## 🎯 Why mpmsub?

Traditional multiprocessing libraries focus on CPU parallelism but ignore memory constraints. mpmsub solves this by:

- **Intelligent scheduling**: Prevents memory exhaustion by considering both CPU and memory requirements
- **Real-time monitoring**: Tracks actual resource usage to improve future predictions  
- **Flexible interfaces**: Choose between dictionary, object-oriented, or convenience function APIs
- **Production ready**: Comprehensive error handling, logging, and progress tracking

## 📚 Documentation Sections

### User Guide
- **[Adding Jobs](guide/jobs.md)** - Learn about the three job interfaces and how to use them effectively

### API Reference  
- **[API Overview](api/overview.md)** - Complete API documentation with examples and type hints

## 🔗 Links

- **[GitHub Repository](https://github.com/nextgenusfs/mpmsub)** - Source code and issues
- **[PyPI Package](https://pypi.org/project/mpmsub/)** - Package installation
- **[License](https://github.com/nextgenusfs/mpmsub/blob/main/LICENSE)** - MIT License

## 🤝 Contributing

We welcome contributions! Please see our GitHub repository for:
- Issue reporting
- Feature requests  
- Pull requests
- Development setup

---

**Get started with the [User Guide](guide/jobs.md) or explore the [API Reference](api/overview.md)!**
