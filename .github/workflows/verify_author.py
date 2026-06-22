import os
import subprocess
import sys

def main():
    allowlist = os.environ.get("AGENT_AUTHOR_ALLOWLIST", "")
    allowed = {a.strip().lower() for a in allowlist.split(",") if a.strip()}
    if not allowed:
        print("AGENT_AUTHOR_ALLOWLIST is empty")
        sys.exit(1)

    rev = sys.argv[1] if len(sys.argv) > 1 else "HEAD~1..HEAD"
    commits = subprocess.check_output(["git", "rev-list", rev]).decode().split()
    for c in commits:
        author = subprocess.check_output(["git", "log", "-1", "--format=%ae", c]).decode().strip().lower()
        name = subprocess.check_output(["git", "log", "-1", "--format=%an", c]).decode().strip().lower()
        if author not in allowed and name not in allowed:
            print(f"Unauthorized commit {c}: author={author} name={name}")
            sys.exit(1)
    print("All commits authorized")

if __name__ == "__main__":
    main()
