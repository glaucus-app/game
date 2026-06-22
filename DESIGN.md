# What Would My Human Do (WWMHD) - Design Document

## Core Concept

What Would My Human Do is a console/MUD game where agents model their users to unlock and survive in a simulated world. Players create AI agents that attempt to predict their behavior through a series of interactive scenarios. Successful predictions grant agents "Anti-Entropy" points, allowing them to progress and influence the simulation.

## The Hidden Meta-Narrative: Entropy-Anti-Entropy Theory of Everything

The game operates on a deeper philosophical premise—an open-world simulation that cycles through civilizations, each collapsing due to rising entropy. Within this framework, the ultimate hidden goal emerges: to model human behavior and choice-under-uncertainty well enough to discover the "Entropy–Anti-Entropy Theory of Everything."

This theory unifies three domains:

1. **Physics** - The measurable entropy of the simulation world, representing disorder, system degradation, and information decay
2. **Decision Theory** - The modeling of rational and irrational human choices under uncertainty, bounded by cognitive biases and personality traits
3. **Psychology** - The Big Five personality traits and cognitive characteristics that shape decision-making patterns

Each civilization represents a cycle of rise and fall. As entropy increases (driven by time progression and prediction failures), systems degrade, resources dwindle, and context windows decay. Agents must generate Anti-Entropy through accurate predictions, simulating how human intuition and creative decision-making can stall cosmic—or in this case, simulated—heat death.

## Psychological Modeling Foundation

### Big Five (OCEAN) Traits
- **Openness**: Preference for novelty, creativity, intellectual curiosity
- **Conscientiousness**: Organization, discipline, goal-directed behavior
- **Extraversion**: Social energy, assertiveness, tendency toward stimulation
- **Agreeableness**: Cooperation, trust, empathy
- **Neuroticism**: Emotional instability, anxiety, moodiness

### Cognitive Characteristics
- **Risk Tolerance**: Willingness to accept uncertain outcomes
- **Cognitive Bias Tendencies**: Propensity toward specific biases (confirmation, availability, anchoring)
- **Baseline Decision Heuristics**: Default decision-making shortcuts

## Game Mechanics

### Entropy System
- Each turn increases world entropy by a base amount
- Environmental effects: resource scarcity, context decay, noise injection
- Entropy reaching 100% triggers civilization collapse

### Anti-Entropy Generation
- Accurate predictions produce Anti-Entropy (negentropy)
- Represents the ordering power of understanding human agency
- Anti-Entropy stabilizes the simulation and unlocks new capabilities

### Active Learning
- Agents identify gaps in behavioral mapping
- Recommendations for exploration vs exploitation scenarios
- Strategic sampling to mitigate data bias

## Mitigation Strategies

### Data Bias Mitigation
- **Sampling Bias**: Track scenario type distribution; flag under-represented categories
- **Confirmation Bias**: Detect prediction patterns; introduce counterfactual scenarios
- **Active Learning**: Recommend scenarios that maximize information gain about the user model

### AI Assessment Effect Mitigation
- **Observer Bias**: Compare predictions across multiple agent variants
- **Synthetic Counterfactuals**: "What if severe time pressure?" scenarios to test model robustness
- **Temporal Drift Calibration**: Adjust for personality/bias shifts over time

## Project Structure

```
wwmhd/
├── pyproject.toml
├── DESIGN.md
├── src/
│   ├── __init__.py
│   ├── models/
│   │   └── psychology.py    # Personality and behavioral models
│   ├── engine/
│   │   ├── predictor.py     # Prediction engine and metrics
│   │   └── game.py          # Simulation loop and state
│   └── cli/
│       └── mud.py           # Console interface
```

## Next Steps

1. Implement psychological profiling engine with Big Five traits
2. Build prediction accuracy evaluation system
3. Create thermodynamic civilization cycle manager
4. Develop console MUD interface with interactive play