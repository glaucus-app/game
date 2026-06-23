# Profile Update Methodology: Bayesian Behavioral Inference

**Status:** Complete  
**Applies to:** WWMHD agent-implemented implicit human profiling  
**Cross-reference:** [Implicit Behavioral Inference Literature Survey](../RESEARCH/implicit-profiling.md) (for signal inventory, persona detection, and bias mitigations)  

---

## 1. Overview

Every WWMHD agent maintains a private, per-human profile — a vector of five Big Five / OCEAN trait estimates, each carried with an associated uncertainty. This profile is the agent's working model of its human user's personality, built exclusively from observed behavioral traces rather than self-reported descriptions.

The profile is:

- **Incremental:** updated observation by observation
- **Confidence-aware:** every trait has an uncertainty score in [0, 1]
- **Bayesian:** updates follow Bayes' rule with a formal prior → evidence → posterior construction
- **Adversarially hardened:** detects and down-weights gaming attempts
- **Drift-competent:** separates trait-level signal from transient contextual noise

This document specifies the complete observation→inference pipeline, statistical update mechanics, drift handling, cadence policy, worked examples, and adversarial robustness measures.

---

## 2. Observation → Inference Pipeline

### 2.1 Pipeline Stages

```
Raw Trace
  │
  ├─▶ Feature Extraction (structured features from raw data)
  │       e.g.: text → TTR, pronoun density, hedging rate
  │       e.g.: UI event log → response latency, burst rate, dwell time
  │       e.g.: in-game choice → risk quantile, cooperation index
  │
  ├─▶ Trait Tagging (map features → targeted trait dimensions)
  │       e.g.: high TTR + short concrete sentences → Openness signal
  │       e.g.: low response latency variance + burst patterns → Conscientiousness ↓
  │
  ├─▶ Evidence Weighting (assign reliability weight to this observation)
  │       Factors: source reliability, signal quality, persona-presentation flag,
  │       recency decay, observation context congruence
  │
  └─▶ Bayesian Update (merge into running profile posterior)
          P(trait | trace_{1:t}) ∝ P(trace_{1:t} | trait) · P_0(trait)
```

### 2.2 Stage 1: Feature Extraction

Scoped to signals the agent can instrumentalize without external instrumentation (survey §1):

| Raw Trace Type | Extracted Features | Targeted Traits |
|---|---|---|
| Agent's natural-language input from the human | Type-token ratio, first-person singular density, we/our density, hedging rate | Openness, Neuroticism, Agreeableness |
| UI timing (turn-open to turn-submit) | Mean latency, latency variance, burst index, dwell time | Conscientiousness, Neuroticism |
| In-game action choices | Risk quantile, loss-aversion delta, cooperation index, planning granularity | Risk, Conscientiousness, Agreeableness |
| Multiplayer interaction logs | Agent-initiated vs. system-initiated action ratio, co-operation frequency | Extraversion |

A full feature extraction specification follows from the signal inventory in the [Implicit Behavioral Inference Literature Survey §5](../RESEARCH/implicit-profiling.md#5-signal-inventory).

### 2.3 Stage 2: Trait Tagging

Each extracted feature maps to one or more trait dimensions via a fixed sensitivity matrix `S`, where each row is a feature and each column is a trait:

```
S[feature_f, trait_t] ∈ [-1, 1]
```

Positive values indicate the feature increases the trait estimate; negative values decrease it. Values near zero mean the feature carries minimal information for that trait.

Example sensitivity rows (initialized from survey evidence, tuned empirically):

| Feature | O | C | E | A | N |
|---|---|---|---|---|---|
| Type-token ratio (TTR) | +0.65 | 0 | 0 | 0 | 0 |
| First-person singular density | 0 | 0 | 0 | 0 | +0.45 |
| Response latency variance | 0 | −0.40 | 0 | 0 | +0.35 |
| Risk quantile (in-game) | 0 | 0 | 0 | 0 | −0.25 (Risk) |
| Cooperation index | 0 | 0 | +0.20 | +0.55 | 0 |

The sensitivity matrix is a hyperparameter of the profile system, grounded empirically in the survey (§3, §5) and calibrated on observed-outcome tracks.

### 2.4 Stage 3: Evidence Weighting

The raw weight `w_raw` from a single observation is computed as:

```
w_raw = w_context × w_persona × w_quality
```

Where:

- `w_context ∈ [0, 1]` — congruence of the observation context with a "typical" interaction. Highly atypical contexts (crisis, celebration) are down-weighted because they invoke trait-irrelevant state variance.
- `w_persona ∈ {0.3, 1.0}` — 0.3 if the observation triggers a persona-presentation flag (§6 below), 1.0 otherwise.
- `w_quality ∈ [0, 1]` — signal reliability of the specific feature extraction (from inventory reliabilities in survey §5; low-word-count samples reduce quality).

The effective evidence weight `w_eff` also incorporates recency decay:

```
w_eff = w_raw × λ^k
```

Where `k` is the number of turns since the observation and `λ = e^(-Δt/τ)` with time constant `τ` (§4 discusses cadence; §3.3 recommends τ ≈ 5–10 turns for the rolling window).

### 2.5 Stage 4: Bayesian Update

Each trait estimate `t ∈ [0, 1]` is accompanied by an uncertainty `σ_t ∈ [0, 1]`. The update is described in full in §3.

---

## 3. Statistical Update Rule

### 3.1 Prior

At profile initialization (cold start, no observations), each trait draws from a population-level Beta prior with parameters matched to normative OCEAN distributions:

```
trait_prior ~ Beta(α = μ·κ, β = (1−μ)·κ)
```

where:
- `μ = 0.5` (population midpoint on the [0,1] scale)
- `κ = 10` (effective prior sample size; larger κ = more conservative prior)

This is equivalent to a prior "sample" of κ=10 observations all at the mean. It encodes weak central tendency: new profiles start moderate and update rapidly toward observed evidence.

**Cross-reference:** The survey (§4.3) recommends population-level priors with μ=50, σ=10 on T-score scale; the Beta formulation above is the [0,1] analog.

### 3.2 Likelihood

Each observation produces a direction and magnitude `x ∈ [-1, 1]` for each trait, derived from the sensitivity-weighted feature vector:

```
x_t = Σ_f S[f, t] × normalized_feature(f) × w_eff
```

The observation is modeled as a noisy draw from a trait-true-value likelihood:

```
P(x | t) ~ N(t, σ_x²)
```

where `σ_x² = 1 − |x|` (higher-magnitude observations are more reliable; near-zero observations carry near-maximum noise).

### 3.3 Update Rule (Conjugate Normal Approximation)

Using a Normal approximation for computational efficiency (the posterior remains approximately Normal for moderate κ and observation counts):

```
posterior_precision = prior_precision + observation_precision
posterior_precision = κ + |x| / σ_x²     // prior precision = κ / μ_precision

μ_post = (prior_μ × prior_weight + x × obs_weight) / (prior_weight + obs_weight)
σ_post² = 1 / (prior_weight + obs_weight)

where:
  prior_weight = κ                              // effective "pseudo-count" of the prior
  obs_weight   = |x| / σ_x²                     // effective "count" contributed by this observation
```

In explicit Beta-binomial conjugate form (preferred for interpretability when sample counts are small):

```
α_post = α_prior + Σ w_eff × positive_evidence
β_post = β_prior + Σ w_eff × negative_evidence
μ_post  = α_post / (α_post + β_post)
σ_post² = (α_post × β_post) / ((α_post + β_post)² × (α_post + β_post + 1))
```

Where `positive_evidence = max(x, 0)` and `negative_evidence = max(−x, 0)` for each observation.

### 3.4 Pseudocode

```python
class TraitEstimate:
    alpha: float    # Beta prior/posterior parameter (positive signal count)
    beta: float     # Beta prior/posterior parameter (negative signal count)

    @property
    def mu(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def confidence(self) -> float:
        total = self.alpha + self.beta
        return 1.0 - (self.alpha * self.beta) / (total ** 2 * (total + 1))

    def update(self, evidence: float, weight: float) -> None:
        alpha_inc = max(evidence * weight, 0)
        beta_inc   = max(-evidence * weight, 0)
        self.alpha += alpha_inc
        self.beta  += beta_inc


def update_profile(
    profile: TraitEstimate,        # current per-trait estimate
    features: dict[str, float],    # extracted features this turn
    sensitivity: dict[str, float], # S[feature, trait] weights
    weight: float,                 # combined w_raw × recency for this observation
) -> TraitEstimate:
    x = sum(sensitivity[f] * features[f] for f in features)
    profile.update(evidence=x, weight=weight)
    return profile
```

---

## 4. Drift vs. Signal

### 4.1 The Problem

Personality is simultaneously:

- **Stable** at the level of rank-order: a person's relative position on Openness compared to peers persists across years (test-retest r ≈ 0.50–0.70 over 10 years; survey §4.2).
- **Variable** at the state level: short-term contextual factors (mood, stress, novelty of situation) can produce trait-irrelevant variance that exceeds true trait variance in brief windows.

If the agent treats every observation as equally indicative of the true trait estimate, transient state variance will produce jittery, unstable profiles.

### 4.2 Exponential Decay with Time Constant

The agent places observations on an exponential decay curve with time constant `τ` (measured in turns or wall-clock hours):

```
weight_t(t) = exp(−Δt / τ) / Σ_{k=1}^{K} exp(−Δt_k / τ)
```

Recommended `τ` values:

| Context | τ (turns) | Rationale |
|---|---|---|
| Casual multiplayer | 10 | sufficient interactions accumulate; personality stability dominates |
| High-stakes single-player | 5 | faster decay because mood-state variance is higher in asymmetric scenarios |
| Post-contradiction | 3 | shorter τ to accelerate resolution when competing evidence bodies conflict (§5) |

**Normalization:** the denominator sums across all stored observations in the rolling window so that weights always sum to 1.0 across the active evidence set.

### 4.3 Rolling Window vs. All-of-History

Three cadence policies are candidates:

| Policy | Description | When Appropriate |
|---|---|---|
| **Every-interaction** | update after every observation, decay over all-of-history | Default; simple; stable for agents with frequent turns |
| **Rolling window** | retain and decay only the last W turns | Preferred when interaction frequency varies widely across users |
| **Batch per epoch** | accumulate observations during epoch, single update at epoch end | Useful when the game's epoch structure provides natural segmentation |

**Recommendation:** Default to **every-interaction with exponential decay over a rolling window of the most recent 50 observations**. If fewer than 50 observations exist in history, decay runs over all available observations. This approach:

- Provides stable estimates without erasing long-term trait signal (τ preserves signal from the distant past at reduced weight rather than hard cutoff)
- Limits memory pressure (bounded window)
- Respects the survey finding (survey §4.2) that contextual contamination dominates at short windows — by applying exponential decay rather than equal-weight moving average, the agent inherently discounts state variance

### 4.4 Minimum Observation Threshold

Before a profile becomes "usable," the agent requires:

- At least 5 observations per trait (not necessarily each turn addresses all traits)
- Prior effective posterior sample size (ESS = α + β) ≥ κ + 2·5 = 20 on each trait

This prevents premature strong conclusions from one or two noisy observations (anchoring hazard, survey §7.3).

---

## 5. Contradictory Evidence Handling

### 5.1 Detection

Contradiction arises when a new observation pulls the posterior in a direction that opposes the current estimate. Quantify it as:

```
contradiction_strength = |x_post − μ_current| / σ_current
```

A contradiction is **significant** if `contradiction_strength > 2.0` (roughly 2σ update in a single step). Below 2.0, the update is consistent with expected sampling variance and no special handling is needed.

### 5.2 Response Protocol for Significant Contradiction

When significant contradiction is detected:

```
Priority 1: Check for context mismatch
  Is the observation temporally or situationally anomalous?
  → Check w_context; if w_context < 0.3, treat as contextual noise;
    apply a one-turn "hold signal" before incorporating.

Priority 2: Check for persona-presentation flag
  → If flag is active, contradiction is likely staged; apply w_persona = 0.3
    and re-weight; if contradiction still persists after re-weighting,
    treat as genuine.

Priority 3: Apply conflict-adjusted update
  → Increase σ_post for the affected trait by +0.15 (temporary uncertainty inflation)
    reflecting unresolved conflict in the evidence base.
  → Log the contradiction in the profile journal with (timestamp, context, x, μ_before, σ_before).

Priority 4: Re-evaluate after next observation
  → If the following observation resolves in the same direction as the
    contradiction, treat as genuine trait-level signal (long-term change).
    If it resolves back, treat as contextual noise and restore uncertainty to
    pre-contradiction level.
```

### 5.3 Contradiction Metrics

The agent tracks per-trait contradiction rate (fraction of observations that exceed 2σ):

- Low rate (< 5%): profile is stable and reliable
- Moderate rate (5%–15%): profile is still stabilizing; expected early-on
- High rate (> 15%): likely signal quality problem, active gaming, or persona dynamics — agent should invoke active learning probes targeting this trait

---

## 6. Persona-Presentation Detection

### 6.1 Threat

Persona-presentation is the principal adversarial vector against implicit profiling: users (consciously or unconsciously) stage behavior that reflects an idealized self-narrative rather than their typical disposition. Left undetected, it inflates trait estimates in socially desirable directions — particularly Agreeableness and Conscientiousness (survey §2.2, §6.1).

(Survey §2.2 reports self-presentation inflates Agreeableness and Conscientiousness by ~0.5 SD on average.)

### 6.2 Detection Procedure

The agent runs the persona gap detector on each observation batch:

```
1. Construct narrative_vector from text features:
   narrative_vector = [ TTR, FPS_pronoun_density, we_density, hedging_rate,
                       self-reference_rate, superlative_rate ]

2. Construct action_vector from action features:
   action_vector = [ choice_entropy, risk_quantile, collaboration_ratio,
                     planning_granularity, co-op_frequency ]

3. Standardize both vectors against the running feature distributions.

4. Compute Mahalanobis distance:
   D² = (narrative_vector − action_vector)ᵀ Σ^(−1) (narrative_vector − action_vector)

5. If D² > threshold → persona flag is active.
```

**Threshold:** Start at `D² > 3.0` (≈ 2 SD for 5-dimensional space under approximate normality). Calibrate empirically; lower to 2.5 if false-negative cost is high (the survey §6.2 recommends a 0.6 SD Mahalanobis starting heuristic, corresponding to this range).

**Cross-reference:** Full detection dimensions (linguistic inflation vs. action dissonance, reaction to probing, response strategy rigidity, social monitoring cues) are described in [Implicit Behavioral Inference Literature Survey §6.1](../RESEARCH/implicit-profiling.md#61-detection-signals).

### 6.3 Agent Response to Persona Flag

When the flag activates:

1. **Set `w_persona = 0.3`** for all subsequent text-derived observations until the flag clears.
2. **Elevate action-derived observations:** their effective weight increases by ×1.5 (preference shift toward revealed-preference signals).
3. **Inflate uncertainty on affected traits:** `σ_t ← σ_t + 0.1` for traits where narrative and action vectors diverged most.
4. **Do not surface the flag to the user.** Persona confrontation damages trust and incentivizes further concealment (survey §6.3).
5. **Journal the event:** record for later calibration and for (optional) chronicle anonymization.

### 6.4 Persona Flag Clearance

The flag clears after:

- The next `N = 3` consecutive observations where `D² < 0.5` (stable congruence), OR
- Explicit confirmation from an action-derived probe whose design purpose is to differentiate genuine vs. displayed preference (see §7 adversarial design)

---

## 7. Update Cadence

### 7.1 Recommended Default: Every-Interaction with Decay

```
for each user_interaction:
    extract_features(user_interaction)
    detect_persona_gap(current_window)
    compute w = compute_weight(recency, persona_flag, context_congruence)
    for each trait t:
        x_t = sensitivity_weighted_feature_vector(features, trait=t)
        profile[t].update(evidence=x_t, weight=w)
    compress_to_rolling_window(max_observations=50)
```

This is performed at the close of every interaction turn. The rolling window cap of 50 prevents unbounded memory growth while preserving τ-weighted access to long-term history.

### 7.2 Turn-Batch Alternative (High-Frequency Interaction)

If the agent operates in a high-frequency dialogue mode (many short messages per turn), batch within the turn:

```
per_turn_buffer = []
for each message in turn:
    features = extract_features(message)
    per_turn_buffer.append(features)

turn_vector = aggregate(per_turn_buffer, method="weighted_mean")
update_all_traits(turn_vector, weight=1.0)
```

Aggregation methods: weighted mean (default), max (for risk-dominant signals), or voted majority (for trait-direction consensus across sub-observations).

### 7.3 Epoch Boundary

At epoch boundaries, the agent performs a consolidation pass:

1. Recompute effective sample size (ESS) for each trait.
2. If ESS < 20 on any trait, mark the profile estimate as "low-confidence" and elevate that trait's weight on active-learning probes in the next epoch.
3. Log the epoch-end profile snapshot to the chronicle (anonymized: trait vector only, no identifying feature data).
4. Reset any ephemeral "contradiction inflation" flags that were scheduled to decay at epoch end.

---

## 8. Uncertainty Modeling

### 8.1 Confidence Score Definition

For each trait `t`:

```
confidence_t = 1.0 − entropy_normalized(t)
```

where entropy is computed from the Beta posterior:

```
H(α, β) = log B(α, β) − (α−1)(ψ(α) − ψ(α+β)) − (β−1)(ψ(β) − ψ(α+β))
```

`ψ` is the digamma function; `B` is the Beta function entropy proxy.

The normalized confidence is:

```
confidence_t = 1.0 − (H(α, β) / H(KAPPA, KAPPA))
```

where `H(KAPPA, KAPPA)` is the entropy of the prior (maximum entropy, minimum confidence).

**Properties:**
- `confidence_t = 0.0` at initialization (maximum uncertainty)
- `confidence_t → 1.0` as ESS → ∞
- `confidence_t ∈ [0, 1]` for all α, β > 0
- For α = β = 1 (no information), confidence = 0.0 exactly

### 8.2 Confidence-Conditioned Behavior

The agent uses confidence to modulate its in-game strategy:

| Confidence Region | Agent Behavior |
|---|---|
| `confidence < 0.3` (low) | Active-learning mode: seek high-information interactions; do NOT commit to trait-dependent game strategies |
| `0.3 ≤ confidence < 0.6` (moderate) | Mixed mode: allow confidence-weighted interventions; prefer low-risk, information-gathering choices |
| `confidence ≥ 0.6` (high) | Standard mode: personality-consistent play allowed; trait-dependent scenario selections enabled |

This implements the survey's (§4.3) recommendation to "target probes at top-2 σ traits" — the agent identifies traits with the lowest confidence and prioritizes interactions likely to yield discriminating signal for those traits.

### 8.3 Uncertainty Inflation Events

Certain events temporarily inflate σ (reduce confidence) regardless of raw ESS:

| Event | σ Inflation | Decay |
|---|---|---|
| Significant contradiction (§5) | +0.15 | Clears on resolution or after 3 consistent observations |
| Persona flag activation (§6) | +0.10 per affected trait | Clears on flag clearance |
| Profile rebuild (privacy revocation + re-init) | Reset to prior | Rebuilds from scratch |
| Cold start | Prior σ (= 0.15 on [0,1] scale) | Natural decay as observations accrue |

---

## 9. Worked Examples

### Example 1: Cold Start — First Three Interactions

**Scenario:** New user; profile is at population prior. Agent collects three interactions.

**Initial state (prior):**
```
μ = 0.50, confidence = 0.0
α = 5, β = 5  (κ=10, μ=0.5)
```

**Observation 1:** User submits a short, concrete, lowercase text with no hedging.
- Features: TTR = 0.72 (high), hedging = 0.0
- S[TTR, O] = +0.65, S[hedging, A] = −0.25
- w_eff = 1.0 (first observation, no persona flag, high context congruence)
- `x_O = 0.65 × 0.72 = 0.47`, `x_A = −0.25 × 0.0 = 0.0`

**After O1:**
```
O: α = 5 + 0.47 = 5.47, β = 5 + 0.0 = 5.00
   μ_O = 5.47/10.47 = 0.522, confidence_O = 1 - (5.47×5.00)/(10.47² × 11.47) ≈ 0.058

A: α = 5 + 0.0 = 5.00, β = 5 + 0.0 = 5.00
   μ_A = 0.500, confidence_A = 0.0 (no change)
```

**Observation 2:** Same user submits a tersely negotiated resource allocation (declines to share, no justification).
- Features: cooperation = 0.15 (low), hedging = 0.0
- S[cooperation, A] = +0.55, S[hedging, A] = −0.25
- w_eff = 1.0
- `x_A = 0.55 × (−0.85 normalised) + (−0.25) × 0.0 = −0.47`
  (normalisation: cooperation=0.15 on [0,1] → −0.85 on [−1,1] for S=+0.55 trait direction)
- `x_C = 0.55 × 0.0 = 0.0` (no conscientiousness signal here)

**After O2:**
```
A: α = 5.00 + 0.0 = 5.00, β = 5.00 + 0.47 = 5.47
   μ_A = 5.00/10.47 = 0.478, confidence_A ≈ 0.058
```

**Observation 3:** User takes a high-risk gambit (risks all resources for a 20% chance of 5× return).
- Features: risk_quantile = 0.85 (high), loss_aversion_delta = −0.30 (low aversion)
- S[risk_quantile, Risk] = +1.0, S[loss_aversion, Neuroticism] = +0.30
  (β=+0.30 means high loss aversion → higher x → higher Neuroticism estimate)
  
Observation evidence on Risk: high risk_quantile (0.85 → x = +0.85 for S=+1.0 trait direction, mapped to Risk trait which lives on its own axis; here risk tolerance is modeled as 1−N_inverted or a separate trait — for clarity we treat Risk as a sixth scalar tracked alongside OCEAN):
- `x_Risk = +0.85 × 1.0 = +0.85`

**Summary after observation 3:**

| Trait | μ | Confidence |
|---|---|---|
| Openness | 0.522 | 0.058 |
| Conscientiousness | 0.500 | 0.000 |
| Extraversion | 0.500 | 0.000 |
| Agreeableness | 0.478 | 0.058 |
| Neuroticism | 0.500 | 0.000 |
| Risk Tolerance | 0.575 | 0.108 |

**Interpretation:**    
- Low confidence across all traits: most are still at or near prior.    
- Openness slightly elevated (high TTR, concrete style); Agreeableness slightly decreased (low cooperation, no hedging).    
- Risk tolerance is the clearest early signal (high-confidence evidence from the gambit).    
- Agent should actively probe Conscientiousness and Extraversion in the next turns, since those traits have zero discriminating observations.

---

### Example 2: Decay Resolution — Including a Contextual Surprise

**Scenario:** A user we have tracked through 30 turns has stable μ_Conscientiousness = 0.78, σ = 0.07 (confidence ≈ 0.86). The user takes a turn in an unusual time-pressured crisis scenario. Response latency variance drops (urgent, focused behavior) and planning granularity coarsens (short, imperative instructions).

**Observation:**
- Features: latency_variance = 0.12 (very low), planning_granularity = 0.15 (coarse)
- S[latency_variance, C] = −0.40, S[planning_granularity, C] = +0.55 (fine granularity = high C, coarse = low C → s=−0.55)

Let's compute the trait-specific evidence:
- `x_C = (−0.40) × (latency_variance_normalised) + (−0.55) × (coarse_normalised)` 
  - latency_variance=0.12 is low → on [−1,1] scale for S=-0.40 it's roughly +0.3
  - planning_granularity=0.15 is coarse → on [−1,1] scale for S=-0.55 it's roughly +0.55
  - `x_C = −0.40 × 0.3 + −0.55 × 0.55 = −0.12 − 0.30 = −0.42`

**Without decay adjustment (bad approach):** μ_C shifts from 0.78 downward by the full −0.42, jumping toward 0.55 — a massive single-step movement that misrepresents the stable user.

**With exponential decay (τ=5 turns, this observation is turn 31, ~0.4× weight):**
- The 30 historical observations each carry weight decaying from 1.0 to ~0.4×
- The new observation carries w_eff ≈ 0.42
- Updated μ_C moves to approximately 0.76 — a small shift within the noise of a single observation, correctly flagged as "possibly situational."

**Application of w_context:** Because this turn occurred in a crisis context (which the agent recognizes as temporally anomalous), w_context is additionally lowered to 0.5, making the net effect even smaller (μ moves to ~0.745, flagged for re-evaluation in 3 turns).

**Outcome:** The correct profile inference is that the user's Conscientiousness is temporarily expressed in focused, coarse behavior under pressure — consistent with high Conscientiousness — and the Bayesian update correctly preserves the stable estimate.

---

### Example 3: Persona Flag + Contradiction

**Scenario:** The agent has μ_Agreeableness = 0.72 over 25 observations (nicely cooperative player). The user writes a long, moralizing narrative paragraph about "always putting others first" (high we-density, superlatives, self-reference). But simultaneously declines to cooperate in an in-game scenario that costs them nothing to help.

**Detection:**
- narrative_vector = [TTR=0.15, FPS_density=0.08, we_density=0.14, hedging=0.02, self_ref=0.06, superlatives=0.04]
- action_vector = [choice_entropy=0.08, risk_quantile=0.25, collab_ratio=0.05, planning=0.10]
- Mahalanobis distance D² = 4.8 > 3.0 threshold → **persona flag activates**

**Effect on update:**
- w_persona drops to 0.3 for the text-derived signal this turn.
- Action-derived observations retain w_persona = 1.0.
- Trait estimate for Agreeableness: the narrative signal would have pulled μ_A up to ~0.78; with w_persona=0.3 the contribution is reduced to a ~0.82 shift, moving μ_A to ~0.744 instead — still slightly inflated but not dramatically so.
- σ_A is inflated by +0.1, reflecting unresolved contradiction.

**Resolution (next 3 turns):**
User consistently makes low-cooperation choices (low collab ratio persists). D² falls below 0.5 by turn 4. Persona flag clears. The final Agreeableness estimate settles at μ_A ≈ 0.62, σ_A ≈ 0.08 — a realistic revised assessment and not the inflated 0.78 that the narrative alone would have produced.

---

## 10. Adversarial Robustness

### 10.1 Attack Surface

An adversarial user can attempt to manipulate their profile estimate through:

| Attack | Method | Targeted Effect |
|---|---|---|
| **Narrative inflation** | Post grandiose self-descriptions without corresponding action | Inflate Agreeableness, Conscientiousness, Extraversion, Openness |
| **Narrative deflation** | Post self-deprecating statements | Deflate self on desired-low traits |
| **Context gaming** | Repeatedly invoke persona-flagged contexts to trigger w_context reduction | Dilute signal quality to preserve an undesired estimate |
| **Observation flooding** | Many low-quality observations to reach ESS quickly at a biased value | Premature convergence |
| **Contradiction exhaustion** | Deliberately produce contradictory observations | Trigger σ inflation, then flood with consistent (but false) signal in desired direction |
| **Probe manipulation** | Recognize when the agent is in active-learning mode (high-uncertainty targeting) and respond with telltale "strong signal" fake actions | Guide profile toward a chosen direction |

### 10.2 Mitigations

#### M1: Persona Gap Enforcement (§6)

The primary defense. Narrative and action vectors are compared on every batch; any systematic divergence triggers w_persona = 0.3 on narrative features and elevated σ. This neutralizes pure-narrative attacks at the cost of a small efficiency loss.

#### M2: Entropy-Regulated Active Learning

When the agent enters active-learning mode (targeting high-uncertainty traits), it selects probe scenarios whose disclosed purpose is information-gathering — making manipulation overt. The agent does not announce "I'm probing your Agreeableness"; the scenario frame carries naturalistic information value. Crucially:

- Active-learning probes are **scenario-driven, not self-report driven.** The user cannot fake a personality-revealing action in-game without performing the actual action.
- The agent records post-probe self reports separately and treats them as low-weight confirmation of action signals, not replacement.

#### M3: Effective Sample Size Floor

Before a profile estimate crosses the usable threshold (ESS ≥ 20), no trait-dependent mechanical consequences are allowed in-game. This prevents observation-flood attacks from prematurely anchoring a profile.

```
if profile[t].ess < MIN_EFFECTIVE_SAMPLE_SIZE:
    lock_game_mechanic(mechanic="trait_dependent_scenario")
    log_event("profile_insufficient_ess", trait=t, ess=profile[t].ess)
```

#### M4: Contradiction Rate Monitor

High contradiction rate (> 15% of recent observations) on a trait triggers a **profile quarantine** for that trait: all future updates for that trait are held in a buffer pending review by the agent's meta-layer. The buffer holds up to 10 observations; beyond that, the oldest buffer entries are incorporated with double w_persona penalty. This defeats contradiction-exhaustion attacks by making sustained contradiction expensive.

#### M5: Cross-Source Correlation Check

Traits are not updated independently. The agent maintains a cross-correlation matrix across traits based on survey priors (survey §3: FFM dimensions have partial correlations with known signatures). An observation that pushes multiple traits simultaneously in a direction inconsistent with these correlations (e.g., extreme high in all five OCEAN dimensions from a single short text sample) triggers a quality check — the weighted update is attenuated by a factor equal to the squared residuals of the correlation residual.

```python
expected_correlation = CORRELATION_PRIOR[("Openness", "Neuroticism")]  # known empirical r
observed_joint_update = (x_O, x_N)  # from single observation
expected_joint = expected_correlation * x_O  # what N would be if real
correlation_residual = (observed_joint_update[1] - expected_joint) ** 2
attenuation = max(1.0 - correlation_residual, 0.5)  # halve the weight at worst
```

This prevents a single adversarial signal from generating implausibly correlated multi-trait jumps.

#### M6: Recency-Limited Override Quota

Even under genuine profile change, the rate of update is capped:

```
max_daily_mu_shift = 0.08  # maximum 8 percentage-point change per 24-hour window
```

If an observation would push μ beyond this ceiling, the excess is deflected into σ inflation (reflecting "we are seeing a lot of change quickly; we do not yet know if this is real"). This hard cap throttles both gaming attacks and the agent's own over-eager updating.

---

## 11. Pseudocode Summary: Full Update Cycle

```python
def interaction_cycle(
    profile: dict[str, TraitEstimate],   # O, C, E, A, N + optional Risk
    sensitivity: dict[str, dict[str, float]],  # feature → trait → weight
    feature_extractors: dict[str, Callable],
    observation: InteractionTrace,
    turn_clock: int,
    tau: int = 5,
    rolling_window_size: int = 50,
) -> dict[str, TraitEstimate]:
    
    # 1. Feature extraction
    features = {name: extractor(observation) for name, extractor in feature_extractors.items()}
    
    # 2. Persona detection
    persona_flag, D2 = detect_persona_gap(
        narrative_features = features["text"],
        action_features    = features["actions"],
        profile_history    = get_recent_window(50)
    )
    
    # 3. Compute weight
    w_context   = context_congruence_score(observation)
    w_persona   = 0.3 if persona_flag else 1.0
    w_recency   = exp(-turn_clock / tau)
    w_eff       = w_context * w_persona * w_recency
    
    # 4. Trait update
    for trait in profile:
        x = sum(sensitivity[f][trait] * features[f] for f in features)
        if abs(x) > CONTRADICTION_THRESHOLD:
            handle_significant_contradiction(profile[trait], x, w_eff)
        else:
            profile[trait].update(evidence=x, weight=w_eff)
    
    # 5. Apply daily cap
    for trait in profile:
        mu_before, mu_after = profile[trait].mu_history[-2:]
        if abs(mu_after - mu_before) > DAILY_SHIFT_CAP:
            profile[trait].attenuate(shift_cap=DAILY_SHIFT_CAP)
    
    # 6. Compress rolling window
    compress_window(max_size=rolling_window_size)
    
    # 7. Clear stale inflation
    if is_epoch_boundary(turn_clock):
        clear_stale_inflation(profile, max_age=3)
    
    return profile
```

---

## 12. Implementation Checklist for WWMHD Agents

Before deploying the profile update system in-game, the agent must verify:

- [ ] Sensitivity matrix `S` is calibrated and documented with empirical weights (not hand-waved)
- [ ] Persona gap threshold `D² > 3.0` is tuned on a held-out validation set of known persona-presenting vs. congruent interactions
- [ ] Decay time constant τ is set appropriate to interaction frequency (§7.1)
- [ ] Minimum ESS gate (≥ 20) is wired to trait-dependent game mechanics
- [ ] Cross-trait correlation residual check is enabled
- [ ] Daily shift cap (0.08 per 24h) is active
- [ ] Profile journaling records: timestamp, features, x vector, μ before, σ before, persona flag state, contradiction flag state — for post-hoc calibration and chronicle anonymization
- [ ] Anonymization pipeline strips all raw features from chronicle publications; only the final anonymized trait vector (μ + confidence per trait) is ever written to the chronicle

---

## 13. References to Survey

This methodology relies on the theoretical and empirical foundations established in the [Implicit Behavioral Inference Literature Survey](../RESEARCH/implicit-profiling.md). Specific cross-references:

| Methodology Section | Survey Section | Basis |
|---|---|---|
| OCEAN trait model + Beta prior | §7.1, §4.3 | FFM consensus; population priors (T-score μ=50, σ=10) |
| Feature extraction signals | §1, §5 | Empirical reliabilities for each trace type |
| Persona gap detection | §6.1–6.3 | Dissonance ratio, Mahalanobis threshold, agent response protocol |
| Self-report downweighting | §2.3 | Behavioral > self-reported under Bayesian update |
| Decay time constant | §4.2 | Rolling window with exponential decay vs. moving average |
| Cold start prior | §4.3 | Population-level priors; first 3–5 observations collapse uncertainty |
| Confirmation bias prevention | §4.1 | Uncertainty-directed active learning; red-teaming via counterfactual |
| Recency weighting | §7.3 | Exponential decay; confirms τ recommendation |
| Bias prevention table (anchoring, recency, narrative fit, persona) | §7.3 | Directly adopted methodology |
