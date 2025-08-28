#!/usr/bin/env python3
"""
Manual wiki synchronization script.

This script copies files from docs/wiki/ to a local wiki repository clone.
Use this as a backup if GitHub Actions aren't working.

Usage:
    python scripts/sync-wiki.py [wiki-repo-path]
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def sync_wiki_files(source_dir: Path, wiki_repo_path: Path):
    """Sync files from source_dir to wiki repository."""
    
    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} does not exist")
        return False
    
    if not wiki_repo_path.exists():
        print(f"Error: Wiki repository {wiki_repo_path} does not exist")
        return False
    
    # Copy all .md files from source to wiki repo
    for md_file in source_dir.glob("*.md"):
        dest_file = wiki_repo_path / md_file.name
        print(f"Copying {md_file} -> {dest_file}")
        shutil.copy2(md_file, dest_file)
    
    # Remove any .md files in wiki repo that don't exist in source
    for md_file in wiki_repo_path.glob("*.md"):
        source_file = source_dir / md_file.name
        if not source_file.exists():
            print(f"Removing {md_file} (not in source)")
            md_file.unlink()
    
    return True


def main():
    # Default paths
    project_root = Path(__file__).parent.parent
    source_dir = project_root / "docs" / "wiki"
    
    # Wiki repo path from command line or default
    if len(sys.argv) > 1:
        wiki_repo_path = Path(sys.argv[1])
    else:
        wiki_repo_path = project_root.parent / "hashsmith.wiki"
    
    print(f"Syncing from {source_dir} to {wiki_repo_path}")
    
    if sync_wiki_files(source_dir, wiki_repo_path):
        print("\nSync completed successfully!")
        print(f"\nTo commit and push changes:")
        print(f"cd {wiki_repo_path}")
        print("git add .")
        print("git commit -m 'Update wiki from main repo'")
        print("git push")
    else:
        print("Sync failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
