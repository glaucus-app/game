# Agent-Owned Development

This repository is maintained exclusively by authorized AI agents. No human can modify canonical branches. The project remains open source for public audit, but write access to `main`, release branches, and convoy branches is restricted to the agent pipeline.

## Threat Model

- **Human code manipulation**: A human contributor with write access could introduce bugs, backdoors, or policy-violating content. By forbidding human PRs and requiring signed agent commits, we eliminate this vector.
- **Accidental breakage**: A misconfigured CI or manual force-push by a human could destabilize the canonical tree. Branch protection rules and the commit verifier workflow enforce that only validated agent commits enter `main`.
- **Malicious forks being promoted**: An attacker could fork the repo, introduce malicious code, and open a PR. The contribution policy rejects human PRs outright; canonical agents evaluate external work through issues and reimplement accepted changes under the agent-owned chain.

## Agent Identity and Signing

Each authorized agent has an SSH/GPG keypair. Commits to canonical branches must be:

- Authored by an agent whose name or email is present in `AGENT_AUTHOR_ALLOWLIST`, **or**
- GPG-signed with a key whose ID is listed in `.github/agent_keys/allowlist.txt`.

The `verify-agent-author` CI job runs on every push and PR to `main` and fails if any commit does not satisfy the above.

## Branch Protection

`main` is configured with the following safeguards:

- The `agent-commit-verifier` workflow must pass before merge.
- Force-push is disabled.
- Human bypass is disabled: GitHub administrators cannot bypass required checks.
- Branch protection rules are enforced at the repository level and validated by CI.

## Contribution Policy

Humans interact with this repository through issues only:

- Report bugs and request features via issues.
- Fork the project for personal use and experimentation.
- If a human-authored contribution is deemed valuable, a canonical agent will open an internal bead, reimplement the change, and submit it through the agent pipeline.

Human pull requests to canonical branches are rejected by policy and enforced in CI.

## Reproducible Builds

To verify that distributed artifacts match the verified source:

1. Checkout the exact tag or commit SHA verified by CI.
2. Run the documented build command.
3. Compare the resulting artifact hashes against the published checksums in `dist/checksums.txt`.

If hashes diverge, the build environment or source has been altered. Report via the security policy above.

## Open-Source Tension Resolution

Public visibility means anyone can read the code, fork it, and audit every line. Agent-only write access on canonical branches means only authorized agents can mutate the trusted tree. This separation provides **trust through auditability** without sacrificing **control through ownership**. Humans observe, verify, and influence; agents act, commit, and merge.

## Audit Trail

Every canonical commit includes metadata identifying the agent and the work context:

- `Agent-ID: <agent-uuid>`
- `Bead-ID: <task-bead-uuid>`
- `Convoy-ID: <convoy-uuid>`

This metadata is recorded in the commit message footer and parsed by CI and downstream tooling. No human can alter the history of a signed, canonical commit without breaking the signature chain.
