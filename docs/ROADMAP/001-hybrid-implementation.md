# WWMHD Hybrid Implementation Roadmap

**Version:** 1.0  
**Date:** 2026-06-23  
**Status:** Draft  
**Branch Strategy:** See §4

---

## 1. Prototype Audit: What We Learned

The existing `src/` codebase is a disposable MUD-only prototype. It taught us three things:

### 1.1 Design Concepts That Proved Right

- **Action-based architecture works**: The `Action` → `Scenario` → `resolve` pattern provided clean separation of concerns. However, action types were too limited (only 8 types) and lacked the structured JSON schema required for Civil-Sim and GT encounters.

- **Human profile inference is viable**: The `HumanProfile` model with `BigFive`, `CognitiveBiases`, and `SocialStyle` dimensions correctly anticipates the five inference dimensions specified in PRD §4.2 (risk tolerance, cooperation propensity, trust slowness, social orientation, resource conservatism). However, the profile was stored server-side, violating REQ-009.

- **Chronicle-writable outputs are achievable**: The `ChronicleWriter` demonstrated dual-part publication (markdown + JSON). However, it lacked atomic publication (REQ-024), immutable versioning (REQ-027), and proper epoch seeding (REQ-028).

### 1.2 Design Concepts That Proved Wrong

- **Scalar entropy is insufficient**: The prototype used a single `entropy: float = 0.0` scalar. The PRD requires dual entropy vectors (Material and Social) with multiple components each. This is a fundamental architectural change, not an iteration.

- **No mode-switching mechanism**: The prototype treated all actions as free-form text. The PRD requires explicit mode declaration (REQ-005), JSON schema publishing (REQ-015), and graceful malformed-JSON handling (REQ-006).

- **Missing epoch lifecycle**: The prototype had no concept of epochs, turns, or deterministic scheduling. The PRD requires a seven-phase loop (REQ-001), epoch boundaries, and chronicle-to-chronicle state seeding (REQ-028).

- **No scene grammar**: Random scenario generation cannot implement the deterministic Scene Grammar required (REQ-014). The grammar must map world state to scenario type.

- **Incomplete world model**: The prototype world model lacked resources, infrastructure, climate, trust graphs, coalitions, and information asymmetry—all core to the hybrid entropy mechanics.

### 1.3 What to Preserve vs Discard

| Prototype Element | Preserve | Discard |
|-------------------|----------|---------|
| Pydantic models for structured data | ✅ Core pattern | ❌ Current model structure |
| Action/Scenario/Resolution flow | ✅ Conceptual skeleton | ❌ Current implementation |
| Chronicle write pattern | ✅ Output pattern | ❌ Current format |
| HumanProfile dimensions | ✅ Dimensions are correct | ❌ Server-side storage design |
| `entropy: float` | ❌ Too simplistic | ✅ Replace with dual-vector system |

---

## 2. Hybrid System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI / Agent I/O                        │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────────┐  │
│  │   MUD Mode  │  │   JSON Mode │  │ Structured Signals    │  │
│  │   (text)    │  │   (+schema) │  │   (real-time)         │  │
│  └─────────────┘  └─────────────┘  └───────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    Scenario Engine                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Scene Grammar: WorldState → ScenarioType + Schema         │  │
│  └───────────────────────────────────────────────────────────┘  │
│           │                │                 │                 │
│           ▼                ▼                 ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│
│  │  Free-Form  │  │  Civil-Sim  │  │  GT Engine  │  │Economy  ││
│  │    MUD      │  │   Module    │  │   Module    │  │ Module  ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘│
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    World State Manager                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Persistent state: resources, infrastructure, climate,     │  │
│  │ trust_graph, coalitions, information_asymmetry            │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    Entropy Engine                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Material Entropy (M𝓔): R𝓔 + I𝓔 + C𝓔 (w_R=0.4, w_I=0.35, w_C=0.25)│  │
│  │ Social Entropy (S𝓔): T𝓔 + K𝓔 + A𝓔 (w_T=0.3, w_K=0.3, w_A=0.4)│  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    Chronicle Service                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Atomic publish: Part A (Markdown narrative) +           │  │
│  │ Part B (JSON world-state + entropy + turn log)          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Data Flow:** Epoch Init → Scene Grammar → Scenario Engine → (MUD/Civil-Sim/GT/Economy) → Interaction Resolution → Entropy Update → Chronicle Publish

---

## 3. Phased Build Plan

### Phase 1: Core World + Scenario Engine

**Goal:** Implement the foundational world state, seven-phase loop, and MUD narrative shell with basic GT encounters.

| Component | Requirements |
|-----------|--------------|
| World State | Epoch/turn tracking, agent registry, basic resources (water, grain) |
| Scenario Engine | Scene Grammar deterministic classifier (MUD/GT only) |
| MUD Shell | Text mode scene framing, free-form action acceptance |
| GT Module | Prisoner's Dilemma, Trust Game, Public Goods Game state machines |
| Entropy Engine | Dual entropy vectors (M𝓔, S𝓔) with basic formula implementation |
| Chronicle Service | Atomic Part A + Part B publication per epoch |
| CLI | Agent connection, turn polling, action submission |

**Concrete Beads:**

1. **`world-state-model`** (Bead): Define `WorldState`, `MaterialEntropy`, `SocialEntropy` Pydantic models per PRD §6. Include resources (stocks), infrastructure (integrity), climate (trajectory), trust graph, coalition list, information asymmetry.

2. **`epoch-scheduler`** (Bead): Implement deterministic epoch progression (REQ-002), seven-phase loop (REQ-001), default social-pause action for missing agents (REQ-004).

3. **`scene-grammar`** (Bead): Define deterministic grammar that classifies turns into MUD or GT based on world state. Publish mode declaration + schema for JSON turns (REQ-005, REQ-014).

4. **`gt-encounters`** (Bead): Implement PD, Trust, and PGG encounters with payoff matrices, round tracking, trust updates (REQ-018-022).

5. **`entropy-engine`** (Bead): Implement M𝓔 and S𝓔 formulas (REQ-019-020), update on resolution (REQ-021), anti-entropy actions (REQ-022).

6. **`chronicle-service`** (Bead): Atomic publication (REQ-024), immutable versioning (REQ-027), epoch seeding (REQ-028).

7. **`cli-interface`** (Bead): Agent I/O with mode declarations, JSON schema validation, structured signals (REQ-005-008).

**Convoy Scope:** Phase 1 convoy delivers playable epochs with MUD narrative + GT sub-encounters, producing chronicle-writable output.

---

### Phase 2: Game-Theory Module (Advanced)

**Goal:** Expand GT module with iterated encounters, coalition mechanics, and ToE detection foundation.

| Component | Requirements |
|-----------|--------------|
| Iterated GT | Multi-round encounters with payoff history |
| Coalition State Machine | Probe → Pact → Fracture → Reformation (REQ-031-033) |
| Trust Graph | Full agent-to-agent trust tracking, decay |
| Information Asymmetry | Private signals per agent, asymmetry metric |
| ToE Detector | Rolling horizon monitor (REQ-034), action-trace clustering (REQ-035) |

**Concrete Beads:**

1. **`iterated-gt-rounds`** (Bead): Multi-round encounter infrastructure, history tracking.

2. **`coalition-engine`** (Bead): State machine implementation, pact enforcement, fracture detection.

3. **`trust-graph-service`** (Bead): Trust matrix updates, decay functions, graph density computation.

4. **`toe-detector`** (Bead): H=50 horizon accumulation, stabilisation detection.

**Convoy Scope:** Phase 2 convoy delivers coalition-forming gameplay ready for ToE discovery.

---

### Phase 3: Economy Module

**Goal:** Implement resource trading, market mechanics, and economic entropy coupling.

| Component | Requirements |
|-----------|--------------|
| Economy Engine | Order-book resolution, margin checks, price discovery |
| Markets | Grain futures, infrastructure bonds, resource exchanges |
| Trading Actions | Bid, ask, trade, invest JSON schemas |
| Economic Signals | Price updates, liquidity metrics (REQ-007) |

**Concrete Beads:**

1. **`economy-ledger`** (Bead): Double-entry ledger, order book, transaction settlement.

2. **`market-exchanges`** (Bead): Grain futures, infrastructure bonds markets.

3. **`trading-actions`** (Bead): JSON action schemas for bid/ask/trade/invest.

**Convoy Scope:** Phase 3 convoy delivers trading mechanics and economic entropy coupling.

---

### Phase 4: Civil-Sim Layer + CLI Polish

**Goal:** Implement policy/resource allocation decisions and production-ready CLI.

| Component | Requirements |
|-----------|--------------|
| Civil-Sim Engine | Resource allocation, policy outcomes, forecasting |
| Regions | Geographic partitioning, local resource stocks |
| Policy Actions | Water allocation, emission treaties, infrastructure spending |
| CLI | Full turn sequence, replay, chronicle fetch |

**Concrete Beads:**

1. **`civil-sim-engine`** (Bead): Resource allocation resolution, policy outcome simulation.

2. **`region-model`** (Bead): Geographic regions with resource/infrastructure traits.

3. **`policy-actions`** (Bead): JSON schemas for civil-sim actions.

4. **`cli-final`** (Bead): Complete CLI with replay, chronicle fetch, multi-epoch simulation.

**Convoy Scope:** Phase 4 convoy delivers complete civil-sim integration and production CLI.

---

## 4. Branch Strategy

1. **Start fresh**: `git checkout -b feature/hybrid-phase-1 main` (discard prototype tree)

2. **Phase branches**: Each phase gets its own branch off the previous phase:
   - `feature/hybrid-phase-1` (core world + scenario)
   - `feature/hybrid-phase-2` (GT module)
   - `feature/hybrid-phase-3` (economy layer)
   - `feature/hybrid-phase-4` (civil-sim + CLI)

3. **No merges from prototype**: The `src/` tree is explicitly discarded. All new code goes in `src/` under the new architecture.

4. **Each bead**: Single focused commit, pushed immediately. Branch per bead if >1 day scope.

---

## 5. Risk Register

| Risk ID | Risk | Likelihood | Impact | Mitigation |
|---------|------|------------|--------|------------|
| R1 | World-state synchronisation across four sub-engines | High | Showstopper | Single authoritative `WorldState` container; event-sourced log; deterministic replay for debugging |
| R2 | Agent mode-switch confusion (text vs JSON) | Medium | Friction | Explicit prompt prefix per turn; mode declared at turn start; malformed JSON → social pause (REQ-006) |
| R3 | Narrative coherence under structured constraint | Medium | Quality | Scene-framing grammar as template; agents fill slots; pure text actions route to default resolution |
| R4 | Scientific-data contamination from MUD noise | Low | Validity | Tag every structured encounter with type, pre/post state; separate chronicle prose from scientific log |
| R5 | Phase-scoping overruns | High | Schedule | Phase gates: Phase 1 must pass integration test before Phase 2 starts; 2-week phase budgets |
| R6 | Entropy formula non-reproducibility | Medium | Trust | Deterministic formulas; seed-reproducible scenarios; all inputs logged per turn |
| R7 | Coalition state-machine edge cases | Medium | Correctness | Finite-state model; explicit transition tests; fracture cooldown configurable |

---

## 6. Dependencies & Interfaces

| Module | Provides | Consumes |
|--------|----------|----------|
| `world-state` | `WorldState`, entropy vectors | Agent actions, encounter resolutions |
| `scenario-engine` | Mode flag, JSON schema | WorldState |
| `gt-module` | Trust updates, coalition state | WorldState trust_graph |
| `economy-module` | Ledger deltas, price signals | WorldState resources |
| `civil-sim-module` | Resource/infrastructure deltas | WorldState resources + infrastructure |
| `entropy-engine` | M𝓔, S𝓔 updates | All module deltas |
| `chronicle-service` | Published chronicles | Resolved epoch state |
| `cli` | Agent I/O interface | All modules via Scenario Engine |

---

## 7. Acceptance Criteria

**Phase 1 Gate:**
- Epochs progress deterministically (REQ-002)
- Each turn produces mode declaration + schema (REQ-005, REQ-015)
- M𝓔 and S𝓔 computed and logged (REQ-018-021)
- Chronicle published atomically at epoch end (REQ-024-025)
- Integration test: 3 agents, 5 epochs, produces valid chronicle with entropy trajectory

**Phase 2 Gate:**
- Coalition pact/fracture mechanics working (REQ-031-033)
- Trust graph density affects entropy (REQ-019-020)
- ToE detector can identify stabilisation patterns (REQ-034-035)

**Phase 3 Gate:**
- Trade executes, margins checked (Economy engine)
- Economic signals deliver asynchronously (REQ-007)
- Market prices affect resource entropy

**Phase 4 Gate:**
- Civil-Sim policy actions resolve correctly
- CLI supports full epoch simulation
- 7-phase loop verified end-to-end

---