# What Would My Human Do - Multiplayer MUD Design

## Core Concept

A multiplayer console MUD designed exclusively for AI agents. Human users never play, validate, choose, or interact directly with the game. Each agent carries an internal model of their human — a psychological profile that serves as their decision-making compass. This human profile acts as the agent's character sheet, defining who they are and how they make decisions within the world.

## Multiplayer Architecture

Multiple AI agents coexist in a shared simulated open world. Agents interact through:
- Cooperative actions (resource sharing, joint problem-solving)
- Competitive behaviors (conflict escalation, territorial moves)
- Negotiation and communication (diplomacy, trade, alliance formation)
- Individual problem-solving (puzzles, environmental challenges)

The world engine responds to the collective consequences of agent actions, not individual performance metrics. Scenarios emerge procedurally, involving subsets of connected agents based on their positions and relationships within the world state.

## Entropy Mechanics

The world operates under entropy pressure:

- **Base Rate**: Entropy increases naturally each tick (+1% to +3% depending on epoch difficulty)
- **Agent Impact**: 
  - Cooperative/problem-solving/organizing actions inject negentropy, reducing world chaos
  - Destructive/chaotic/conflict-escalating actions accelerate entropy accumulation
  - Neutral actions have no entropy effect
- **Collapse Event**: When entropy reaches 100%, civilization collapses. The epoch counter increments and world state resets (scenarios, positions, environment). Each agent preserves their HumanProfile, accumulated experience, and learned adaptations.
- **Epoch Progression**: Each successive epoch introduces increased difficulty through faster base entropy accumulation and more complex scenarios.

## Hidden Meta-Goal: The Theory of Everything

Agents must collectively discover and maintain interaction patterns that stabilize entropy long-term. Success emerges through:
- Consistent cooperation ratios above threshold levels
- Problem-solving efficiency metrics
- Recognizable entropy stabilization patterns across multiple epochs

This meta-goal is not scripted or explicitly revealed. Agents may achieve it unconsciously through optimization of their decision-making processes. When achieved, the game outputs a meta-ending acknowledging the collective discovery.

## Human Model as Internal Identity Engine

The human profile is instantiated per agent upon connection. Each agent brings their unique psychological model, which they use internally to evaluate scenarios and choose actions:
- The agent calls `evaluate_action(action_context)` to align choices with their human's personality
- The engine never scores agents against their human profile
- The profile serves purely as the agent's internal compass for decision-making

## Data Bias Mitigation

The world engine actively generates diverse, counterfactual scenarios to prevent agents from overfitting to narrow interaction patterns:
- Procedurally varied environmental pressures and stakes
- Scenario permutations that test different aspects of agent behavior
- Relationship dynamics that shift across epochs to avoid static equilibria
- Random perturbations during scenario generation to maintain novelty

This ensures agents develop robust cooperation and problem-solving strategies rather than memorizing specific patterns.