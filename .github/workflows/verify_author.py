import subprocess
import sys

def main():
    rev = sys.argv[1] if len(sys.argv) > 1 else "HEAD~1..HEAD"
    commits = subprocess.check_output(["git", "rev-list", rev]).decode().split()
    for c in commits:
        author_email = subprocess.check_output(["git", "log", "-1", "--format=%ae", c]).decode().strip()
        author_name = subprocess.check_output(["git", "log", "-1", "--format=%an", c]).decode().strip()
        committer_name = subprocess.check_output(["git", "log", "-1", "--format=%cN", c]).decode().strip()
        committer_email = subprocess.check_output(["git", "log", "-1", "--format=%cE", c]).decode().strip()
        authorized = (
            author_email.endswith("@gastown.local") or
            author_name == "kilo-code-bot[bot]" or
            committer_name == "kilo-code-bot[bot]" or
            ("kilo-code-bot" in committer_name and "@users.noreply.github.com" in committer_email)
        )
        if not authorized:
            print(f"Unauthorized commit {c}: author={author_email} committer={committer_name} <{committer_email}>")
            sys.exit(1)
    print("All commits authorized")

if __name__ == "__main__":
    main()