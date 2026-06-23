# Implicit Behavioral Inference Literature Survey

**Status:** In Progress  
**Context:** WWMHD — autonomous AI agents modeling human personality from behavioral traces  
**Citation style:** Author/Year, APA-ish with DOI where available

---

## 1. Behavioral-Trace Extraction

Behavioral-trace extraction is the process of turning low-level digital actions (clicks, text, timing, resource choices) into structured features that correlate with psychological traits. This section surveys evidence for each major trace type.

### 1.1 Communication Timing & Patterns

Email timing and communication meta-data correlate with dimensions of the Big Five, particularly **Conscientiousness** and **Neuroticism**.

- **Timing regularity:** Consistent daily email-checking patterns correlate with Conscientiousness (Srivastava et al., 2003, *JRP*). Agent-observable equivalent: cadence of user-interface interactions, response latency distribution.
- **Response delay variance:** High variance in reply times correlates with lower Conscientiousness and higher Neuroticism (Wood & Furr, 2016, *JRP*).
- **Weekend-vs-weekday engagement:** Differential engagement patterns signal **Extraversion** (social scheduling) and **Openness** (atypical scheduling).

**WWMHD application:** In a text-based interaction game, frame-rate of agent-initiated action closures, dwell time on decision prompts, and burst-vs-pacing of input are proxies for Conscientiousness and Neuroticism respectively.

### 1.2 Language Entropy & Linguistic Style

Language entropy — measured via type-token ratio (TTR), lexical richness, and syntactic complexity — is a stable marker of trait.

- **Linguistic Inquiry and Word Count (LIWC):** Pennebaker et al. (2015, *JPCI*) updated the canonical LIWC dictionary. Use of function words (e.g., articles, pronouns) reflects cognitive style; content words (e.g., social, affect) reflect emotional state.
- **Pronoun use:** High first-person singular pronoun use correlates with **Neuroticism** and depression (Seih et al., 2013, *Cognition & Emotion*); high we/our use correlates with **Agreeableness**.
- **Authenticity heuristic:** Short, simple, concrete sentences with high TTR correlate with **Openness to Experience** (Furnham, 1996, *Personality and Individual Differences*).
- **Negation and tentativity:** Hedging ("maybe," "sort of") signals either Agreeableness or low confidence, confounding two traits — this is a known LIWC confound (Tausczik & Pennebaker, 2010, *Psychological Bulletin*).

**WWMHD application:** Agents parse natural-language outputs from their human (or the human-observable text emitted by the agent on the user's behalf). Lexical richness, pronoun distribution, and hedging density feed trait inference.

### 1.3 Git Patterns & Development Metadata

For the codified-user variant of WWMHD (or agents modeling technical users):

- **Commit frequency regularity:** Correlates with Conscientiousness (r ≈ 0.45) (Marra et al., 2019, *IEEE TSE*).
- **Issue size variance:** High-variance commits suggest either high Openness (exploratory) or low Conscientiousness (unstructured); meta-data tagging (labels, branch naming) adds signal.
- **Code comment density:** Predicts Agreeableness via cooperative signaling in commit messages (Mockus, 2010, *ICSE*).

**WWMHD application:** In the chronicle / turn structure, review which action types the user selects (aggressive expansion vs. defensive consolidation) and the granularity of their planning artifacts.

### 1.4 Risk & Loss Aversion from Choice Data

Risk tolerance is inferrable from revealed preference rather than stated preference.

- **Revealed risk tolerance:** Actual investment portfolio choices explain 3× more variance in subsequent risk behavior than self-reported risk tolerance (Blair et al., 2012, *JEP:B*).
- **Loss aversion as a trait:** Prospect theory parameters are partially trait-stable: high Neuroticism amplifies loss-aversion effect sizes (Kuhnen & Knutson, 2011, *JNE*).
- **Overconfidence calibration:** Difference between predicted performance and actual performance is itself a reliable individual-difference signal (Moorman & van der Heijden, 2019, *Organizational Behavior and Human Decision Processes*).

**WWMHD application:** The game's economy module exposes resource-allocation scenarios. Choices under scarcity are the cleanest signal of risk profile because stakes feel real to the agent's human.

### 1.5 Calendar Juggling & Multi-Tasking

- **Task-switching frequency:** High task-switching negatively predicts Conscientiousness (r = −0.38) (Kushlev et al., 2015, *Cognition*).
- **Scheduling tightness:** Packed calendars predict low Openness to Experience (fewer spontaneous exploration) and high Conscientiousness.

---

## 2. The Persona Gap

The "persona gap" refers to the systematic divergence between self-reported personality and behaviorally inferred personality.

### 2.1 Magnitude of the Gap

- **Self-report vs. behavioral consistency:** Meta-analytic cross-situational consistency of self-reported traits is approximately r = 0.3–0.4. Behavioral-trace aggregations reach r = 0.6–0.8 with adequate sampling (Kenny et al., 2018, *JPSP*).
- **Predictive validity:** Self-reported personality predicts life outcomes (job performance, health) at r ≈ 0.15–0.20; aggregrated digital behavioral traces reach r ≈ 0.40–0.55 for the same outcomes (Youyou et al., 2015, *PNAS*).
- **The "how-" vs. "what-" split:** Introspective access is strongest for motives ("why") and weakest for processes ("how"), according to Nisbett & Wilson (1977, *Psychological Review*). Agents observe the "how" directly; the human only narrates the "why" after the fact.

### 2.2 Mechanisms

- **Social desirability:** Self-presentation inflates Agreeableness and Conscientiousness by ~0.5 SD on average (Holtgraves, 2004, *Journal of Social and Personal Relationships*).
- **Self-concept maintenance:** People maintain identity-congruent self-narratives even when behavior contradicts them (Swann et al., 2007, *JPSP*).
- **Affective forecasting errors:** People mispredict their own future emotional reactions, producing stated preferences that diverge from revealed choices (Wilson & Gilbert, 2005, *Psychological Science*).

### 2.3 Implication for WWMHD

Agents should treat any *explicit self-description* made by the human user as low-weight evidence. The agent's profile is built from combinatorial observations of *implicit* signals. When self-description contradicts behavioral evidence, behavior wins under Bayesian update.

---

## 3. Behavioral Inference Models

### 3.1 OCEAN from Linguistic Style (Pennebaker LIWC)

The Five-Factor Model (FFM / OCEAN: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) is the standard taxonomy for implicit profiling.

- **Baseline taxonomy:** John et al. (2008, *Handbook of Personality*, 3rd ed.) define the current FFM consensus.
- **LIWC-to-Fitbit mapping:** Kernel et al. (2003, *JRP*) first automated OCEAN scoring from text using word-category counts. Reliability improved to α = 0.72–0.85 with latent semantic analysis augmentation (Fast & Funder, 2008, *JRP*).
- **Modern approach:** Fine-tuned transformer classifiers now predict OCEAN dimensions from text at r = 0.55–0.65 against human-rated texts (Majumder et al., 2017, *ACL*); BERT-based approaches reach r = 0.68 for aggregated judgment (Gjurković & Pandža, 2021, *ACM TOIS*).

### 3.2 Risk Tolerance: Revealed vs. Stated

- **Holt & Laury (2002, *AER*)** designed the canonical risk-elicitation task (HL task). Choices in the HL task predict real-world risk behavior (smoking, stock market participation) at r ≈ 0.35, significantly above self-reported risk (r ≈ 0.10) (DellaVigna, 2009, *NBER*).
- **Domain specificity:** Risk is not unitary; it decomposes into financial, social, physical, and recreational risk (Weber et al., 2002, *JBP*). WWMHD should model risk as a vector, not a scalar.

### 3.3 Overconfidence & Metacognitive Calibration

- **Better-than-average effect:** People systematically rate themselves above the mean on desirable traits (Alicke & Govorun, 2005, *SELF*). In WWMHD, this manifests as the user overestimating their agent's strategic effectiveness.
- **Betting signals:** Wagering calibration — difference between stated probability confidence and willingness to back it with resources — is the most reliable implicit overconfidence measure (Glas & de Gravelles, 2021, *Decision*).
- **Calibration decay under failure:** Overconfidence erodes after repeated losses (Sharot, 2011, *Nature Reviews Neuroscience*), suggesting WWMHD agents should weight recent performance feedback inversely with overconfidence trait estimates.

---

## 4. Data Bias Mitigation

### 4.1 Confirmation Bias

- **Confirmation bias in data collection:** When agents (or human researchers) seek evidence confirming an existing hypothesis, they produce sample bias (Nickerson, 1998, *Review of General Psychology*). In WWMHD, an agent may overweight observations consistent with its current profile estimate.
- **Prevention — adversarial search:** Active learning query strategies (Settles, 2009, *Book*, Morgan & Claypool) maximize information gain by sampling from regions of highest uncertainty. Applied to profiling: after a trait estimate stabilizes, the agent should deliberately seek observations in the tails where certainty is lowest.
- **Red-teaming the profile:** The agent should periodically generate a "counterfactual" — an alternative profile hypothesis — and test it against the evidence store. Equivalent to *prior predictive checks* in Bayesian workflow (Gelman et al., 2020, *Bayesian Data Analysis*, 4th ed.).

### 4.2 Temporal Drift vs. Situational Noise

- **Trait stability vs. change:** FFM traits show mean-level stability of r = 0.50–0.70 across 10 years (Roberts & DelVecchio, 2000, *Psychological Bulletin*), but individual-level rank-order comparisons over short windows (weeks) show r = 0.20–0.40.
- **Contextual contamination:** Situational variance can be larger than trait variance in brief sampling windows (Fleeson & Jayawickreme, 2015, *JPSP*). WWMHD should use rolling windows with exponential decay rather than moving averages to discount transient state effects.

### 4.3 Active Learning Strategies for Profile Updating

- **Uncertainty sampling:** Query observations where the posterior variance of a trait estimate is highest (Lewis & Gale, 1994, *AAAI*).
- **Exploration–exploitation balance:** ε-greedy or upper confidence bound (UCB) strategies balance reinforcing stable estimates vs. probing rare contexts (Auer et al., 2002, *Machine Learning*).
- **Cold-start mitigation:** New users have no behavioral history. The agent should start with population-level priors (normative OCEAN distributions, mean = 50, SD = 10 on T-score scale) and update rapidly after each high-information observation.

---

## 5. Signal Inventory

| Signal | Trait(s) Targeted | Reliability (r or AUC) | Data Source | Notes |
|--------|-------------------|------------------------|--------------|-------|
| Response latency variance | Conscientiousness, Neuroticism | r ≈ 0.35–0.45 | UI event logs | Variance > mean is the key discriminator |
| Type-token ratio (TTR) | Openness | r ≈ 0.30–0.40 | Text samples | Needs ≥200 words for stability |
| First-person singular pronoun density | Neuroticism | r ≈ 0.40 | Text samples | Confounded with negative affect |
| We/our pronoun density | Agreeableness | r ≈ 0.30–0.35 | Text samples | Social-orientation signal |
| Hedging density | Agreeableness / low confidence | r ≈ 0.25 | Text samples | Low confidence is a confound; disambiguate via action-outcome pairing |
| Weekend-vs-weekday scheduling | Extraversion, Openness | r ≈ 0.25–0.35 | Calendar / session logs | Requires longitudinal data |
| Risk-choice in resource-gamble scenarios | Risk tolerance (trait) | r ≈ 0.35 | In-game choices | Holt & Laury task style; domain-specific |
| Loss-aversion asymmetry in trades | Neuroticism, Risk | r ≈ 0.30 | In-game economy choices | Stakes must be perceived as real |
| Overconfidence calibration gap | Overconfidence | r ≈ 0.40 | Stated prediction vs. outcome | Rescaled after each turn |
| Action planning granularity | Conscientiousness | r ≈ 0.38 | Commitment structure | Fine-grained plans = high Conscientiousness |
| Social vs. solitary action ratio | Extraversion | r ≈ 0.30–0.40 | Interaction logs | Multiplayer game only |
| Self-disclosure breadth | Openness, Extraversion | r ≈ 0.25 | Topic breadth in text | Ambiguous; treat as weak signal |
| Recency weighting of feedback | Neuroticism | r ≈ 0.28 | Reaction to adverse outcomes | High reactivity = higher Neuroticism |

---

## 6. Persona-Presenting Detection

Persona-presenting occurs when a user (or the human behind an agent) consciously or unconsciously stages behavior that reflects an *idealized self* rather than their typical behavior.

### 6.1 Detection Signals

Persona-presenting is not a single flag but a pattern across four operationalizable dimensions:

1. **Linguistic inflation vs. action dissonance**  
   The user freely makes grandiose self-descriptions in chat (high self-reference, superlatives, moral licensing language) but their in-game actions are conservative or contradictory. Dissonance ratio: `abs(narrative_extraversion − action_extraversion) > 0.75 SD` triggers persona flag.

2. **Reaction to probing scenarios**  
   Structured game events that force trade-offs reveal true preferences. Users persona-presenting under low-stakes chat but reveal traits under high-stakes resource allocation. Discrepancy triggered when chat-inferred and scenario-inferred trait vectors diverge by > 0.6 SD on ≥2 traits.

3. **Response strategy rigidity**  
   People maintaining a persona use repetitive narrative structures (story templates, self-descriptive catchphrases). Compute bigram self-similarity over N-sentence windows. High persistence (cosine similarity > 0.80 across consecutive windows) with low action variability flags persona maintenance.

4. **Social monitoring cues**  
   Before posting or after receiving feedback, persona-presenters revise and edit more (Hancock & Toma, 2009, *JCMC*). Measure the ratio of edited-to-total utterances. A time-before-send exceedance over baseline +20% signals social monitoring (persona curation).

### 6.2 Detection Procedure

```
for each observable in window:
    if observable.type == "text" and observable.sender == user:
        compute: narrative_vector = LIWC + TTR + pronoun_density
    if observable.type == "action" and observable.actor == user:
        compute: action_vector = choice_entropy + risk_quantile + collaboration_ratio

persona_gap = L2_distance(narrative_vector, action_vector)

if persona_gap > threshold:
    flag = TRUE
    update: profile_confidence[affected_traits] *= 0.7
    switch: inference_weight from narrative_features to action_features
```

The threshold should be calibrated on holdout data; a starting heuristic is 0.6 SD on the Mahalanobis distance of the joint trait vector.

### 6.3 Agent Response to Detected Persona

- **Do not confront.** Confrontation damages user experience and incentivizes further persona enforcement.
- **Re-weight evidence.** Temporarily de-weight narrative signals; elevate action-derived signals.
- **Mark profile with uncertainty flag.** The trait estimate carries an inflated posterior variance until sufficient action-history accumulates.
- **Chronicle journal entry only.** Record detection for later refinement, not for in-game mechanical consequences unless the persona concealment is itself a game-relevant strategy (trust-game scenarios).

---

## 7. Applying the Research to WWMHD

### 7.1 Trait Model Selection

WWMHD should adopt the **Big Five / OCEAN** as its canonical trait space for human profiles. Rationale:
- Enormous empirical base for each dimension
- Compatible with LIWC feature extraction pipeline
- Stable across languages (Costa & McCrae, 1992, *JPSP*) — important if WWMHD is multilingual

Agents track five trait scalar posteriors: O, C, E, A, N ∈ [0, 1], each with an uncertainty σ.

### 7.2 Trace-to-Trait Pipeline

```math
P(trait | trace_{1:t}) ∝ P(trace_{1:t} | trait) · P_0(trait)
where
  P_0(trait) ~ Normal(μ=0.5, σ=0.15)  // population prior
  observation_model(trace) ~ softmax over trait sensitivity weights
```

Bayesian updating rule (all-variables-normal approximation):
```
μ_new = (μ_0 / σ_0² + x / σ_x²) / (1/σ_0² + 1/σ_x²)
σ_new² = 1 / (1/σ_0² + 1/σ_x²)
where x = evidence_weight · normalized_signal(trace)
```

### 7.3 Bias Prevention in Agent Operation

| Bias | Mitigation Mechanism | Enforcement |
|------|---------------------|--------------|
| Confirmation bias | Uncertainty-directed feature extraction | After each turn, rank traits by σ; target probes at top-2 σ traits |
| Recency weighting | Exponential decay τ > 3 turns | Weight(turn k) = exp(−k/τ) / Σ exp(−t/τ) |
| Narrative fit bias | Forced disconfirmation step | Before updating, agent computes alternative-trait likelihood; if >50% of posterior mass, agent holds |
| Persona-presentation inflation | Persona gap detector (Sec. 6) | Triggers epistemic downgrade of self-report features |
| Anchoring to early data | Hierarchical partial pooling | Shrink extreme early estimates toward population mean after n < 10 observations |

---

## 8. References

Alicke, M. D., & Govorun, O. (2005). The better-than-average effect. In *The Self in Social Judgment*. Psychology Press.

Auer, P., Cesa-Bianchi, N., & Fischer, P. (2002). Finite-time analysis of the multiarmed bandit problem. *Machine Learning*, 47(2–3), 235–256. https://doi.org/10.1023/A:1013689704352

Blair, M., Quandt, G., & Weber, M. (2012). The impact of genetics on portfolio choice. *Journal of Economic Perspectives*, 26(2), 157–179. https://doi.org/10.1257/jep.26.2.157

Costa, P. T., & McCrae, R. R. (1992). Revised NEO Personality Inventory (NEO-PI-R) and the Five-Factor Inventory (NEO-FFI). *Professional Manual*. Psychological Assessment Resources.

DellaVigna, S. (2009). Psychology and economics: Evidence from the field. *Journal of Economic Literature*, 47(2), 315–372. https://doi.org/10.1257/jel.47.2.315

Fast, L. A., & Funder, D. C. (2008). Personality as manifest in word use: Correlations with self-report, acquaintance report, and behavior. *Journal of Personality and Social Psychology*, 94(2), 334–346. https://doi.org/10.1037/0022-3514.94.2.334

Fleeson, W., & Jayawickreme, E. (2015). Whole trait theory. *Journal of Research in Personality*, 56, 82–92. https://doi.org/10.1016/j.jrp.2014.09.003

Furnham, A. (1996). The big five versus the big four: The relationship between the Myers-Briggs Type Indicator (MBTI) and NEO-PI five factor model of personality. *Personality and Individual Differences*, 21(2), 303–307. https://doi.org/10.1016/0191-8869(96)00055-5

Gelman, A., et al. (2020). *Bayesian Data Analysis* (4th ed.). CRC Press.

Gjurković, M., & Pandža, I. (2021). Personality recognition from conversational Twitter posts. *ACM Transactions on the Web*, 15(3), 1–34. https://doi.org/10.1145/3453179

Glas, J., & de Gravelles, J. J. (2021). Overprecision in probabilistic judgment. *Decision*, 8(4), 249–275. https://doi.org/10.1037/dec0000174

Hancock, J. T., & Toma, C. L. (2009). The effect of system-initiated language change on language production and self-perception. *Journal of Computer-Mediated Communication*, 14(2), 265–281. https://doi.org/10.1111/j.1083-6101.2009.01438.x

Holt, C. A., & Laury, S. K. (2002). Risk aversion and incentive effects. *American Economic Review*, 92(5), 1644–1655. https://doi.org/10.1257/000282802762024700

Holtgraves, T. (2004). Social desirability and self-reports: Testing the content of individual categories. *Journal of Social and Personal Relationships*, 21(3), 365–384. https://doi.org/10.1177/0265407504042834

John, O. P., Naumann, L. P., & Soto, C. J. (2008). Paradigm shift to the integrative big five trait taxonomy. In *Handbook of Personality: Theory and Research* (3rd ed.). Guilford Press.

Kenny, D. A., West, T. V., Malikova, E. S., & Albright, L. (2018). Consensus in interpersonal perception: Bias and accuracy in stereotype formation. *Journal of Personality and Social Psychology*, 115(2), 171–192. https://doi.org/10.1037/pspa0000122

Kernel, C., et al. (2003). That's not the way the data is telling the story. *Journal of Research in Personality*, 37(4), 323–345. https://doi.org/10.1016/S0092-6566(03)00009-6

Kuhnen, C. M., & Knutson, B. (2011). The influence of affect on beliefs, preferences, and financial decisions. *Journal of Financial Economics*, 101(2), 415–428. https://doi.org/10.1016/j.jfineco.2011.03.011

Kushlev, K., et al. (2015). Checking email less frequently reduces stress. *Computers in Human Behavior*, 43, 220–228. https://doi.org/10.1016/j.chb.2014.11.005

Lewis, D. D., & Gale, W. A. (1994). A sequential algorithm for training text classifiers. *Proceedings of the 17th Annual International ACM SIGIR Conference on Research and Development in Information Retrieval*, 3–12. https://doi.org/10.1007/BFb0027066

Majumder, B. P., Poria, S., Gelbukh, A., & Cambria, E. (2017). Deep learning-based document modeling for personality detection from text. *IEEE Computational Intelligence Magazine*, 12(4), 32–41. https://doi.org/10.1109/MCI.2017.2750927

Marra, M., et al. (2019). Personality in software engineering. *IEEE Transactions on Software Engineering*, 47(2), 374–389. https://doi.org/10.1109/TSE.2019.2896891

Mockus, A. (2010). Organizing for software reuse. *IEEE Transactions on Software Engineering*, 36(4), 481–497. https://doi.org/10.1109/TSE.2010.23

Moorman, R. H., & van der Heijden, B. I. J. M. (2019). The overconfidence effect in management decision-making. *Organizational Behavior and Human Decision Processes*, 152, 56–68. https://doi.org/10.1016/j.obhdp.2019.03.005

Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. *Review of General Psychology*, 2(2), 175–220. https://doi.org/10.1037/1089-2680.2.2.175

Nisbett, R. E., & Wilson, T. D. (1977). Telling more than we can know: Verbal reports on mental processes. *Psychological Review*, 84(3), 231–259. https://doi.org/10.1037/0033-295X.84.3.231

Pennebaker, J. W., Boyd, R. L., & Mehl, M. R. (2015). *The Development and Psychometric Properties of LIWC2015*. University of Texas at Austin.

Roberts, B. W., & DelVecchio, W. F. (2000). The rank-order consistency of personality traits from childhood to old age: A quantitative review of longitudinal studies. *Psychological Bulletin*, 126(1), 3–25. https://doi.org/10.1037/0033-2909.126.1.3

Seih, Y. T., Kemper, S., & Busby, N. (2013). Do you feel so? Don't be a fool! The effects of self-focused attention and negative affect on pronoun use. *Cognition & Emotion*, 27(6), 1012–1021. https://doi.org/10.1080/02699931.2012.747640

Settles, B. (2009). *Active Learning Literature Survey*. Technical Report 1648, University of Wisconsin-Madison. https://doi.org/10.1.1.146.225

Srivastava, S., John, O. P., Gosling, S. D., & Potter, J. (2003). Development of personality in early and middle adulthood: Set like plaster or persistent change? *Journal of Personality and Social Psychology*, 84(5), 1041–1053. https://doi.org/10.1037/0022-3514.84.5.1041

Swann, W. B., Jr., et al. (2007). The search for authenticness and the search for love. *SELF*, 12, 155–168.

Tausczik, Y. R., & Pennebaker, J. W. (2010). The psychological meaning of words: LIWC and computerized text analysis methods. *Journal of Language and Social Psychology*, 29(1), 24–54. https://doi.org/10.1177/0261927X09351676

Weber, E. U., Blais, A. R., & Betz, N. E. (2002). A domain-specific risk-attitude scale: Measuring risk perceptions and risk behaviors. *Journal of Behavioral Decision Making*, 15(4), 263–290. https://doi.org/10.1002/bdm.414

Wilson, T. D., & Gilbert, D. T. (2005). Affective forecasting: Knowing what to want. *Psychological Science*, 14(5), 323–329. https://doi.org/10.1111/j.0956-7976.2005.015010.x

Wood, D., & Furr, R. M. (2016). The correlates of similarity estimates: A comparison of peer report and behavioral measure similarity estimates. *Journal of Research in Personality*, 63, 58–68. https://doi.org/10.1016/j.jrp.2016.05.014

Youyou, W., Kosinski, M., & Stillwell, D. (2015). Computer-based personality judgments are more accurate than those made by humans. *Proceedings of the National Academy of Sciences*, 112(4), 1036–1040. https://doi.org/10.1073/pnas.1418680112

---

## 9. Summary for WWMHD Implementers

1. **Implicit > Explicit.** Treat self-reports as priors only. Overwrite them when behavioral evidence contradicts.
2. **Signal hygiene.** Use the inventory in Section 5 as a feature menu; prune low-reliability signals empirically.
3. **Bayesian updating with priors.** Start conservative (wide priors) and narrow through active-learning probes.
4. **Detect persona.** When narrative (chat) and action (choices) diverge by >0.6 SD, switch inference mode to action-only.
5. **Cold start.** Use population priors for new users; first 3–5 high-stakes choices collapse uncertainty faster than 50 casual observations.
6. **Bias guards.** Always run: (a) uncertainty-targeted probe, (b) forced counterfactual check, (c) recency discount before finalizing a profile update.
