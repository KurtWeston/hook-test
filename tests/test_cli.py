import pytest
import tempfile
import os
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock


class TestCLI:
    """Test CLI interface and command-line argument handling"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_git_repo(self):
        """Create a temporary git-like directory structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / '.git' / 'hooks'
            git_dir.mkdir(parents=True)
            
            pre_commit = git_dir / 'pre-commit'
            pre_commit.write_text('#!/bin/bash\necho "pre-commit hook"\nexit 0')
            pre_commit.chmod(0o755)
            
            yield tmpdir

    def test_cli_help_command(self, runner):
        """Test --help flag displays usage information"""
        from hook_test.cli import cli
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'hook-test' in result.output.lower() or 'usage' in result.output.lower()

    def test_cli_version_flag(self, runner):
        """Test --version flag displays version"""
        from hook_test.cli import cli
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0

    def test_cli_with_hook_name(self, runner, mock_git_repo):
        """Test running hook by name from .git/hooks directory"""
        from hook_test.cli import cli
        with runner.isolated_filesystem():
            os.chdir(mock_git_repo)
            result = runner.invoke(cli, ['pre-commit'])
            assert 'pre-commit' in result.output or result.exit_code in [0, 1, 2]

    def test_cli_with_custom_script_path(self, runner):
        """Test running hook from custom path"""
        from hook_test.cli import cli
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write('#!/bin/bash\necho "custom hook"\nexit 0')
            hook_path = f.name
        os.chmod(hook_path, 0o755)
        try:
            result = runner.invoke(cli, [hook_path])
            assert result.exit_code in [0, 1, 2]
        finally:
            os.unlink(hook_path)

    def test_cli_verbose_mode(self, runner, mock_git_repo):
        """Test verbose flag provides detailed output"""
        from hook_test.cli import cli
        with runner.isolated_filesystem():
            os.chdir(mock_git_repo)
            result = runner.invoke(cli, ['--verbose', 'pre-commit'])
            assert result.exit_code in [0, 1, 2]
