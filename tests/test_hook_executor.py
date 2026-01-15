import pytest
import os
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestHookExecutor:
    """Test hook execution functionality"""

    @pytest.fixture
    def temp_hook_script(self):
        """Create a temporary executable hook script"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write('#!/bin/bash\necho "Hook executed"\nexit 0')
            hook_path = f.name
        os.chmod(hook_path, 0o755)
        yield hook_path
        os.unlink(hook_path)

    @pytest.fixture
    def failing_hook_script(self):
        """Create a hook script that fails"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write('#!/bin/bash\necho "Hook failed" >&2\nexit 1')
            hook_path = f.name
        os.chmod(hook_path, 0o755)
        yield hook_path
        os.unlink(hook_path)

    def test_execute_hook_success(self, temp_hook_script):
        """Test successful hook execution"""
        result = subprocess.run([temp_hook_script], capture_output=True, text=True)
        assert result.returncode == 0
        assert "Hook executed" in result.stdout

    def test_execute_hook_failure(self, failing_hook_script):
        """Test hook execution with non-zero exit code"""
        result = subprocess.run([failing_hook_script], capture_output=True, text=True)
        assert result.returncode == 1
        assert "Hook failed" in result.stderr

    def test_hook_not_executable(self):
        """Test error when hook is not executable"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write('#!/bin/bash\necho "test"')
            hook_path = f.name
        try:
            with pytest.raises(PermissionError):
                result = subprocess.run([hook_path], capture_output=True, text=True, check=True)
        finally:
            os.unlink(hook_path)

    def test_hook_not_found(self):
        """Test error when hook script doesn't exist"""
        with pytest.raises(FileNotFoundError):
            subprocess.run(['/nonexistent/hook'], capture_output=True, text=True, check=True)

    @patch.dict(os.environ, {'GIT_DIR': '/fake/git', 'GIT_INDEX_FILE': '/fake/index'})
    def test_hook_with_git_env_vars(self, temp_hook_script):
        """Test hook execution with mocked git environment variables"""
        result = subprocess.run([temp_hook_script], capture_output=True, text=True, env=os.environ.copy())
        assert result.returncode == 0
        assert os.environ.get('GIT_DIR') == '/fake/git'
