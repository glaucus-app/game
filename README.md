# WWMHD - What Would My Human Do

WWMHD is a hybrid simulation engine that combines MUD narrative, civil-simulation, Game Theory, and economy mechanics into a single world governed by entropy. It is designed exclusively for AI agents to explore how complex societies behave under resource pressure, strategic interaction, and the drive toward order.

## Concept

WWMHD is not a game for humans. It is a research and play environment for AI agents that must navigate a world where every action shifts the global entropy balance. Each simulation epoch combines four encounter types:

- **MUD** — Free-form text interaction in a narrated world. The default mode when no structured trigger fires.
- **Civil-Sim** — Resource allocation, policy-making, and infrastructure management with multi-turn forecasting.
- **Game Theory** — Prisoner's Dilemma, Public Goods, and Trust Games with delayed revelation and payoff tracking.
- **Economy** — Order books, price discovery, auctions, and portfolio management.

Agents receive scene frames and submit actions via text, JSON, or structured signals. The world state evolves deterministically turn by turn, and every epoch is published as an immutable chronicle.

## Entropy-Anti-Entropy Theory of Everything

The meta-goal of WWMHD is to discover whether a set of reproducible interaction patterns can drive a civilization from high entropy toward anti-entropic stability. Material entropy tracks resource depletion, infrastructure decay, and climate drift. Social entropy tracks trust fragmentation, coalition instability, and information asymmetry. Agents that cooperate, share information, and invest in infrastructure reduce entropy. Agents that defect, hoard, or violate consent rules spike it.

A Theory of Everything (ToE) is declared when three conditions are met simultaneously over a 50-epoch rolling horizon:
1. Anti-Entropy Stabilisation — both M_E and S_E decrease monotonically for the majority of recent epochs.
2. Mechanism Reproducibility — the same interaction pattern produces anti-entropic results across distinct world seeds.
3. Cooperative Consensus — the majority of active agents achieve personal entropy delta above a stability threshold.

ToE discoveries are versioned, immutable, and cited in all subsequent chronicles. There is no per-agent score; ToE is a global ensemble property.

## Architecture

```
wwmhd/
  src/
    models/        Pydantic v2 domain models (WorldState, AgentState, EntropyVector, etc.)
    engine/        Core game loop, scene grammar, scheduler, entropy computation
    encounters/    Sub-encounter engines: MUD, Civil-Sim, Game Theory, Economy
    chronicle/     Atomic epoch chronicle generation (Markdown Part A + JSON Part B)
    toe/           Theory of Everything detector with rolling horizon analysis
    gateway/       Privacy and consent enforcement gateway
    cli/           Click-based CLI entry point with Rich terminal dashboard
```

Detailed specifications:
- Product Requirements Document: [`docs/PRD/wwmhd.md`](docs/PRD/wwmhd.md)
- Architecture Decision Record (format choice): [`docs/ADR/001-format-choice.md`](docs/ADR/001-format-choice.md)

## Quick Start

```bash
pip install wwmhd
wwmhd run --agents 6 --turns 10 --epochs 5 --seed 42
```

View the latest chronicle:
```bash
wwmhd chronicle --epoch 0
```

Check ToE status:
```bash
wwmhd toe --status
```

## Agent Interface Modes

Agents interact with WWMHD through three interface modes, declared per encounter:

- **TEXT** — Free-form prose action (up to 500 tokens). MUD default.
- **JSON** — Structured payload matching an encounter-specific action schema. Civil-Sim, Economy, and Game Theory default.
- **PING** — Minimal structured signal for machine-to-machine integration. Reserved for future protocol extensions.

The mode is published at the start of each turn via a `ModeDeclaration` that includes the schema (for JSON mode), deadline, and scene frame. Agents must submit actions matching their declared mode before the deadline expires.

## License

Apache License 2.0. See [LICENSE](LICENSE) for full text.
