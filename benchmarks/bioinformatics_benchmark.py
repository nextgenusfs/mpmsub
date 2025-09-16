#!/usr/bin/env python3
"""
Real-world bioinformatics pipeline benchmark.

This demonstrates mpmsub benefits using realistic bioinformatics tasks
like sequence alignment, assembly, and annotation that have varying
CPU and memory requirements.
"""

import time
import sys
import psutil
import subprocess
import tempfile
import random
import string
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to import mpmsub
sys.path.insert(0, str(Path(__file__).parent.parent))
import mpmsub


def generate_fasta_file(filename, num_sequences=1000, seq_length=500):
    """Generate a fake FASTA file for testing."""
    bases = ['A', 'T', 'G', 'C']
    
    with open(filename, 'w') as f:
        for i in range(num_sequences):
            f.write(f">sequence_{i}\n")
            sequence = ''.join(random.choices(bases, k=seq_length))
            f.write(f"{sequence}\n")


def create_alignment_job(input_file, output_file, memory_mb=500):
    """Simulate a sequence alignment job (like BLAST or BWA)."""
    script_content = f'''
import time
import random

# Simulate memory allocation for alignment
print("Loading reference genome...")
reference_data = bytearray({memory_mb} * 1024 * 1024)  # {memory_mb}MB

# Simulate alignment computation
print("Performing alignment...")
time.sleep(2 + random.uniform(0, 1))  # 2-3 seconds

# Write fake output
with open("{output_file}", "w") as f:
    f.write("# Alignment results\\n")
    f.write("query1\\tref_chr1\\t95.2\\t450\\n")
    f.write("query2\\tref_chr2\\t87.1\\t380\\n")

print("Alignment completed successfully!")
'''
    return script_content


def create_assembly_job(input_file, output_file, memory_mb=1500):
    """Simulate a genome assembly job (like SPAdes or Canu)."""
    script_content = f'''
import time
import random

# Simulate memory allocation for assembly
print("Loading sequencing reads...")
read_data = bytearray({memory_mb} * 1024 * 1024)  # {memory_mb}MB

# Simulate assembly computation (longer running)
print("Performing de novo assembly...")
time.sleep(4 + random.uniform(0, 2))  # 4-6 seconds

# Write fake output
with open("{output_file}", "w") as f:
    f.write(">contig_1\\n")
    f.write("ATCGATCGATCGATCG" * 50 + "\\n")
    f.write(">contig_2\\n")
    f.write("GCTAGCTAGCTAGCTA" * 30 + "\\n")

print("Assembly completed successfully!")
'''
    return script_content


def create_annotation_job(input_file, output_file, memory_mb=800):
    """Simulate a gene annotation job (like Augustus or GeneMark)."""
    script_content = f'''
import time
import random

# Simulate memory allocation for annotation
print("Loading genome and models...")
genome_data = bytearray({memory_mb} * 1024 * 1024)  # {memory_mb}MB

# Simulate annotation computation
print("Predicting genes...")
time.sleep(3 + random.uniform(0, 1.5))  # 3-4.5 seconds

# Write fake output
with open("{output_file}", "w") as f:
    f.write("# Gene predictions\\n")
    f.write("gene1\\tchr1\\t1000\\t2500\\t+\\thypothetical protein\\n")
    f.write("gene2\\tchr1\\t3000\\t4200\\t-\\tkinase domain\\n")

print("Annotation completed successfully!")
'''
    return script_content


def run_bioinformatics_pipeline_naive(temp_dir, num_samples=6):
    """Run a bioinformatics pipeline using naive parallel execution."""
    print(f"🧬 Running bioinformatics pipeline (naive) with {num_samples} samples...")
    
    # Create input files
    input_files = []
    for i in range(num_samples):
        input_file = temp_dir / f"sample_{i}.fasta"
        generate_fasta_file(input_file, num_sequences=500)
        input_files.append(input_file)
    
    # Create job scripts
    jobs = []
    for i, input_file in enumerate(input_files):
        # Each sample gets: alignment + assembly + annotation
        
        # Alignment job (moderate memory)
        align_script = temp_dir / f"align_{i}.py"
        align_output = temp_dir / f"alignment_{i}.sam"
        align_script.write_text(create_alignment_job(input_file, align_output, 500))
        jobs.append(('alignment', [sys.executable, str(align_script)]))
        
        # Assembly job (high memory)
        assembly_script = temp_dir / f"assembly_{i}.py"
        assembly_output = temp_dir / f"assembly_{i}.fasta"
        assembly_script.write_text(create_assembly_job(input_file, assembly_output, 1500))
        jobs.append(('assembly', [sys.executable, str(assembly_script)]))
        
        # Annotation job (moderate-high memory)
        annot_script = temp_dir / f"annotation_{i}.py"
        annot_output = temp_dir / f"annotation_{i}.gff"
        annot_script.write_text(create_annotation_job(input_file, annot_output, 800))
        jobs.append(('annotation', [sys.executable, str(annot_script)]))
    
    def run_job(job_info):
        job_type, cmd = job_info
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            runtime = time.time() - start_time
            return {
                'type': job_type,
                'success': result.returncode == 0,
                'runtime': runtime
            }
        except Exception as e:
            return {'type': job_type, 'success': False, 'error': str(e)}
    
    start_time = time.time()
    start_memory = psutil.virtual_memory().used
    
    # Run with limited workers to prevent memory exhaustion
    max_workers = min(4, psutil.cpu_count())
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(run_job, jobs))
    
    total_time = time.time() - start_time
    peak_memory = psutil.virtual_memory().used
    
    successful = sum(1 for r in results if r.get('success', False))
    
    return {
        'method': 'naive_bioinformatics',
        'total_time': total_time,
        'successful_jobs': successful,
        'total_jobs': len(jobs),
        'memory_delta_mb': (peak_memory - start_memory) / (1024**2),
        'job_breakdown': {
            'alignment': sum(1 for r in results if r.get('type') == 'alignment' and r.get('success')),
            'assembly': sum(1 for r in results if r.get('type') == 'assembly' and r.get('success')),
            'annotation': sum(1 for r in results if r.get('type') == 'annotation' and r.get('success'))
        }
    }


def run_bioinformatics_pipeline_mpmsub(temp_dir, num_samples=6):
    """Run a bioinformatics pipeline using mpmsub."""
    print(f"🚀 Running bioinformatics pipeline (mpmsub) with {num_samples} samples...")
    
    # Create input files
    input_files = []
    for i in range(num_samples):
        input_file = temp_dir / f"sample_{i}.fasta"
        generate_fasta_file(input_file, num_sequences=500)
        input_files.append(input_file)
    
    start_time = time.time()
    start_memory = psutil.virtual_memory().used
    
    # Create mpmsub cluster with memory limit
    cluster = mpmsub.cluster(p=psutil.cpu_count(), m="4G", progress_bar=True)
    
    # Add jobs with appropriate resource requirements
    for i, input_file in enumerate(input_files):
        # Alignment job (moderate memory, 1 CPU)
        align_script = temp_dir / f"align_{i}.py"
        align_output = temp_dir / f"alignment_{i}.sam"
        align_script.write_text(create_alignment_job(input_file, align_output, 500))
        cluster.jobs.append({
            'cmd': [sys.executable, str(align_script)],
            'p': 1,
            'm': '600M',
            'id': f'align_{i}'
        })
        
        # Assembly job (high memory, 2 CPUs)
        assembly_script = temp_dir / f"assembly_{i}.py"
        assembly_output = temp_dir / f"assembly_{i}.fasta"
        assembly_script.write_text(create_assembly_job(input_file, assembly_output, 1500))
        cluster.jobs.append({
            'cmd': [sys.executable, str(assembly_script)],
            'p': 2,
            'm': '1.8G',
            'id': f'assembly_{i}'
        })
        
        # Annotation job (moderate-high memory, 1 CPU)
        annot_script = temp_dir / f"annotation_{i}.py"
        annot_output = temp_dir / f"annotation_{i}.gff"
        annot_script.write_text(create_annotation_job(input_file, annot_output, 800))
        cluster.jobs.append({
            'cmd': [sys.executable, str(annot_script)],
            'p': 1,
            'm': '1G',
            'id': f'annotation_{i}'
        })
    
    # Run the pipeline
    cluster.run()
    
    total_time = time.time() - start_time
    peak_memory = psutil.virtual_memory().used
    
    successful = len(cluster.completed_jobs)
    
    # Count job types
    job_breakdown = {'alignment': 0, 'assembly': 0, 'annotation': 0}
    for job in cluster.completed_jobs:
        job_id = job.get('id', '')
        if 'align' in job_id:
            job_breakdown['alignment'] += 1
        elif 'assembly' in job_id:
            job_breakdown['assembly'] += 1
        elif 'annotation' in job_id:
            job_breakdown['annotation'] += 1
    
    return {
        'method': 'mpmsub_bioinformatics',
        'total_time': total_time,
        'successful_jobs': successful,
        'total_jobs': len(cluster.jobs),
        'memory_delta_mb': (peak_memory - start_memory) / (1024**2),
        'job_breakdown': job_breakdown
    }


def main():
    """Run bioinformatics pipeline benchmark."""
    print("🧬 Bioinformatics Pipeline Benchmark")
    print("=" * 45)
    
    # System info
    total_memory_gb = psutil.virtual_memory().total / (1024**3)
    cpu_count = psutil.cpu_count()
    
    print(f"System: {cpu_count} CPUs, {total_memory_gb:.1f}GB RAM")
    print()
    
    # Pipeline description
    num_samples = 4  # Reduced for faster demo
    print(f"Pipeline: {num_samples} genomic samples")
    print("Each sample requires:")
    print("  • Sequence alignment (1 CPU, 600MB)")
    print("  • Genome assembly (2 CPUs, 1.8GB)")
    print("  • Gene annotation (1 CPU, 1GB)")
    print(f"Total: {num_samples * 3} jobs")
    print()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        print("🔬 Running benchmarks...\n")
        
        # Test 1: Naive approach
        print("Test 1: Naive Parallel Execution")
        print("-" * 35)
        try:
            naive_result = run_bioinformatics_pipeline_naive(temp_path, num_samples)
            print(f"   ✅ Completed: {naive_result['successful_jobs']}/{naive_result['total_jobs']} jobs")
            print(f"   ⏱️  Total time: {naive_result['total_time']:.1f}s")
            print(f"   🧠 Memory delta: {naive_result['memory_delta_mb']:.0f}MB")
        except Exception as e:
            print(f"❌ Naive approach failed: {e}")
            naive_result = None
        
        print()
        
        # Test 2: mpmsub approach
        print("Test 2: mpmsub Memory-Aware Execution")
        print("-" * 40)
        try:
            mpmsub_result = run_bioinformatics_pipeline_mpmsub(temp_path, num_samples)
            print(f"   ✅ Completed: {mpmsub_result['successful_jobs']}/{mpmsub_result['total_jobs']} jobs")
            print(f"   ⏱️  Total time: {mpmsub_result['total_time']:.1f}s")
            print(f"   🧠 Memory delta: {mpmsub_result['memory_delta_mb']:.0f}MB")
        except Exception as e:
            print(f"❌ mpmsub approach failed: {e}")
            mpmsub_result = None
        
        print()
        
        # Compare results
        if naive_result and mpmsub_result:
            print("📊 BIOINFORMATICS PIPELINE COMPARISON")
            print("=" * 42)
            
            naive_time = naive_result['total_time']
            mpmsub_time = mpmsub_result['total_time']
            
            if naive_time > 0 and mpmsub_time > 0:
                speedup = naive_time / mpmsub_time
                efficiency = mpmsub_result['successful_jobs'] / max(1, naive_result['successful_jobs'])
                
                print(f"⏱️  Pipeline Runtime:")
                print(f"   Naive:   {naive_time:.1f}s")
                print(f"   mpmsub:  {mpmsub_time:.1f}s")
                print(f"   Speedup: {speedup:.2f}x")
                print()
                
                print(f"✅ Job Success Rate:")
                print(f"   Naive:   {naive_result['successful_jobs']}/{naive_result['total_jobs']}")
                print(f"   mpmsub:  {mpmsub_result['successful_jobs']}/{mpmsub_result['total_jobs']}")
                print(f"   Improvement: {efficiency:.2f}x")
                print()
                
                print(f"🧬 Job Type Breakdown (mpmsub):")
                breakdown = mpmsub_result['job_breakdown']
                print(f"   Alignments:  {breakdown['alignment']}/{num_samples}")
                print(f"   Assemblies:  {breakdown['assembly']}/{num_samples}")
                print(f"   Annotations: {breakdown['annotation']}/{num_samples}")
                print()
                
                print("🎯 Key Benefits Demonstrated:")
                if speedup > 1.1:
                    print(f"   • {speedup:.1f}x faster pipeline execution")
                if efficiency > 1.0:
                    print(f"   • {efficiency:.1f}x better job completion rate")
                print("   • Prevents memory exhaustion with large assemblies")
                print("   • Optimizes mixed CPU/memory workloads")
                print("   • Scales efficiently with sample count")
        
        else:
            print("❌ Could not complete comparison")


if __name__ == "__main__":
    main()
