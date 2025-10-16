#!/usr/bin/env python3
"""
Basic tests for mpmsub library.
"""

import os
import sys

import pytest

# Add parent directory to path so we can import mpmsub
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mpmsub
from mpmsub.utils import parse_cpu_string, parse_memory_string, validate_job


class TestUtils:
    """Test utility functions."""

    def test_parse_memory_string(self):
        """Test memory string parsing."""
        assert parse_memory_string("1G") == 1024
        assert parse_memory_string("2048M") == 2048
        assert parse_memory_string("1024") == 1024
        assert parse_memory_string(2048) == 2048
        assert parse_memory_string(None) is None

        with pytest.raises(ValueError):
            parse_memory_string("invalid")

    def test_parse_cpu_string(self):
        """Test CPU string parsing."""
        assert parse_cpu_string("4") == 4
        assert parse_cpu_string(6) == 6
        assert parse_cpu_string(None) is None

        with pytest.raises(ValueError):
            parse_cpu_string("invalid")

    def test_validate_job(self):
        """Test job validation."""
        # Valid job
        job = {"cmd": ["echo", "hello"], "p": 1, "m": "100M"}
        validated = validate_job(job)
        assert validated["cmd"] == ["echo", "hello"]
        assert validated["p"] == 1
        assert validated["m"] == 100

        # Invalid job - missing cmd
        with pytest.raises(ValueError):
            validate_job({"p": 1, "m": "100M"})

        # Invalid job - empty cmd
        with pytest.raises(ValueError):
            validate_job({"cmd": [], "p": 1, "m": "100M"})


class TestCluster:
    """Test cluster functionality."""

    def test_cluster_creation(self):
        """Test cluster creation."""
        # Auto-detect resources
        p = mpmsub.cluster()
        assert p.max_cpus > 0
        assert p.max_memory_mb > 0

        # Explicit resources
        p = mpmsub.cluster(p=4, m="2G")
        assert p.max_cpus == 4
        assert p.max_memory_mb == 2048

    def test_job_management(self):
        """Test job queue management."""
        p = mpmsub.cluster(p=2, m="1G")

        # Add jobs
        job_id1 = p.jobs.append({"cmd": ["echo", "test1"]})
        job_id2 = p.jobs.append({"cmd": ["echo", "test2"]})

        assert len(p.jobs) == 2
        assert job_id1 != job_id2

    def test_simple_execution(self):
        """Test simple job execution."""
        p = mpmsub.Cluster(cpus=2, memory="1G", verbose=False)

        # Add simple jobs
        p.jobs.append({"cmd": ["echo", "hello"]})
        p.jobs.append({"cmd": ["echo", "world"]})

        # Run jobs
        results = p.run()

        # Check results
        assert len(p.completed_jobs) == 2
        assert len(p.failed_jobs) == 0
        assert all(job.success for job in p.completed_jobs)

        # Check outputs
        outputs = [job.stdout.strip() for job in p.completed_jobs]
        assert "hello" in outputs
        assert "world" in outputs

    def test_job_defaults(self):
        """Test job defaults for p and m."""
        p = mpmsub.cluster(p=2, m="1G")
        p.verbose = False

        # Job with no p or m specified
        job_id = p.jobs.append({"cmd": ["echo", "test"]})

        # Check that defaults were applied
        job = p.job_queue.pending_jobs[0]
        assert job["p"] == 1  # Default CPU
        assert job["m"] is None  # No memory limit by default

        # Job with only p specified
        p.jobs.append({"cmd": ["echo", "test2"], "p": 2})
        job2 = p.job_queue.pending_jobs[1]
        assert job2["p"] == 2
        assert job2["m"] is None

        # Job with only m specified
        p.jobs.append({"cmd": ["echo", "test3"], "m": "100M"})
        job3 = p.job_queue.pending_jobs[2]
        assert job3["p"] == 1
        assert job3["m"] == 100

    def test_profiling(self):
        """Test profiling functionality."""
        p = mpmsub.cluster(p=2, m="1G")
        p.verbose = False

        # Add jobs for profiling
        p.jobs.append({"cmd": ["echo", "profile_test1"]})
        p.jobs.append({"cmd": ["python3", "-c", "print('profile_test2')"]})

        # Run profiling
        results = p.profile(verbose=False)

        # Check results
        assert len(results) == 2
        assert all(r.success for r in results)
        assert all(r.runtime > 0 for r in results)

        # Check that jobs were moved to completed
        assert len(p.completed_jobs) == 2
        assert len(p.job_queue.pending_jobs) == 0

    def test_progress_bar(self):
        """Test progress bar functionality."""
        # Test with progress bar enabled
        cluster_with_progress = mpmsub.cluster(p=2, m="1G", progress_bar=True)
        cluster_with_progress.jobs.append({"cmd": ["echo", "test"], "p": 1})
        results = cluster_with_progress.run()
        assert results["jobs"]["completed"] == 1

        # Test with progress bar disabled
        cluster_no_progress = mpmsub.cluster(p=2, m="1G", progress_bar=False)
        cluster_no_progress.jobs.append({"cmd": ["echo", "test"], "p": 1})
        results = cluster_no_progress.run()
        assert results["jobs"]["completed"] == 1

        # Test progress bar with profiling
        cluster_profile = mpmsub.cluster(p=2, m="1G", progress_bar=True)
        cluster_profile.jobs.append({"cmd": ["echo", "test"], "p": 1})
        profile_results = cluster_profile.profile(verbose=False)
        assert len(profile_results) == 1
        assert profile_results[0].success

    def test_job_object_interface(self):
        """Test the new Job object interface."""
        # Test basic Job creation
        job = mpmsub.Job(["echo", "test"])
        assert job.cmd == ["echo", "test"]
        assert job.p is None  # Default
        assert job.m is None  # Default

        # Test builder pattern
        job2 = (
            mpmsub.Job(["echo", "test2"])
            .cpu(2)
            .memory("1G")
            .with_id("test_job")
            .with_timeout(30.0)
        )

        assert job2.p == 2
        assert job2.m == "1G"
        assert job2.id == "test_job"
        assert job2.timeout == 30.0

        # Test to_dict conversion
        job_dict = job2.to_dict()
        expected = {
            "cmd": ["echo", "test2"],
            "p": 2,
            "m": "1G",
            "id": "test_job",
            "cwd": None,
            "env": None,
            "timeout": 30.0,
            "stdout": None,
            "stderr": None,
        }
        assert job_dict == expected

        # Test adding Job objects to cluster
        cluster = mpmsub.cluster(p=2, m="1G")
        cluster.jobs.append(job)
        cluster.jobs.append(job2)

        results = cluster.run()
        assert results["jobs"]["completed"] == 2

    def test_mixed_job_interfaces(self):
        """Test mixing Job objects and dictionaries."""
        cluster = mpmsub.cluster(p=2, m="1G")

        # Add mix of Job objects and dictionaries
        jobs_to_add = [
            {"cmd": ["echo", "dict_job"], "p": 1, "m": "100M"},
            mpmsub.Job(["echo", "object_job"]).cpu(1).memory("150M"),
        ]

        cluster.jobs.extend(jobs_to_add)

        # Verify both were added correctly
        assert len(cluster.jobs) == 2

        results = cluster.run()
        assert results["jobs"]["completed"] == 2


if __name__ == "__main__":
    pytest.main([__file__])
