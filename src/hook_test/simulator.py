"""Core hook simulation logic."""
import os
import subprocess
import tempfile
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class HookType(Enum):
    PRE_COMMIT = 'pre-commit'
    COMMIT_MSG = 'commit-msg'
    PRE_PUSH = 'pre-push'
    PREPARE_COMMIT_MSG = 'prepare-commit-msg'
    POST_COMMIT = 'post-commit'
    PRE_REBASE = 'pre-rebase'


class HookSimulator:
    def __init__(self, verbose: bool = False, git_dir: Optional[str] = None):
        self.verbose = verbose
        self.git_dir = Path(git_dir) if git_dir else Path.cwd() / '.git'
    
    def run_hook(
        self,
        hook_type: HookType,
        script_path: Path,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a hook script with simulated environment."""
        if not script_path.exists():
            raise FileNotFoundError(f"Hook script not found: {script_path}")
        
        if not os.access(script_path, os.X_OK):
            script_path.chmod(0o755)
        
        env = self._setup_environment(hook_type, **kwargs)
        
        if hook_type == HookType.PRE_COMMIT:
            return self._run_pre_commit(script_path, env, kwargs.get('staged_files', []))
        elif hook_type == HookType.COMMIT_MSG:
            return self._run_commit_msg(script_path, env, kwargs.get('commit_message', ''))
        elif hook_type == HookType.PRE_PUSH:
            return self._run_pre_push(script_path, env, kwargs)
        else:
            return self._run_generic(script_path, env, hook_type)
    
    def _setup_environment(self, hook_type: HookType, **kwargs) -> Dict[str, str]:
        """Setup git environment variables."""
        env = os.environ.copy()
        env['GIT_DIR'] = str(self.git_dir)
        env['GIT_INDEX_FILE'] = str(self.git_dir / 'index')
        env['GIT_AUTHOR_NAME'] = 'Test User'
        env['GIT_AUTHOR_EMAIL'] = 'test@example.com'
        env['GIT_COMMITTER_NAME'] = 'Test User'
        env['GIT_COMMITTER_EMAIL'] = 'test@example.com'
        return env
    
    def _run_pre_commit(self, script_path: Path, env: Dict[str, str], staged_files: List[str]) -> Dict[str, Any]:
        """Run pre-commit hook simulation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for file in staged_files:
                file_path = Path(tmpdir) / file
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(f"# Sample content for {file}\n")
            
            result = subprocess.run(
                [str(script_path)],
                env=env,
                cwd=tmpdir,
                capture_output=True,
                text=True
            )
        
        return self._format_result(script_path, HookType.PRE_COMMIT, result)
    
    def _run_commit_msg(self, script_path: Path, env: Dict[str, str], message: str) -> Dict[str, Any]:
        """Run commit-msg hook simulation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(message)
            msg_file = f.name
        
        try:
            result = subprocess.run(
                [str(script_path), msg_file],
                env=env,
                capture_output=True,
                text=True
            )
            return self._format_result(script_path, HookType.COMMIT_MSG, result)
        finally:
            Path(msg_file).unlink(missing_ok=True)
    
    def _run_pre_push(self, script_path: Path, env: Dict[str, str], kwargs: Dict) -> Dict[str, Any]:
        """Run pre-push hook simulation."""
        remote_name = kwargs.get('remote_name', 'origin')
        remote_url = kwargs.get('remote_url', 'https://github.com/user/repo.git')
        
        push_data = f"refs/heads/main abc123 refs/heads/main def456\n"
        
        result = subprocess.run(
            [str(script_path), remote_name, remote_url],
            env=env,
            input=push_data,
            capture_output=True,
            text=True
        )
        
        return self._format_result(script_path, HookType.PRE_PUSH, result)
    
    def _run_generic(self, script_path: Path, env: Dict[str, str], hook_type: HookType) -> Dict[str, Any]:
        """Run generic hook simulation."""
        result = subprocess.run(
            [str(script_path)],
            env=env,
            capture_output=True,
            text=True
        )
        
        return self._format_result(script_path, hook_type, result)
    
    def _format_result(self, script_path: Path, hook_type: HookType, result: subprocess.CompletedProcess) -> Dict[str, Any]:
        """Format hook execution result."""
        return {
            'hook_type': hook_type.value,
            'script_path': str(script_path),
            'exit_code': result.returncode,
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }