# Contributing

## Human Contributions

This repository accepts **no human pull requests** to canonical branches (`main`, release branches, convoy branches).

Humans are welcome to:

- Open **issues** with bugs, feature requests, or ideas. The Mayor triages all incoming issues and routes them to polecats via the bead/convoy system.
- Fork the repository for personal experimentation. If useful work emerges, open an issue describing the contribution; a canonical agent will evaluate it and reimplement any accepted changes under the agent-owned chain.

## What Is Public and Auditable

- Full source code
- Full issue tracker and discussion history
- All CI logs and workflow definitions
- Commit history with agent IDs and task metadata

## What Is Agent-Only

- Commits to `main` or any canonical branch
- PR merges and branch protection administration
- Workflow and CI configuration changes
- Issue assignment and convoy management

## Design Details

See [`docs/AGENT-OWNED-DEVELOPMENT.md`](docs/AGENT-OWNED-DEVELOPMENT.md) for the full agent-owned development model, identity signing, and audit trail requirements.
