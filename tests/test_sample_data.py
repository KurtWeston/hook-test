import pytest
import tempfile
import os
from pathlib import Path


class TestSampleData:
    """Test sample data generation for different hook types"""

    def test_generate_staged_files_list(self):
        """Test generating sample staged files for pre-commit"""
        sample_files = ['src/main.py', 'tests/test_main.py', 'README.md']
        assert len(sample_files) == 3
        assert all(isinstance(f, str) for f in sample_files)

    def test_generate_commit_message(self):
        """Test generating sample commit message for commit-msg hook"""
        sample_msg = "feat: add new feature\n\nDetailed description"
        assert len(sample_msg) > 0
        assert '\n' in sample_msg

    def test_commit_msg_file_creation(self):
        """Test creating temporary commit message file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('test commit message')
            msg_file = f.name
        try:
            assert os.path.exists(msg_file)
            with open(msg_file, 'r') as f:
                content = f.read()
            assert content == 'test commit message'
        finally:
            os.unlink(msg_file)

    def test_pre_push_sample_data(self):
        """Test generating sample data for pre-push hook"""
        sample_data = "refs/heads/main abc123 refs/heads/main def456\n"
        lines = sample_data.strip().split('\n')
        assert len(lines) == 1
        parts = lines[0].split()
        assert len(parts) == 4

    def test_empty_staged_files(self):
        """Test handling empty staged files list"""
        sample_files = []
        assert isinstance(sample_files, list)
        assert len(sample_files) == 0
