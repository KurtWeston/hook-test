"""Unit tests for hook simulator."""
import pytest
import tempfile
from pathlib import Path
from hook_test.simulator import HookSimulator, HookType


@pytest.fixture
def temp_hook_script():
    """Create a temporary hook script."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh') as f:
        f.write('#!/bin/bash\necho "Hook executed"\nexit 0')
        script_path = Path(f.name)
    
    script_path.chmod(0o755)
    yield script_path
    script_path.unlink(missing_ok=True)


@pytest.fixture
def failing_hook_script():
    """Create a hook script that fails."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh') as f:
        f.write('#!/bin/bash\necho "Hook failed" >&2\nexit 1')
        script_path = Path(f.name)
    
    script_path.chmod(0o755)
    yield script_path
    script_path.unlink(missing_ok=True)


def test_pre_commit_success(temp_hook_script):
    simulator = HookSimulator()
    result = simulator.run_hook(
        HookType.PRE_COMMIT,
        temp_hook_script,
        staged_files=['test.py', 'README.md']
    )
    
    assert result['success'] is True
    assert result['exit_code'] == 0
    assert 'Hook executed' in result['stdout']


def test_pre_commit_failure(failing_hook_script):
    simulator = HookSimulator()
    result = simulator.run_hook(
        HookType.PRE_COMMIT,
        failing_hook_script,
        staged_files=['test.py']
    )
    
    assert result['success'] is False
    assert result['exit_code'] == 1
    assert 'Hook failed' in result['stderr']


def test_commit_msg_hook(temp_hook_script):
    simulator = HookSimulator()
    result = simulator.run_hook(
        HookType.COMMIT_MSG,
        temp_hook_script,
        commit_message='feat: test commit'
    )
    
    assert result['success'] is True
    assert result['hook_type'] == 'commit-msg'


def test_pre_push_hook(temp_hook_script):
    simulator = HookSimulator()
    result = simulator.run_hook(
        HookType.PRE_PUSH,
        temp_hook_script,
        remote_name='origin',
        remote_url='https://github.com/test/repo.git'
    )
    
    assert result['success'] is True
    assert result['hook_type'] == 'pre-push'


def test_nonexistent_script():
    simulator = HookSimulator()
    with pytest.raises(FileNotFoundError):
        simulator.run_hook(
            HookType.PRE_COMMIT,
            Path('/nonexistent/script.sh')
        )