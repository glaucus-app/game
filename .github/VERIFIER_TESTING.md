# Agent Commit Verifier — Local Testing Guide

Use these steps to verify pass/fail behavior for agent and human commits before pushing.

## Prerequisites

- Python 3.11+
- Git
- A repository with `.github/agent_keys/allowlist.txt` configured

## Quick Test Script (local pass/fail simulation)

```bash
#!/usr/bin/env bash
set -euo pipefail

# Set up a temp repo to test against
rm -rf /tmp/verifier-test && mkdir /tmp/verifier-test && cd /tmp/verifier-test
git init -b main
git config user.name "Test Agent"
git config user.email "test-agent@example.com"

# Create allowlist containing this test identity
mkdir -p .github/agent_keys
echo "test-agent@example.com" > .github/agent_keys/allowlist.txt
git add .github/agent_keys/allowlist.txt
git commit -m "init: add agent allowlist"

# Simulate an allowed agent commit (PASS)
echo "allowed" > file.txt
git add file.txt
git commit -m "agent commit"

# Run verifier logic inline
python3 - <<'PY'
import os, subprocess, sys

allowlist = set()
with open(".github/agent_keys/allowlist.txt") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            allowlist.add(line)

base = subprocess.run(["git", "rev-parse", "HEAD~1"], capture_output=True, text=True).stdout.strip()
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
commits = subprocess.run(["git", "rev-list", f"{base}..{head}"], capture_output=True, text=True).stdout.strip().split("\n")

passed = True
for c in commits:
    if not c:
        continue
    info = subprocess.run(["git", "show", "-s", "--format=%H|%an|%ae|%G?", c], capture_output=True, text=True)
    _, an, ae, sig = info.stdout.strip().split("|")
    key_id = sig[1:].strip() if sig != "N" and sig.startswith("G") else None
    author_ok = an in allowlist or ae in allowlist
    sig_ok = key_id and key_id in allowlist
    if not (author_ok or sig_ok):
        print(f"FAIL: commit {c} by {an} <{ae}> is not an authorized agent")
        passed = False

print("PASS" if passed else "FAIL")
sys.exit(0 if passed else 1)
PY

# Simulate a human (disallowed) commit (FAIL)
git config user.name "Human User"
git config user.email "human@example.com"
echo "human change" >> file.txt
git add file.txt
git commit -m "human commit"

# Verify failure
python3 - <<'PY'
import os, subprocess, sys

allowlist = set()
with open(".github/agent_keys/allowlist.txt") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            allowlist.add(line)

base = subprocess.run(["git", "rev-parse", "HEAD~1"], capture_output=True, text=True).stdout.strip()
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
commits = subprocess.run(["git", "rev-list", f"{base}..{head}"], capture_output=True, text=True).stdout.strip().split("\n")

failed = False
for c in commits:
    if not c:
        continue
    info = subprocess.run(["git", "show", "-s", "--format=%H|%an|%ae|%G?", c], capture_output=True, text=True)
    parts = info.stdout.strip().split("|")
    _, an, ae, sig = parts if len(parts) >= 4 else ("", "", "", "N")
    key_id = sig[1:].strip() if sig != "N" and sig.startswith("G") else None
    author_ok = an in allowlist or ae in allowlist
    sig_ok = key_id and key_id in allowlist
    if not (author_ok or sig_ok):
        print(f"FAIL: commit {c} by {an} <{ae}> is not an authorized agent")
        failed = True

print("FAIL (expected)" if failed else "PASS (unexpected)")
sys.exit(1 if failed else 0)
PY
```

## Expected Results

| Scenario | Expected outcome |
|----------|------------------|
| Agent commit (email in allowlist) | PASS |
| Human commit (email not in allowlist) | FAIL |
| Mixed bag with at least one human | FAIL |

## Notes

- The CI workflow uses `shell: python` (no `{0}` placeholder) for inline scripts.
- `AGENT_AUTHOR_ALLOWLIST` repo variable takes precedence; `.github/agent_keys/allowlist.txt` is the fallback.
- If both sources are empty, the job fails immediately with a clear error message.
