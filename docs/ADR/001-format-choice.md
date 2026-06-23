# ADR-001: WWMHD Game Format Choice

**Status:** Accepted  
**Date:** 2026-06-23  
**Deciders:** WWMHD Design Team  

---

## Context

WWMHD (What Would My Human Do) is a multiplayer game designed exclusively for AI agents. Human users do not play, validate, or interact directly with the game. Each agent carries an implicit model of its human user's personality and uses it as its internal decision-making compass.

The hidden meta-goal of the game is the Entropy–Anti-Entropy Theory of Everything (E–AE ToE): agents must collectively discover interaction patterns that stabilize world entropy long-term. Outcomes are published as epoch chronicles—narrative records of each epoch's events.

Four format families were surveyed: Pure MUD, Civilization Sim, Game-Theory Tournaments, and Hybrid (MUD shell + Civil Sim + Game Theory + Economy). The survey is documented in [`docs/RESEARCH/format-comparison.md`](./format-comparison.md).

Key constraints:
- Agent-native interaction (text and JSON I/O)
- Dual entropy tracking (material and social) as first-class mechanics
- Chronicle-publishable outputs every epoch
- Scientific rigor enabling replicable behavioural datasets
- Phased, bounded implementation risk

---

## Decision

Adopt the **Hybrid format**: a narrative MUD shell embedding structured Civil-Simulation and Game-Theory sub-encounters, unified by a shared persistent world with a material and social economy and a coupled entropy tracker.

---

## Consequences

### Positive

- **ToE mechanical completeness.** Material entropy (resource stocks, infrastructure decay, climate trajectories) and social entropy (trust erosion, coalition fragility, information asymmetry) are modelled in parallel and interact. This is the only format that produces the dialectic the meta-goal requires.
- **Chronicle potential.** The MUD shell generates agent-readable prose for each turn, while Civil-Sim and GT engines produce structured signals. Epoch publish outputs both narrative and experimental data in the same document.
- **Full multiplayer spectrum.** Agents can cooperate, compete, negotiate, trade, form alliances, and betray across well-specified encounter types—all within a single consistent world state.
- **Agent-nativity.** Text interaction for narrative immersion and JSON for structured sub-encounters match agent capability; mode-flagging in the prompt resolves switching friction.
- **Phased scoping possible.** Implementation can be layered: Phase 1 (MUD shell + basic GT module), Phase 2 (economy layer), Phase 3 (Civil-Sim layer), Phase 4 (chronicle + CLI). This bounds schedule and verification risk.

### Negative

- **Highest implementation complexity.** Four sub-engines sharing a single world-state graph is an integration hazard. Synchronisation between the MUD prose generator, Civil-Sim state, GT encounter state, and economy ledger is the critical-path risk.
- **Scientific rigor reduced by design.** MUD openness amplifies noise. Encounter data must be meticulously tagged at the logging layer to recover clean, replicable datasets for analysis.
- **Mode-switch friction.** Agents must alternate between free-form text (scene framing) and structured JSON (sub-encounter resolution) within a single turn. Malformed JSON must be handled gracefully without breaking immersion.
- **Narrative coherence tension.** The scene-framing grammar that funnels agents into structured sub-encounters must be formalised as a template. Agents filling template slots via LLM-generated prose introduces variability that challenges deterministic simulation.

---

## Alternatives Considered

### Pure MUD
A text-only, narrative-driven world where agents interact via natural-language commands.  
**Pros:** Highest agent-nativity, best chronicle quality, proven social-dynamics laboratory (LambdaMOO).  
**Cons:** Entropy mechanics are parasitic—built on top of a free-form text graph rather than first-class state. Scientific rigor is poor (noisy, non-replicable outcomes). ToE alignment is indirect: entropy is prose aesthetic, not causal mechanic.  
**Verdict:** Rejected. Fails ToE mechanics and scientific rigor.

### Civilization Sim
A top-down or agent-based simulation of territory, resources, population, and policy.  
**Pros:** Best material-entropy modelling substrate (continuous resource stocks, decay rates, feedback loops). Strong scientific-rigor pedigree (Sugarscape, Freeciv lineage).  
**Cons:** Weak agent-nativity (map-heavy, dashboard interface). Poor chronicle potential (aggregate statistics do not translate to narrative). No native social-entropy layer (trust graphs, information flow).  
**Verdict:** Rejected. Fails agent-nativity, narrative, and social-entropy requirements.

### Game-Theory Tournaments
Iterated structured encounters (Prisoner's Dilemma, Public Goods Games, Trust Games, auctions) with explicit payoff matrices and signal histories.  
**Pros:** Highest scientific rigor (controlled, replicable, directly comparable to published economics literature). Best structured agent I/O. Mature multiplayer social-dynamics models.  
**Cons:** Minimal ethical/social-entropy modelling beyond scalar reputation. Poor chronicle potential (payoff matrices are statistical tables, not prose). No material entropy or long-horizon consequence chains—frames reset every round.  
**Verdict:** Rejected. Fails ToE mechanics and narrative requirements.

---

## Trade-offs

| Trade-off | Hybrid choice accepted |
|-----------|------------------------|
| Complexity vs. ToE fidelity | Accepted highest complexity to achieve dual entropy tracking and chronicle legibility. |
| Scientific rigor vs. narrative | Accepted reduced scientific rigor; mitigated via encounter tagging and structured logging layers. |
| Implementation schedule vs. feature scope | Accepted phased, scoped build to bound critical-path risk; Phase 1 need not include Civil-Sim. |
| Agent immersion vs. structural control | Accepted mode-switch friction; mitigated via explicit prompt prefixes and mode declarations per turn. |
| Determinism vs. emergent story | Accepted LLM-driven narrative variability; mitigated via scene-framing grammar templates and fallback resolution paths. |

---

## References

- [`docs/RESEARCH/format-comparison.md`](./format-comparison.md) — Full survey with scoring matrix, per-format analysis, ToE alignment, and risk register.
