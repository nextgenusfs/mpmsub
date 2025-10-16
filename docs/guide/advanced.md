# Advanced Features

## Pipeline Support

mpmsub supports chaining subprocess commands together using pipes, similar to shell pipes (`cmd1 | cmd2 | cmd3`).

### Pipeline Creation

```python
import mpmsub

p = mpmsub.cluster(cpu=4, memory="8G")

# Method 1: Pipeline convenience function
pipeline_job = mpmsub.pipeline([
    ["cat", "dataset.txt"],
    ["grep", "pattern"],
    ["sort", "-n"],
    ["head", "-20"]
], cpu=1, memory="500M", stdout="results.txt")

# Method 2: Builder pattern with pipe_to()
log_analysis = mpmsub.Job(["cat", "/var/log/access.log"]) \
    .pipe_to(["grep", "ERROR"]) \
    .pipe_to(["sort"]) \
    .pipe_to(["uniq", "-c"]) \
    .cpu(1).memory("200M") \
    .stdout_to("error_summary.txt")

p.jobs.extend([pipeline_job, log_analysis])
p.run()
```

### Pipeline Features

- Automatic piping between commands
- Error handling for individual commands
- Memory monitoring across the entire pipeline
- Output redirection for final command
- Resource scheduling like any other job

## Output Redirection

Automatically redirect subprocess stdout and stderr to files.

```python
import mpmsub

p = mpmsub.cluster(cpu=4, memory="8G")

# Dictionary interface
p.jobs.append({
    "cmd": ["python", "analysis.py"],
    "cpu": 2, "memory": "2G",
    "stdout": "results.txt", "stderr": "errors.txt"
})

# Job object interface
job = mpmsub.Job(["python", "ml_script.py"]) \
    .cpu(4).memory("4G") \
    .stdout_to("output.txt").stderr_to("errors.txt")

# Pipeline output redirection (applies to final command)
pipeline = mpmsub.pipeline([
    ["cat", "data.csv"],
    ["python", "process.py"]
], cpu=2, memory="3G", stdout="report.txt")

p.jobs.extend([job, pipeline])
p.run()
```

## Flexible API

mpmsub supports multiple parameter names for better usability:

```python
import mpmsub

# CPU parameter names (all equivalent)
job1 = mpmsub.job(["echo", "test"], p=4)           # Traditional
job2 = mpmsub.job(["echo", "test"], cpu=4)         # Alternative
job3 = mpmsub.job(["echo", "test"], cpus=4)        # Alternative

# Memory parameter names (all equivalent)
job4 = mpmsub.job(["echo", "test"], m="1G")        # Traditional
job5 = mpmsub.job(["echo", "test"], memory="1G")   # Alternative

# Mixed usage is supported
job6 = mpmsub.job(["echo", "test"], cpu=2, m="1G")

# Cluster creation
p = mpmsub.cluster(cpu=4, memory="8G")             # Alternative syntax
p = mpmsub.cluster(p=4, m="8G")                    # Traditional syntax
```

### Resource Information

```python
# Show system resources when creating cluster
p = mpmsub.cluster(describe=True)

# Or call describe_resources() method
p.describe_resources()
```

## Example Workflows

### Bioinformatics Pipeline

```python
import mpmsub

p = mpmsub.cluster(cpu=8, memory="32G")

# Quality control pipeline
qc_pipeline = mpmsub.pipeline([
    ["fastqc", "raw_reads.fastq"],
    ["trimmomatic", "SE", "raw_reads.fastq", "trimmed.fastq", "TRAILING:20"]
], cpu=4, memory="4G", stderr="qc_errors.txt")

# Assembly job
assembly = mpmsub.Job(["spades.py", "--single", "trimmed.fastq", "-o", "assembly"]) \
    .cpu(8).memory("16G").stdout_to("assembly.log")

p.jobs.extend([qc_pipeline, assembly])
p.run()
```

### Data Science Workflow

```python
import mpmsub

p = mpmsub.cluster(cpu=6, memory="16G")

# Preprocessing pipeline
preprocessing = mpmsub.pipeline([
    ["python", "download_data.py"],
    ["python", "clean_data.py"]
], cpu=2, memory="4G", stdout="preprocessing.log")

# Model training
models = [
    mpmsub.job(["python", "train.py", "--model", "rf"], cpu=2, memory="3G"),
    mpmsub.job(["python", "train.py", "--model", "xgb"], cpu=2, memory="3G")
]

p.jobs.append(preprocessing)
p.jobs.extend(models)
p.run()
```
