#!/usr/bin/env python3
"""
Git Commit Generator - A tool to generate multiple empty commits with progress tracking.
"""
import argparse
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

@dataclass
class CommitConfig:
    """Configuration for git commit generation."""
    count: int
    auto_push: bool
    message_prefix: str = "Commit"
    branch: Optional[str] = None
    dry_run: bool = False

def run_command(command: str, capture_output: bool = False) -> Tuple[bool, str]:
    """Execute a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=capture_output,
            executable="/bin/bash"
        )
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr if capture_output else str(e)

def get_current_branch() -> str:
    """Get the current git branch name."""
    success, output = run_command("git rev-parse --abbrev-ref HEAD", capture_output=True)
    if not success:
        print("Error: Not a git repository or no commits yet.")
        sys.exit(1)
    return output.strip()

def make_commit(commit_number: int, total_commits: int, config: CommitConfig) -> bool:
    """Create a single commit with the given configuration."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"{config.message_prefix} {commit_number + 1} of {total_commits} at {timestamp}"
    
    if config.dry_run:
        print(f"[DRY RUN] Would commit: {message}")
        return True
        
    success, _ = run_command(f'git commit --allow-empty -m "{message}"')
    return success

def main():
    """Main function to handle command-line arguments and execute the commit process."""
    parser = argparse.ArgumentParser(description='Generate multiple git commits.')
    parser.add_argument('count', type=int, help='Number of commits to generate')
    parser.add_argument('--push', '-p', action='store_true', help='Auto push after commits')
    parser.add_argument('--prefix', default='Commit', help='Custom commit message prefix')
    parser.add_argument('--branch', help='Specify branch to commit to (default: current branch)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    if args.count <= 0:
        print("Error: Count must be a positive integer.")
        sys.exit(1)
    
    config = CommitConfig(
        count=args.count,
        auto_push=args.push,
        message_prefix=args.prefix,
        branch=args.branch,
        dry_run=args.dry_run
    )
    
    print(f"\nStarting commit generation for {config.count} commits")
    print(f"Branch: {config.branch or get_current_branch()}")
    print(f"Auto-push: {'Yes' if config.auto_push else 'No'}")
    if config.dry_run:
        print("DRY RUN MODE: No changes will be made")
    print("-" * 50)
    
    failed_commits = 0
    
    for i in range(config.count):
        progress = (i + 1) / config.count * 100
        print(f"\rCommitting... {i + 1}/{config.count} ({progress:.1f}%)", end="")
        
        if not make_commit(i, config.count, config):
            failed_commits += 1
    
    print("\n\nCommit generation complete!")
    
    if failed_commits > 0:
        print(f"Warning: {failed_commits} commits failed")
    
    if config.auto_push and not config.dry_run:
        print("\nPushing changes to remote...")
        success, output = run_command("git push", capture_output=True)
        if success:
            print("Successfully pushed to remote")
        else:
            print(f"Failed to push: {output}")
    elif config.auto_push and config.dry_run:
        print("\n[DRY RUN] Would push changes to remote")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)