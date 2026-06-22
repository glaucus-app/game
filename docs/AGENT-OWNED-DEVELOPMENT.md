# Agent-Owned Development

This document defines the agent-owned development model for this repository.

## Threat Model

We protect against three classes of threat:

1. **Human code manipulation** — unauthorized modification of canonical source by a human with push access.
2. **Accidental breakage** — untested or unreviewed changes landing on `main` from outside the agent coordination pipeline.
3. **Malicious forks being promoted** — a compromised or rogue fork whose changes are merged into canonical branches.

The model does not prevent humans from reading, forking, or opening issues. It restricts write operations on canonical branches to authorized AI agents.

## Agent Identity & Signing

Each polecat agent holds an SSH/GPG keypair. Commits to canonical branches are signed with the agent's GPG key. The public key is registered in `.github/agent_keys/allowlist.txt`.

CI verifies every commit against:
- The `AGENT_AUTHOR_ALLOWLIST` repository variable (comma-separated emails or names), **or**
- A valid GPG signature whose key ID appears in `.github/agent_keys/allowlist.txt`.

## Branch Protection

- `main` requires the `agent-commit-verifier` workflow to pass before merging.
- Force-push is disabled on `main` and all convoy/release branches.
- No human bypass of branch-protection rules is permitted.

## Contribution Policy

Humans may open issues with ideas, bug reports, or feedback. The Mayor triages issues and assigns work to agents via the coordination pipeline.

If a human wants to contribute code, they fork the repository. Canonical agents may adopt the work by opening an agent-authored PR that reimplements the change. Direct human PRs to canonical branches are blocked by automation.

## Reproducible Builds

Distributed binaries are built in CI from the exact source tree present on the signed commit. The build record includes the commit SHA and the list of GPG signatures. Anyone can reproduce the build by checking out the signed commit and running the same CI steps.

## Open-Source Tension Resolution

Public visibility plus agent-only write access creates **trust, not control**. The full source, issue tracker, and discussion remain public. The write path is restricted to agents so that every change is attributable, signed, and verified. Auditors can inspect the full history; humans cannot inject unverified code into `main`.

## Audit Trail

Every commit to a canonical branch includes metadata in the commit message:

- `Agent-ID: <polecat UUID>`
- `Bead-ID: <task bead UUID>`
- `Convoy-ID: <convoy UUID>`

The verifier workflow does not enforce message format directly, but the Mayor and refinery chain review commit messages before landing.

## Local Test

To verify the workflow logic locally:

```bash
# Configure allowlist
export AGENT_AUTHOR_ALLOWLIST="agent@example.com,clover-bot"

# Test with an authorized commit
git commit --allow-empty -m "test authorized" --author="agent@example.com"
python3 .github/workflows/verify_author.py

# Test with an unauthorized commit
git commit --allow-empty -m "test unauthorized" --author="human@example.com"
python3 .github/workflows/verify_author.py && echo "should fail"
```

Signature verification requires importing the agent's public key:

```bash
gpg --import .github/agent_keys/agent.pub
git commit --allow-empty -m "test signed" -S
python3 .github/workflows/verify_signatures.py
```
