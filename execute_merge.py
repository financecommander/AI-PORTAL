#!/usr/bin/env python3
"""Execute git commands to resolve PR #17 merge conflicts."""

import subprocess
import sys
import os

def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd, 
        shell=True, 
        cwd="/workspaces/AI-PORTAL",
        capture_output=True, 
        text=True
    )
    
    if result.stdout:
        print(f"  Output: {result.stdout.strip()}")
    if result.stderr:
        print(f"  Error: {result.stderr.strip()}")
    
    if check and result.returncode != 0:
        print(f"  ❌ Command failed with exit code {result.returncode}")
        return False
    
    print(f"  ✅ Success")
    return True

def main():
    """Execute the merge conflict resolution."""
    os.chdir("/workspaces/AI-PORTAL")
    
    print("=== Resolving PR #17 Merge Conflicts ===\n")
    
    # Step 1: Checkout PR branch
    if not run_command("git checkout copilot/implement-crewai-pipeline-wrapper"):
        print("\n❌ Failed to checkout PR branch")
        return 1
    
    # Step 2: Merge develop
    merge_result = run_command("git merge origin/develop", check=False)
    
    # Step 3: Resolve conflicts if any
    if not merge_result:
        print("\n⚠️  Merge conflicts detected, resolving...")
        
        run_command("git checkout --ours backend/.env.example", check=False)
        run_command("git checkout --ours backend/main.py", check=False)
        run_command("git checkout --ours backend/routes/__init__.py", check=False)
        
        # Step 4: Stage resolved files
        run_command("git add backend/.env.example backend/main.py backend/routes/__init__.py", check=False)
        
        # Step 5: Complete merge
        if not run_command('git commit -m "fix: resolve merge conflicts — keep PR #17 versions"'):
            print("\n❌ Failed to commit merge resolution")
            return 1
    else:
        print("\n✅ Merge completed without conflicts")
    
    # Step 6: Push
    if not run_command("git push origin copilot/implement-crewai-pipeline-wrapper"):
        print("\n❌ Failed to push changes")
        return 1
    
    print("\n=== ✅ Successfully resolved PR #17 merge conflicts ===")
    
    # Show latest commit
    run_command("git log -1 --oneline")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
