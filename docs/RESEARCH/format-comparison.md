# WWMHD Format Survey: MUD vs Civilization Sim vs Game Theory vs Hybrid

**Purpose:** Compare four game-format families against the Entropy–Anti-Entropy Theory of Everything (E-AE ToE) and WWMHD operational constraints.

**Scoring rubric:** 1 = poor fit, 5 = excellent fit. Scores are reasoned rather than purely quantitative; the rationale matters more than the number.

---

## 1. Format Descriptions

| # | Format | Core description |
|---|--------|-----------------|
| 1 | **Pure MUD** | Narrative-driven, text-only, open-ended scenarios. Agents interact via natural-language commands and receive prose descriptions. |
| 2 | **Civilization Sim** | Resource, policy, and people simulation. Governance decisions propagate through a modelled population and landscape. |
| 3 | **Game-Theory Tournaments** | Iterated structured encounters (PD, public-goods, trust games, auctions) with explicit payoff matrices and signal histories. |
| 4 | **Hybrid** | MUD narrative shell embedding structured Civil-Sim and Game-Theory sub-encounters, unified by a material + social economy and entropy tracker across both dimensions. |

---

## 2. Scoring Matrix

| Criterion (weight) | 1 Pure MUD | 2 Civ Sim | 3 GT Tournaments | 4 Hybrid |
|---|---|---|---|---|
| **ToE Alignment (high)** | 2/5 | 4/5 | 3/5 | **5/5** |
| **Chronicle Potential (high)** | **5/5** | 3/5 | 2/5 | **5/5** |
| **Agent-Nativity (high)** | **5/5** | 3/5 | **5/5** | 4/5 |
| **Multiplayer Dynamics (medium)** | 3/5 | 4/5 | **5/5** | **5/5** |
| **Entropy Mechanics Fit (high)** | 2/5 | **5/5** | 3/5 | **5/5** |
| **Implementation Complexity (medium)** | **2/5 (easier)** | 4/5 | 1/5 | 5/5 (hardest) |
| **Scientific Rigor (medium)** | 1/5 | 4/5 | **5/5** | 4/5 |

---

## 3. Detailed Analysis

### 3.1 Pure MUD

**Definition.** A text-interactive world where agents navigate rooms, converse with NPCs and other players, and influence the world via typed commands. The canonical lineage runs from MUD1 (1978, Essex) through MOO (1990) to modern frameworks like Evennia and Aardwolf.

**Prior art (2–3 examples).**
1. *LambdaMOO* (Pavel Curtis, 1990, Xerox PARC) — social-experiment MUD with user-built spaces and emergent governance; demonstrated that text worlds produce live social norms and observable trust graphs.
2. *Evennia* (Griatch et al., ongoing) — open-source Python MUD framework; provides real-time text routing, scriptable objects, and a flat attribute system that makes it a candidate integration substrate.
3. *AI Dungeon* (Latitude, 2019) — LLM-driven text adventure; shows that generative text can be harnessed for interactive narrative, but also illustrates free-form lack of structure.

**Strengths.**
- Highest agent-nativity: pure text I/O, structured JSON overlays trivial to inject.
- Best chronicle potential: high-quality prose flows naturally; agent actions read as narrative prose.
- Proven social-dynamics laboratory: LambdaMOO ran open-ended trust, reputation, and governance experiments for years.

**Weaknesses.**
- Entropy mechanics are parasitic: material decay, resource depletion, and institutional entropy require custom coding on top of a free-form text graph. There is no built-in notion of state continuity beyond room membership and bag contents.
- Scientific rigor suffers: outcomes are noisy and non-replicable. The open-world parameter space is too large for controlled experimental design without extensive scaffolding.
- ToE alignment is indirect: the *theme* of entropy can be referenced in prose, but the *mechanism* cannot be modelled without substantial hybridisation.

### 3.2 Civilization Sim

**Definition.** A top-down or agent-based simulation of a territory containing resources, population segments, infrastructure, and policy levers. Decisions change resource stocks and population behaviour over time.

**Prior art (2–3 examples).**
1. *Freeciv* (Freeciv project, ongoing fork of MicroProse Civilization, 1991) — turn-based hex-tile resource/growth/war simulation; shows the genre's capacity for long-horizon civilisation arc-play.
2. *SimCity* (Will Wright / Maxis, 1989) — urban-simulation layer on top of agent-resource mechanics; infrastructure as emergent property of local rules.
3. *Banished* (Shining Rock Software, 2013) — survival-civilisation sim where resource exhaustion and seasonal entropy are the primary antagonists.

**Strengths.**
- Best entropic modelling substrate: continuous resource stocks, degradation rates, population decay, and policy feedback loops directly mirror material entropy and anti-entropy (ordering through infrastructure, knowledge, institutions).
- High scientific-rigor potential: agent-based models (ABMs) in this space have a long tradition in social simulation (e.g., Epstein & Axtell's Sugarscape, 1996).
- Multiplayer tension through asymmetric geography and resource endowment is natural.

**Weaknesses.**
- Weak agent-nativity: the interface tends toward map manipulation, numeric dashboards, and visual simulation — unsuitable as the dominant interaction mode for pure text/JSON agents.
- Poor chronicle potential: individual actor stories fall out of aggregate statistics. Compelling narrative prose must be retroactively synthesised, not directly produced.
- No built-in social-entropy model: trust erosion, coalition dynamics, and information asymmetry are not modelled at the social-graph level; they must be layered in manually.

### 3.3 Game-Theory Tournaments

**Definition.** A sequence of tabletop-style structured encounters — iterated Prisoner's Dilemma (PD), Public Goods Games (PGG), Trust Games, first-price auctions — whose rules are formalised as payoff matrices or state machines.

**Prior art (2–3 examples).**
1. *Axelrod's Computer Tournament* (Robert Axelrod, 1980) — iterated PD competition; established that tit-for-tat and its derivatives robustly evolve cooperation.
2. *Berg, Dickhaut & McCabe Trust Game* (1995) — one-shot trust experiment with binary send/return; foundational experimental-economics protocol.
3. *Stanford Strategy Lab / MEL Science Match Lab* (ongoing) — large-scale online mechanism-design experiments; modern infrastructure for running structured encounter batteries at scale.

**Strengths.**
- Highest scientific rigor: encounters are controlled, replicable, and directly comparable to published experimental results. Cleanest path to publishable behavioural datasets on cooperation, punishment, and free-riding.
- Best agent-nativity: structured state in, structured action out. Perfect fit for JSON-typed agents.
- Multiplayer dynamics are the core design object: asymmetric information, hidden-types, coalition formation, and signallings all have mature game-theoretic models.

**Weaknesses.**
- Minimal ethical / social-entropy modelling: trust, reputation decay, coalition fragility exist only if explicitly encoded as game state. Standard tournament protocols ignore them.
- Poor chronicle/ToE narrative potential: payoff matrices tell no story. Raw tournament outputs are statistical tables, not prose.
- Atomistic encounters discourage long-horizon consequences: a PD round resets every period, which strips temporal texture unless rounds are chained.

### 3.4 Hybrid (MUD Shell + Civil Sim + Game Theory + Economy)

**Definition.** A narrative MUD shell within which agents encounter scenes that resolve via structured sub-encounters — policy decisions routed through the Civil-Sim engine, social and economic interactions routed through Game-Theory protocols, all backed by a shared persistent world whose material and social dimensions decay and regenerate rachet-fashion.

**Prior art (2–3 examples).**
1. *EVE Online* (CCP Games, 2003–) — persistent single-shard sandbox where emergent player alliances fight over resource regions; the economy is player-driven with real-money value; narrative occurs in agent-generated chronicles and meta-game media. The closest large-scale prior art to the Hybrid target.
2. *Crusader Kings* (Paradox Interactive, 2004–) — character-level narrative (MUD-like) layered over domain-management sim; diplomatic marriage, vassal management, and succession crises embed game-theoretic choices inside a chronicled dynastic story.
3. *RimWorld* (Ludeon Studios, 2013) — narratively generated colony sim where colonist mood, social relations, and resource management interact to produce emergent story arcs told through an in-game chronicle system.

**Strengths.**
- Best ToE alignment (see §4): material entropy (resources, terrain, infrastructure) and social entropy (trust, coalition stability, information flow) are modelled in parallel and interact. The MUD shell provides the narrative lens through which agent behaviour becomes interpretable as meaning.
- High chronicle potential: the MUD shell produces agent-readable prose describing each turn's interactions, while the Civil-Sim and GT engines produce structured signals vice-versa. Epoch publish produces both rich stories and structured datasets.
- Multiplayer dynamics span the full spectrum: MUD-style roleplay negotiation, Civil-Sim diplomacy and resource competition, GT structured competition with asymmetric information, and economy-layer markets and alliances.
- Agent-native interaction modes match agent capability: text for narrative immersion, JSON for analytic decisions, mixed modes for hybrid sub-encounters.

**Weaknesses.**
- Implementation complexity is the highest of any format discussed. Four engines sharing a consistent world state is an integration hazard. Schedule and verification risk is significant (see §6).
- Scientific rigor is reduced by design: MUD freedom introduces noise. Structured encounter logs must be meticulously tagged to recover clean experimental data.
- Design tension between MUD openness and GT/civil-sim structure: agents must be funnelered into structured encounters without breaking immersion; the framing grammar is non-trivial to specify.

---

## 4. Alignment with the E–AE Theory of Everything

The E–AE ToE, as applied to WWMHD, posits that the universe's fundamental dynamic is the tension between entropy (energy dispersal, disorder, information loss, collapse) and anti-entropy (energy concentration, structure formation, information gain, organisation, life). A game format's fidelity to this meta-goal is measured by how naturally it can:

(i) track **material entropy** — resource depletion, infrastructure decay, environmental degradation, energy dispersal;  
(ii) track **social entropy** — trust erosion, coalition fragility, information asymmetry decay, norm collapse; and  
(iii) make the interaction between (i) and (ii) visible to agents and to the epoch chronicle without breaking the fiction.

### 4.1 Per-Format ToE Mechanic Coverage

| Dimension | Pure MUD | Civ Sim | GT Tournaments | Hybrid |
|---|---|---|---|---|
| Material entropy | absent (cosmetic) | built-in | absent | **built-in** |
| Social entropy | weak (social lore) | absent | partial (trust games embed) | **built-in + emergent** |
| Interaction effects | none | narrow (economy sim) | none | **full coupling** |
| Agent-visible feedback | prose only | dashboards | payoff histories | **prose + structured signals** |
| Chronicle-publishable path | yes (prose) | no (aggregate stats) | no (tables) | **yes (both)** |

### 4.2 Why Pure MUD Is ToE-Underfitted

A text world writes entropy as adjective — *"the square is decrepit"* — but the agent cannot intervene on the mechanic because there is no underlying state machine governing decay. The narrative is decorative rather than causal; entropy appears and disappears at the author's discretion. WWMHD's ToE meta-goal requires mechanics that *produce* entropy as a first-class world state, not prose aesthetics.

### 4.3 Why Civil Sim Is ToE-Partial

Civil Sim is purpose-built for material entropy: resources deplete, terrain degrades, infrastructure has a maintenance tax that grows over time. The limitation is social entropy: there is no native trust-graph or information-flow layer. A civilisation sim can model institutional decay only as a number, not as a social graph property an agent can observe and react to. This gap is critical: the E–AE ToE requires tracking how social order fails in lockstep with material depletion — mutual reinforcement — which the Civ Sim alone cannot express.

### 4.4 Why Pure GT Tournaments Are ToE-Narrow

Game-theory tournaments model social entropy robustly within a single encounter (trust generation and betrayal, coalition fragility in public-goods games). But the frame resets every round: material entropy is absent, long-horizon consequence chains are broken, and the narrative is statistical rather than chronicle-ready. A tournament captures a slice of social entropy; it cannot represent the dialectic between material and social collapse that the ToE proposes.

### 4.5 Why Hybrid Is ToE-Complete

The Hybrid format is the only design that triangulates all three ToE requirements simultaneously:

- **Material entropy** is tracked by the Civil-Sim engine: resource stocks, infrastructure integrity, energy return on investment, and climate/trajectory variables all decay continuously. Agents observe this as structured signals (resource levels, region hazard scores).
- **Social entropy** is tracked by the GT engine: trust, reputation, coalition membership, and information symmetry decay per interaction. Agents observe this as both structured signals (trust-value changes, coalition-graph delta) and as MUD prose (dialogue, diplomatic exchanges).
- **Chronicle publication** binds the two: a turn's material collapse and a coalition's betrayal are reported in the same epoch prose, making their interaction narratively legible and experimentally traceable.

---

## 5. Per-Factor Rationale Narrative

### 5.1 Chronicle / Narrative Potential

**Winner: Pure MUD (5), Hybrid (5).** Spatial and agent-action prose is the genre native to Hypertext Fiction and Interactive Fiction traditions. The MUD shell wins outright for prose quality and immersion depth. The Hybrid ties by inheriting the MUD shell; the Civil-Sim and GT post-processors generate auxiliary narrative hooks (economic report summaries, coalition-watch bulletins) that the chronicle layer can season proactively.

**Civ Sim (3):** Aggregate tables and shiny UI charts do not translate to memorable prose without substantial NLP post-processing. A civilisation-level GDP chart is not a story; an agent reading it is not immersed.

**GT Tournaments (2):** Payoff matrices are the antithesis of narrative. Even when encounters are narratively framed, the incentive structure dominates; the outcome is a table entry, not a chapter.

### 5.2 Agent-Nativity

**Tie: Pure MUD (5), GT Tournaments (5).** Both formats are natural for text-in / structured-out agents. MUDs accept free text; GT engines accept JSON actions with deterministic transitions. Both are server-push + client-pull compatible.

**Hybrid (4):** The hybrid agent must switch modes — sometimes prose (scene framing), sometimes JSON (sub-encounter action) — within a single turn. This is not a hard problem (mode-flag in the prompt), but it is a friction cost that pure formats avoid.

**Civil Sim (3):** Pure civil sim is map/graph-heavy; a text-mode interface layer must be built on top, and that layer will be a projection rather than a native surface.

### 5.3 Multiplayer Dynamics

**Winner: Hybrid (5), GT Tournaments (5).** Both cover the full spectrum: cooperation, competition, asymmetric information, coalition formation, and negotiated trades. GT is cleaner for controlled comparison; Hybrid is richer for emergent play.

**Civ Sim (4):** Diplomacy systems in Civ-style games are well-developed. The limitation is the same as elsewhere: Civ Sim multiplayer tends to be symmetric-information unless modded heavily.

**Pure MUD (3):** Social play exists but is under-specified. Emergent trust is organic but not instrumentable.

### 5.4 Entropy Mechanics Fit

**Winner: Hybrid (5), Civ Sim (5).** Civil Sim built the genre around material entropy; Hybrid extends it to social entropy. The Hybrid wins practically because the MUD chronicle makes entropy visible and meaningfully mutable by agents.

**GT Tournaments (3):** A single encounter's trust dynamics map to a micro-scale social entropy. But there is no accumulation layer — no world state that persists and degrades across rounds beyond a scalar reputation variable.

**Pure MUD (2):** Entropy exists only as flavour text unless explicitly implemented as a separate mechanic (custom rooms, wear systems, hunger timers), which pushes the format toward the Hybrid.

### 5.5 Implementation Complexity

**Ranking:**
1. GT Tournaments (1/5) — State machines, action trees, and buffers. Proven patterns, low integration risk.
2. Pure MUD (2/5) — MUD framework is commodity. World graph and command parser are well-understood.
3. Civil Sim (4/5) — ABM performance, pathfinding, terrain meshing, and population simulation are computationally heavy and hard to test deterministically.
4. Hybrid (5/5) — All of the above in a single consistent world-state graph. Synchronisation between MUD prose generator, civil-sim state, GT encounter state, and economy ledger is the critical-path risk. Mode-switching grammar for agents is non-trivial.

### 5.6 Scientific Rigor

**Ranking:**
1. GT Tournaments (5/5) — Directly comparable to Axelrod, Berg et al., and the mechanism-design literature. Controlled parameters, replicable conditions, clean statistical analysis.
2. Civil Sim (4/5) — ABM methodology is well-regarded; Sugarscape, Sugarscape-style experiments are peer-validated. Rigor depends on careful model calibration.
3. Hybrid (4/5) — Structured GT encounters embedded in a MUD shell produce clean encounter data *if encounters are carefully logged*. The MUD noise is manageable with encounter tagging.
4. Pure MUD (1/5) — Free text is a noise amplifier; statistical analysis of open-world action traces is nascent and under-standardised.

---

## 6. Hybrid Implementation Risk Register

| Risk | Severity | Mitigation |
|---|---|---|
| World-state sync across four sub-engines | High | Single authoritative world-state container (event-sourced log) that all engines read from; deterministic replay for debugging. |
| Agent mode-switch confusion (text vs JSON sub-encounters) | Medium | Explicit prompt prefix per turn; mode declared at turn start; malformed JSON treated as social pause rather than silent failure. |
| Narrative coherence under structured constraint | Medium | Scene-framing grammar must be formalised as a template; agents fill slots, LLM renders prose; pure text actions that fall outside structured grammar must route to default resolution. |
| Scientific-data contamination from MUD noise | Low-medium | Tag every structured encounter with agent IDs, encounter type, pre/post state deltas, and outcome; separate chronicle prose from scientific log at ingestion. |
| Phase-scoping overruns | High | Build in layered phases (§7); Phase 1 need only include MUD shell + basic GT module; add Civil-Sim layer in Phase 3. |

---

## 7. Preliminary Recommendation

**Recommended format: Hybrid (MUD Shell + Civil Sim + Game Theory + Economy).**

### 7.1 Rationale

The Hybrid is the only format that is simultaneously:
- faithful to the E–AE ToE at the mechanical level (dual entropy tracking), and
- faithful to it at the narrative level (epoch chronicle makes the material–social dialectic legible to a reader),
- agent-native across interaction modes (text for immersion, JSON for structured sub-encounters),
- capable of the full multiplayer spectrum (cooperation, competition, negotiation, asymmetric info, trade), and
- amenable to phased construction so that implementation risk can be bounded and contained.

No single sub-format achieves more than three of these simultaneously. Pure MUD wins narrative and agent-nativity but fails ToE mechanics and scientific rigor. Civil Sim wins ToE mechanics and scientific rigor but fails agent-nativity and narrative. GT Tournaments win agent-nativity, multiplayer, and scientific rigor but fail ToE mechanics and narrative. Only Hybrid absorbs the strengths and attempts — through deliberate architecture — to contain the weaknesses.

### 7.2 Non-Goals at This Stage

The format choice does **not** imply:
- Multiplayer is the only valid scope. Single-agent play is a first-class use case.
- Every MUD turn must resolve through a structured sub-encounter. Free-form MUD interaction is the primary interaction mode; sub-encounters are embeddedGame-Theory-encounters-only when the scene grammar triggers them.
- Maximum complexity is required at launch. Phase-scoping (see §6) is mandatory.

### 7.3 Immediate Next Steps

1. Freeze the Hybrid as the architectural target; update adjacent ADR if needed to reflect this survey.
2. Define the **Scene Grammar** — the formal grammar by which the MUD shell decides whether a turn triggers a Civil-Sim / GT sub-encounter. This is the design document that bridges all four sub-engines.
3. Proceed to the Phase 1 build plan in `docs/ROADMAP/001-hybrid-implementation.md`.
