"""CLI interface for hook-test."""
import click
import sys
from pathlib import Path
from .simulator import HookSimulator, HookType


@click.group()
@click.version_option()
def cli():
    """Test git hooks locally without committing."""
    pass


@cli.command()
@click.argument('hook_script', type=click.Path(exists=True))
@click.option('--files', '-f', multiple=True, help='Staged files to simulate')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed execution info')
@click.option('--git-dir', type=click.Path(), help='Custom .git directory path')
def pre_commit(hook_script, files, verbose, git_dir):
    """Test a pre-commit hook with simulated staged files."""
    simulator = HookSimulator(verbose=verbose, git_dir=git_dir)
    files_list = list(files) if files else ['sample.py', 'README.md']
    
    result = simulator.run_hook(
        HookType.PRE_COMMIT,
        Path(hook_script),
        staged_files=files_list
    )
    
    _display_result(result, verbose)
    sys.exit(result['exit_code'])


@cli.command()
@click.argument('hook_script', type=click.Path(exists=True))
@click.option('--message', '-m', help='Commit message to test')
@click.option('--message-file', type=click.Path(exists=True), help='File containing commit message')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed execution info')
@click.option('--git-dir', type=click.Path(), help='Custom .git directory path')
def commit_msg(hook_script, message, message_file, verbose, git_dir):
    """Test a commit-msg hook with a sample commit message."""
    simulator = HookSimulator(verbose=verbose, git_dir=git_dir)
    
    if message_file:
        msg = Path(message_file).read_text()
    elif message:
        msg = message
    else:
        msg = "feat: add new feature\n\nThis is a sample commit message for testing."
    
    result = simulator.run_hook(
        HookType.COMMIT_MSG,
        Path(hook_script),
        commit_message=msg
    )
    
    _display_result(result, verbose)
    sys.exit(result['exit_code'])


@cli.command()
@click.argument('hook_script', type=click.Path(exists=True))
@click.option('--remote', default='origin', help='Remote name')
@click.option('--url', default='https://github.com/user/repo.git', help='Remote URL')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed execution info')
@click.option('--git-dir', type=click.Path(), help='Custom .git directory path')
def pre_push(hook_script, remote, url, verbose, git_dir):
    """Test a pre-push hook with simulated push data."""
    simulator = HookSimulator(verbose=verbose, git_dir=git_dir)
    
    result = simulator.run_hook(
        HookType.PRE_PUSH,
        Path(hook_script),
        remote_name=remote,
        remote_url=url
    )
    
    _display_result(result, verbose)
    sys.exit(result['exit_code'])


@cli.command()
@click.argument('hook_script', type=click.Path(exists=True))
@click.option('--hook-type', type=click.Choice(['prepare-commit-msg', 'post-commit', 'pre-rebase']), required=True)
@click.option('--verbose', '-v', is_flag=True, help='Show detailed execution info')
@click.option('--git-dir', type=click.Path(), help='Custom .git directory path')
def generic(hook_script, hook_type, verbose, git_dir):
    """Test other git hooks with basic simulation."""
    simulator = HookSimulator(verbose=verbose, git_dir=git_dir)
    hook_type_enum = HookType[hook_type.upper().replace('-', '_')]
    
    result = simulator.run_hook(hook_type_enum, Path(hook_script))
    
    _display_result(result, verbose)
    sys.exit(result['exit_code'])


def _display_result(result, verbose):
    """Display hook execution results."""
    if verbose:
        click.echo(f"\n{'='*60}")
        click.echo(f"Hook: {result['hook_type']}")
        click.echo(f"Script: {result['script_path']}")
        click.echo(f"{'='*60}\n")
    
    if result['stdout']:
        click.echo(result['stdout'], nl=False)
    
    if result['stderr']:
        click.secho(result['stderr'], fg='red', err=True, nl=False)
    
    if verbose:
        click.echo(f"\n{'='*60}")
        click.echo(f"Exit Code: {result['exit_code']}")
        status = click.style('SUCCESS', fg='green') if result['success'] else click.style('FAILED', fg='red')
        click.echo(f"Status: {status}")
        click.echo(f"{'='*60}")
    elif not result['success']:
        click.secho(f"\nHook failed with exit code {result['exit_code']}", fg='red', err=True)


if __name__ == '__main__':
    cli()