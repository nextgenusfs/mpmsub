# Advanced Features

This guide covers the advanced features of mpmsub including pipelines, output redirection, and flexible API usage.

## Pipeline Support

mpmsub supports chaining subprocess commands together using pipes, similar to shell pipes (`cmd1 | cmd2 | cmd3`). This allows you to create complex data processing workflows with automatic resource management.

### Pipeline Creation Methods

#### Method 1: Pipeline Convenience Function

The simplest way to create pipelines:

```python
import mpmsub

p = mpmsub.cluster(cpu=4, memory="8G")

# Create a data processing pipeline
pipeline_job = mpmsub.pipeline([
    ["cat", "large_dataset.txt"],
    ["grep", "important_pattern"],
    ["sort", "-n"],
    ["uniq", "-c"],
    ["head", "-20"]
], cpu=1, memory="500M", id="data_analysis", stdout="top_patterns.txt")

p.jobs.append(pipeline_job)
p.run()
```

#### Method 2: Pipeline Object with Job

For more control over pipeline creation:

```python
import mpmsub

# Create a Pipeline object
text_processing = mpmsub.Pipeline([
    ["echo", "Hello World"],
    ["tr", "a-z", "A-Z"],
    ["sed", "s/HELLO/GREETINGS/g"],
    ["rev"]  # Reverse the string
])

# Use with Job object
job = mpmsub.Job(cmd=text_processing) \
    .cpu(1) \
    .memory("100M") \
    .with_id("text_transform") \
    .stdout_to("transformed_text.txt")

p = mpmsub.cluster(cpu=2, memory="4G")
p.jobs.append(job)
p.run()
```

#### Method 3: Builder Pattern with pipe_to()

Build pipelines step by step using the fluent interface:

```python
import mpmsub

p = mpmsub.cluster(cpu=4, memory="8G")

# Build pipeline incrementally
log_analysis = mpmsub.Job(["cat", "/var/log/access.log"]) \
    .pipe_to(["grep", "ERROR"]) \
    .pipe_to(["awk", "{print $1, $4}"]) \
    .pipe_to(["sort"]) \
    .pipe_to(["uniq", "-c"]) \
    .pipe_to(["sort", "-nr"]) \
    .pipe_to(["head", "-10"]) \
    .cpu(1) \
    .memory("200M") \
    .with_id("error_analysis") \
    .stdout_to("top_error_sources.txt")

p.jobs.append(log_analysis)
p.run()
```

### Pipeline Features

- **Automatic Piping**: Commands are connected using `subprocess.PIPE`
- **Error Handling**: Individual command failures are detected and reported
- **Memory Monitoring**: Resource usage is tracked across the entire pipeline
- **Output Redirection**: Final command output can be redirected to files
- **Resource Scheduling**: Pipelines are scheduled like any other job

### Pipeline Best Practices

1. **Memory Estimation**: Consider the memory usage of all commands in the pipeline
2. **Error Handling**: Test pipelines with small datasets first
3. **Output Management**: Use output redirection to capture results
4. **Resource Planning**: Pipelines may use more memory than individual commands

## Output Redirection

Automatically redirect subprocess stdout and stderr to files without manual file handling.

### Basic Output Redirection

```python
import mpmsub

p = mpmsub.cluster(cpu=4, memory="8G")

# Dictionary interface
p.jobs.append({
    "cmd": ["python", "data_analysis.py"],
    "cpu": 2,
    "memory": "2G",
    "stdout": "analysis_results.txt",
    "stderr": "analysis_errors.txt"
})

# Job object interface
job = mpmsub.Job(["python", "machine_learning.py"]) \
    .cpu(4) \
    .memory("4G") \
    .stdout_to("ml_output.txt") \
    .stderr_to("ml_errors.txt")

p.jobs.append(job)

# Convenience function
analysis_job = mpmsub.job(
    ["R", "--slave", "-f", "statistics.R"],
    cpu=1, memory="1G",
    stdout="stats_output.txt",
    stderr="stats_errors.txt"
)

p.jobs.append(analysis_job)
p.run()
```

### Pipeline Output Redirection

For pipelines, output redirection applies to the final command:

```python
import mpmsub

p = mpmsub.cluster(cpu=4, memory="8G")

# Pipeline with output redirection
data_pipeline = mpmsub.pipeline([
    ["cat", "raw_data.csv"],
    ["python", "clean_data.py"],
    ["python", "analyze_data.py"],
    ["python", "generate_report.py"]
], cpu=2, memory="3G", stdout="final_report.txt", stderr="pipeline_errors.txt")

p.jobs.append(data_pipeline)
p.run()
```

### Output Redirection Features

- **Automatic File Creation**: Output files are created automatically
- **Error Capture**: Both stdout and stderr can be captured separately
- **Pipeline Support**: Works with both single commands and pipelines
- **Path Handling**: Supports relative and absolute file paths

## Flexible API

mpmsub supports multiple parameter names for better usability and compatibility.

### CPU Parameter Names

```python
import mpmsub

# All of these are equivalent
job1 = mpmsub.job(["echo", "test"], p=4)           # Traditional
job2 = mpmsub.job(["echo", "test"], cpu=4)         # Alternative
job3 = mpmsub.job(["echo", "test"], cpus=4)        # Alternative

# Works with all interfaces
p = mpmsub.cluster(cpu=4, memory="8G")             # Alternative syntax
p = mpmsub.cluster(cpus=4, memory="8G")            # Alternative syntax
p = mpmsub.cluster(p=4, m="8G")                    # Traditional syntax
```

### Memory Parameter Names

```python
import mpmsub

# All of these are equivalent
job1 = mpmsub.job(["echo", "test"], m="1G")        # Traditional
job2 = mpmsub.job(["echo", "test"], memory="1G")   # Alternative

# Mixed usage is supported
job3 = mpmsub.job(["echo", "test"], cpu=2, m="1G")      # Mixed
job4 = mpmsub.job(["echo", "test"], p=2, memory="1G")   # Mixed
```

### Cluster Resource Description

Get information about available system resources:

```python
import mpmsub

# Show system resources when creating cluster
p = mpmsub.cluster(describe=True)

# Or call describe_resources() method
p = mpmsub.cluster(cpu=4, memory="8G")
p.describe_resources()
```

This will display:
- Total system CPU cores
- Total system memory
- Configured cluster limits
- Available resources for scheduling

## Advanced Examples

### Bioinformatics Pipeline

```python
import mpmsub

p = mpmsub.cluster(cpu=8, memory="32G")

# Quality control and trimming pipeline
qc_pipeline = mpmsub.pipeline([
    ["fastqc", "raw_reads.fastq"],
    ["trimmomatic", "SE", "raw_reads.fastq", "trimmed_reads.fastq", "TRAILING:20"],
    ["fastqc", "trimmed_reads.fastq"]
], cpu=4, memory="4G", id="qc_pipeline", stderr="qc_errors.txt")

# Assembly job with output redirection
assembly_job = mpmsub.Job(["spades.py", "--single", "trimmed_reads.fastq", "-o", "assembly"]) \
    .cpu(8) \
    .memory("16G") \
    .with_id("genome_assembly") \
    .stdout_to("assembly_log.txt") \
    .stderr_to("assembly_errors.txt")

# Annotation pipeline
annotation_pipeline = mpmsub.pipeline([
    ["prokka", "--outdir", "annotation", "assembly/contigs.fasta"],
    ["cp", "annotation/PROKKA_*.gff", "final_annotation.gff"]
], cpu=2, memory="2G", stdout="annotation_log.txt")

p.jobs.extend([qc_pipeline, assembly_job, annotation_pipeline])
p.run()
```

### Data Science Workflow

```python
import mpmsub

p = mpmsub.cluster(cpu=6, memory="16G")

# Data preprocessing pipeline
preprocessing = mpmsub.pipeline([
    ["python", "download_data.py"],
    ["python", "clean_data.py"],
    ["python", "feature_engineering.py"]
], cpu=2, memory="4G", stdout="preprocessing_log.txt", stderr="preprocessing_errors.txt")

# Model training jobs
models = [
    mpmsub.job(["python", "train_model.py", "--model", "rf"], 
               cpu=2, memory="3G", stdout="rf_training.log"),
    mpmsub.job(["python", "train_model.py", "--model", "xgb"], 
               cpu=2, memory="3G", stdout="xgb_training.log"),
    mpmsub.job(["python", "train_model.py", "--model", "nn"], 
               cpu=4, memory="6G", stdout="nn_training.log")
]

# Evaluation pipeline
evaluation = mpmsub.Job(["python", "evaluate_models.py"]) \
    .cpu(1) \
    .memory("2G") \
    .stdout_to("evaluation_results.txt") \
    .stderr_to("evaluation_errors.txt")

p.jobs.append(preprocessing)
p.jobs.extend(models)
p.jobs.append(evaluation)

p.run()
```

These advanced features make mpmsub suitable for complex computational workflows while maintaining simplicity and resource efficiency.
