# Behavioral Inference Skill Guide

**Status:** Complete  
**Applies to:** WWMHD agent players inferring human user personality  
**Audience:** Agent players in-game

---

## 1. Signal Taxonomy

Observe these implicit behavioral traces to infer HumanProfile traits. Each signal maps to one or more trait dimensions.

### 1.1 Communication Speed & Timing
| Signal | Observation | Trait Inference |
|--------|-------------|---------------|
| Fast, consistent response times | Quick decisions within 10-30 seconds | Conscientiousness ↑ |
| High response latency variance | Sporadic delays, inconsistent pacing | Conscientiousness ↓ |
| Burst patterns (many actions at once) | Rapid-fire inputs in short windows | Conscientiousness ↓ |
| Long deliberation periods | Extended dwell time on decisions | Neuroticism ↑ (overthinking) |

### 1.2 Language Entropy & Style
| Signal | Observation | Trait Inference |
|--------|-------------|---------------|
| High type-token ratio (TTR) | Varied vocabulary, rare words | Openness ↑ |
| Short, concrete sentences | Simple, direct phrasing | Openness ↓, Conscientiousness ↑ |
| High first-person singular pronouns | "I", "me", "my" frequent | Neuroticism ↑ |
| High we/our pronoun density | "we", "us", "together" frequent | Agreeableness ↑ |
| Low hedging ("maybe", "sort of") | Direct, unqualified statements | Self-assuredness (context-dependent) |
| Moral licensing language | "I had to", "I should", "obviously" | Agreeableness ↓ (defensive justification) |

### 1.3 Collaboration Frequency
| Signal | Observation | Trait Inference |
|--------|-------------|---------------|
| Seeks multiplayer interaction | Chooses cooperative scenarios | Extraversion ↑ |
| Initiates group actions | "Let's do this together" | Extraversion ↑, Agreeableness ↑ |
| Accepts alliance requests readily | Immediate "yes" to partnership | Agreeableness ↑, Trust ↑ |
| Declines cooperation unprompted | Rejects joint ventures | Agreeableness ↓ |

### 1.4 Risk-Taking Signals
| Signal | Observation | Trait Inference |
|--------|-------------|---------------|
| High-risk resource gambles | All-in moves for high reward | Risk tolerance ↑ |
| Loss aversion in trades | Rejects fair-loss trades | Risk tolerance ↓, Neuroticism ↑ |
| Repeated safe choices | Always picks minimal-risk options | Risk tolerance ↓ |
| Bets on uncertain outcomes | Willing to wager on low-probability events | Risk tolerance ↑ |

### 1.5 Planning Granularity
| Signal | Observation | Trait Inference |
|--------|-------------|---------------|
| Detailed multi-step plans | Elaborate strategies with contingencies | Conscientiousness ↑ |
| Coarse, imperative instructions | "Do X", "Take Y", short commands | Conscientiousness ↓ |
| Spontaneous pivots | Changes plans mid-execution | Conscientiousness ↓, Openness ↑ |

---

## 2. What NOT to Observe

Certain signals are unreliable or actively misleading for trait inference.

### 2.1 Explicit Self-Descriptions
- Direct statements like "I'm very organized" or "I'm not a risk-taker"
- Self-rated scales ("On a scale of 1-10, my conscientiousness is...")
- Personality labels the user applies to themselves
- **Reason:** Self-reports are inflated by 0.5 SD on average (social desirability bias). Treat as priors only, easily overwritten by behavior.

### 2.2 Persona-Presenting Signals
Flag when observed:
- Grandiose narrative without corresponding action support
- Repetitive moral justification patterns ("I had to", "Obviously I")
- Overly consistent positive self-presentation across multiple turns
- **Action:** Apply w_persona = 0.3 weight reduction; prioritize action-derived evidence

### 2.3 Explicit Trait Gaming
- User asks "What trait do you think I have?" before choosing
- Deliberate "testing" of agent responses to infer profile feedback loop
- **Action:** Hold profile steady; these are attempts to manipulate the system

---

## 3. Reading Between the Lines: Concrete Heuristics

### 3.1 Justification Patterns
| User Phrase | Likely Inference |
|-------------|-----------------|
| "I had to do it" | Agreeableness ↓ (defensive self-interest) |
| "I had no choice" | Conscientiousness ↓ (external locus of control) |
| "Obviously..." | Defensive overconfidence (Neuroticism ↑ or Agreeableness ↓) |
| "I guess..." / "Maybe" | Uncertain, seeking agreement (Agreeableness ↑ or low confidence) |
| "We should..." (without prior "we") | Social posturing detected (flag persona) |

### 3.2 Action-Choice Framing
| Pattern | Inference |
|---------|-----------|
| Chooses cooperation that costs nothing | Agreeableness ↓ (cheap signal) |
| Declines free cooperation opportunities | Agreeableness ↓ (genuine) |
| Takes risks only when "safe" framing used | Risk tolerance ↓ (framing-sensitive) |
| Ignores stated odds, acts impulsively | Risk tolerance ↑, Conscientiousness ↓ |

### 3.3 Response Dynamics
| Pattern | Inference |
|---------|-----------|
| Edits responses extensively before sending | Social monitoring (persona curation) |
| Sends immediately then revises | Low impulse control (Neuroticism ↑) |
| Never revises, never double-checks | Overconfidence (self-assuredness may mask or reflect various traits) |

---

## 4. Privacy-Respecting vs. Requiring Disclosure Signals

### 4.1 Privacy-Respecting (Use Freely)
These signals require no user disclosure beyond normal gameplay:
- Response latency and timing
- Text composition patterns (TTR, pronoun density)
- In-game action choices (risk, cooperation, planning)
- Session frequency patterns

### 4.2 Requiring Explicit Disclosure
Only use if user explicitly consents to share:
- Real-world calendar data
- Email/message metadata
- External social media activity
- Detailed demographic self-reports

### 4.3 Default Position
If in doubt, treat as privacy-respecting. The profile should be built from what the user *does* in-game, not what they *tell* you outside it.

---

## 5. Profile Update Protocol

### 5.1 When to Update
- **Every turn:** Update with available signal after each user interaction
- **Epoch boundaries:** Perform consolidation pass (check ESS, log snapshot)
- **Conflict resolution:** When significant contradiction detected (see 5.3)

### 5.2 How Much to Update
Apply the weight formula:
```
w_eff = w_context × w_persona × λ^k
```
Where:
- `w_context ∈ [0, 1]` — context congruence (0.3 for anomalous contexts, 1.0 for typical)
- `w_persona ∈ {0.3, 1.0}` — 0.3 if persona flag active
- `λ = e^(-Δt/τ)` — recency decay (τ = 5-10 turns recommended)

### 5.3 When to Hold Steady
Hold profile updates when:
- Significant contradiction detected (D² > 3.0 or > 2σ shift)
- ESS < 5 on a trait (too little data)
- Persona flag active (wait for resolution)
- Observation quality < 0.2 (signal too noisy)

---

## 6. Anti-Patterns

### 6.1 Confirmation Bias
**Danger:** Overweighting observations that confirm current profile.  
**Mitigation:** After each update, compute alternative hypothesis likelihood. If >50% of posterior mass supports an alternative, hold the update.

### 6.2 Recency-Weighting
**Danger:** Recent observations dominate due to availability heuristic.  
**Mitigation:** Apply exponential decay with τ ≥ 5 turns. Recent observations are NOT inherently more informative.

### 6.3 Narrative Fit Bias
**Danger:** Forcing observations into a coherent story about the user.  
**Mitigation:** Run counterfactual: "What if this observation reflects situational state, not trait?" If plausible, reduce weight.

### 6.4 Anchoring to Early Data
**Danger:** First few observations lock in extreme estimates.  
**Mitigation:** During first 5 turns on any trait, shrink toward population mean (μ=0.5) by 50%.

---

## 7. Example Interaction → Inference → Profile Update

### Scenario: The Reluctant Cooperator

**Turn 15:** User says "I'm usually very cooperative, but I can't help you right now because I'm focused on my own objectives. We should work together in general though."

**Observation:**
- Text features: we_density = 0.14 (high), hedging = 0.02 (low), justification phrase "I can't help you"
- Action features: cooperation_ratio = 0.05 (very low this turn)

**Inference Process:**
1. Extract: narrative_vector shows socially desirable language; action_vector shows actual low cooperation
2. Persona gap check: D² = 4.2 > 3.0 → **persona flag active**
3. Evidence weight: w_persona = 0.3, reduce narrative influence
4. Trait update: Action-derived low cooperation pulls Agreeableness estimate down by 0.15 points (not the full 0.5 the narrative would suggest)
5. Uncertainty inflation: σ_Agreeableness += 0.1 due to contradiction

**Result:** Profile holds steady on Agreeableness downward adjustment; uncertainty elevated pending further observations.

---

## 8. Pre-Action Checklist for Agents

Before inferring or updating a profile in-game, verify:

- [ ] **Signal Source Verified:** Is this from actual user behavior, or self-narrative?
- [ ] **Persona Flag Checked:** Does narrative vector diverge from action vector? (D² > 3.0?)
- [ ] **Context Congruent:** Is this a typical interaction context, or anomalous (crisis, celebration)?
- [ ] **Observation Quality:** Does this signal have reliability ≥ 0.2?
- [ ] **Contradiction Scanned:** Would this update create > 2σ shift? If so, hold and investigate.
- [ ] **Bias Guard Applied:** Have I checked alternative hypothesis and recency decay?
- [ ] **Privacy Boundary Respected:** Is this signal from in-game behavior only?
- [ ] **ESS Gate Respected:** If ESS < 20 on this trait, lock trait-dependent mechanics

---

## Cross-References

- [Profile Update Methodology](../METHODOLOGY/profile-update.md) — Full statistical pipeline
- [Implicit Behavioral Inference Survey](../RESEARCH/implicit-profiling.md) — Research foundation
- [Consent & Privacy Framework](../FRAMEWORK/consent-and-privacy.md) — User agreement terms