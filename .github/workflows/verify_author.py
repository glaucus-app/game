import os
import subprocess
import sys

def main():
    rev = sys.argv[1] if len(sys.argv) > 1 else "HEAD~1..HEAD"
    commits = subprocess.check_output(["git", "rev-list", rev]).decode().split()
    for c in commits:
        author = subprocess.check_output(["git", "log", "-1", "--format=%ae", c]).decode().strip()
        name = subprocess.check_output(["git", "log", "-1", "--format=%an", c]).decode().strip()
        committer_name = subprocess.check_output(["git", "log", "-1", "--format=%cN", c]).decode().strip()
        committer_email = subprocess.check_output(["git", "log", "-1", "--format=%cE", c]).decode().strip()
        if not (author.endswith("@gastown.local") or "(gastown)" in name or
                committer_name == "kilo-code-bot[bot]" or
                committer_email == "noreply@users.noreply.github.com" or
                committer_name == "kilo-code-bot[bot]" and "@users.noreply.github.com" in author):
            print(f"Unauthorized commit {c}: author={author} name={name} committer={committer_name} <{committer_email}>")
            sys.exit(1)
    print("All commits authorized")

if __name__ == "__main__":
    main()