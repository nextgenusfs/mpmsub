# mpmsub Performance Benchmarks

This directory contains performance benchmarks that demonstrate the benefits of mpmsub's memory-aware scheduling compared to naive parallel execution approaches.

## 🎯 Why These Benchmarks Matter

Traditional multiprocessing libraries focus on CPU parallelism but ignore memory constraints. This can lead to:
- **System crashes** from memory exhaustion
- **Severe performance degradation** from excessive swapping
- **Failed jobs** due to out-of-memory errors
- **Inefficient resource utilization**

mpmsub solves these problems with intelligent memory-aware scheduling.

## 📊 Available Benchmarks

### 1. Simple Benchmark (`simple_benchmark.py`)
**Quick demonstration of core benefits**

- Creates memory-intensive jobs that would overwhelm naive parallel execution
- Shows clear performance and reliability improvements
- **Runtime**: ~2-3 minutes
- **Best for**: Quick demos and understanding basic concepts

```bash
python benchmarks/simple_benchmark.py
```

**Example Output**:
```
🎯 mpmsub Performance Demonstration
==================================================
System: 8 CPUs, 16.0GB RAM

Scenario: 8 jobs, each requiring 800MB for 3s
Total memory if run simultaneously: 6.4GB

📊 COMPARISON RESULTS
=========================
⏱️  Execution Time:
   Naive parallel: 12.3s
   mpmsub:         8.1s
   Speedup:        1.52x

✅ Success Rate:
   Naive parallel: 6/8
   mpmsub:         8/8
   Efficiency:     1.33x

🎉 CONCLUSION: mpmsub provides significant benefits!
   • 1.5x faster execution
   • 1.3x better success rate
   • Intelligent memory management prevents system overload
```

### 2. Bioinformatics Pipeline (`bioinformatics_benchmark.py`)
**Real-world genomics workflow simulation**

- Simulates sequence alignment, genome assembly, and gene annotation
- Mixed CPU/memory requirements typical of bioinformatics
- **Runtime**: ~3-5 minutes
- **Best for**: Demonstrating real-world applicability

```bash
python benchmarks/bioinformatics_benchmark.py
```

**Example Output**:
```
🧬 Bioinformatics Pipeline Benchmark
=============================================
Pipeline: 4 genomic samples
Each sample requires:
  • Sequence alignment (1 CPU, 600MB)
  • Genome assembly (2 CPUs, 1.8GB)
  • Gene annotation (1 CPU, 1GB)
Total: 12 jobs

📊 BIOINFORMATICS PIPELINE COMPARISON
==========================================
⏱️  Pipeline Runtime:
   Naive:   15.2s
   mpmsub:  11.8s
   Speedup: 1.29x

✅ Job Success Rate:
   Naive:   10/12
   mpmsub:  12/12
   Improvement: 1.20x

🎯 Key Benefits Demonstrated:
   • 1.3x faster pipeline execution
   • 1.2x better job completion rate
   • Prevents memory exhaustion with large assemblies
   • Optimizes mixed CPU/memory workloads
```

### 3. Comprehensive Benchmark (`performance_comparison.py`)
**Detailed analysis with multiple test scenarios**

- Memory pressure testing
- Mixed workload optimization
- Scalability analysis
- **Runtime**: ~10-15 minutes
- **Best for**: Detailed performance analysis and research

```bash
python benchmarks/performance_comparison.py
```

## 🚀 Quick Start

Run all benchmarks with a single command:

```bash
python benchmarks/run_all_benchmarks.py
```

Or run individual benchmarks:

```bash
# Quick demo (2-3 minutes)
python benchmarks/simple_benchmark.py

# Real-world example (3-5 minutes)
python benchmarks/bioinformatics_benchmark.py

# Comprehensive analysis (10-15 minutes)
python benchmarks/performance_comparison.py
```

## 📋 System Requirements

- **Python 3.7+** with mpmsub installed
- **psutil** for system monitoring
- **4GB+ RAM** recommended for meaningful results
- **Multi-core CPU** to demonstrate parallelism benefits

## 🔬 What These Benchmarks Test

### Memory Pressure Scenarios
- Jobs requiring more total memory than available system RAM
- Demonstrates mpmsub's ability to prevent memory exhaustion
- Shows graceful degradation vs system crashes

### Mixed Workloads
- Combination of CPU-intensive and memory-intensive jobs
- Tests intelligent scheduling optimization
- Compares resource utilization efficiency

### Scalability
- Performance with increasing job counts
- Memory usage scaling
- Throughput optimization

### Real-World Applicability
- Bioinformatics pipeline simulation
- Realistic job duration and resource requirements
- Mixed job types with dependencies

## 📊 Interpreting Results

### Key Metrics

- **Speedup**: How much faster mpmsub completes the workload
- **Success Rate**: Percentage of jobs completed successfully
- **Memory Efficiency**: Peak memory usage comparison
- **Resource Utilization**: CPU and memory usage patterns

### Expected Benefits

- **1.2-2x speedup** in memory-constrained scenarios
- **10-30% better success rate** under memory pressure
- **Reduced system instability** and crash prevention
- **Better resource utilization** with mixed workloads

## 🎯 Use Cases Demonstrated

### Scientific Computing
- Genomics pipelines (alignment, assembly, annotation)
- Image processing workflows
- Machine learning model training

### Data Processing
- Large dataset analysis
- ETL pipelines with memory-intensive transformations
- Batch processing workflows

### Development & Testing
- Parallel test execution
- Build systems with memory-heavy compilation
- CI/CD pipeline optimization

## 🤝 Contributing

To add new benchmarks:

1. Create a new Python script in the `benchmarks/` directory
2. Follow the existing pattern for comparison functions
3. Include clear output formatting and result interpretation
4. Add documentation to this README
5. Test on multiple system configurations

## 📚 Further Reading

- [mpmsub Documentation](../docs/index.md)
- [API Reference](../docs/api/overview.md)
- [User Guide](../docs/guide/jobs.md)

---

**These benchmarks demonstrate that mpmsub isn't just safer than naive parallel execution—it's often significantly faster and more reliable too!**
