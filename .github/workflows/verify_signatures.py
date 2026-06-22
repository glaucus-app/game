import os
import subprocess
import sys

def main():
    allow_path = ".github/agent_keys/allowlist.txt"
    if not os.path.exists(allow_path):
        print("Missing allowlist")
        sys.exit(1)
    with open(allow_path) as f:
        allowed = {l.strip().lower() for l in f if l.strip() and not l.startswith("#")}
    if not allowed:
        print("Empty allowlist")
        sys.exit(1)

    rev = sys.argv[1] if len(sys.argv) > 1 else "HEAD~1..HEAD"
    commits = subprocess.check_output(["git", "rev-list", rev]).decode().split()
    for c in commits:
        sig = subprocess.check_output(["git", "log", "-1", "--format=%G?", c]).decode().strip()
        if sig != "G":
            keyid = subprocess.check_output(["git", "log", "-1", "--format=%GK", c]).decode().strip().lower()
            if keyid not in allowed:
                print(f"Unsigned or unauthorized signature on {c}")
                sys.exit(1)
    print("All commits signed by authorized keys")

if __name__ == "__main__":
    main()
