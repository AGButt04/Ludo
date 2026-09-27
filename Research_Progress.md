# Ludo RL — Research Progress

Updated: September 22, 2026

## Project direction

Study how training choices affect an RL agent in four-player Ludo, rather than only building a strong bot. The goal is a rigorous senior thesis; the question remains provisional pending advisor feedback and a broader novelty search.

## Papers reviewed: findings and candidate questions

These are findings reported in the local papers, not results we have reproduced.

**2011 — Alvi & Ahmed: Complexity Analysis and Playing Strategies for Ludo**

- Analyzes state-space complexity and compares random, aggressive, defensive, fast, and mixed strategies. Its experiments support combining hand-designed strategies into a strong heuristic baseline.
- **Candidate question:** Does human strategic guidance accelerate learning, or restrict the performance and behavior an agent eventually develops?
- **Implication:** The strategies provide baselines and behavior categories. Guidance through rewards and initialization from expert knowledge are different interventions; our proposed study focuses on rewards.

**2012 — Alhajry et al.: TD(λ) and Q-Learning Based Ludo Players**

- Studies four-player self-play and training mixtures containing expert or random opponents. Self-play TD reaches approximately 66% wins against three random players and 30% against three experts; self-play Q-learning reaches approximately 63% and 27%.
- Expert-containing training mixtures did not improve final performance; the Q-learning results report faster learning with experts. TD uses terminal feedback, while Q-learning uses shaped rewards and predefined strategy actions.
- **Candidate question:** How do self-play and fixed-opponent training affect learning speed and performance against unfamiliar opponents?
- **Implication:** Opponent-regime comparisons already exist. Comparing the paper’s TD and Q-learning agents does not isolate reward effects because other design choices also differ.

**2023 — Tubaishat et al.: Incorporating Feature Penalty in Reinforcement Learning for Ludo Game**

- Uses Q-learning with penalty tables and evaluates against one, two, and three random opponents, plus humans. It reports strong performance against random players but weaker performance against humans.
- **Candidate question:** Does guidance that helps against simple opponents also help against stronger or unfamiliar opponents?
- **Implication:** Include held-out opponents and this study in the literature review. Some narrative results conflict with Table IV, so exact benchmark values need reconciliation.

**2026 — Bargavi et al.: DQN and PPO on Ludo with Structured State Encoding**

- Reports its best results with PPO and structured encoding: 83.7% against random and 42.3% against an expert. It reports sparse rewards finishing about eight percentage points below shaped rewards and identifies its two-player setting as a limitation.
- **Candidate question:** How do these training choices work in four-player Ludo, and does their effect change with player count?
- **Implication:** Its comparison with 2012 is not established as directly compatible: the older results involve three opponents, while this paper describes two-player experiments. Its reward comparison also does not establish how shaping interacts with self-play.

Sources: [2011](../Research%20and%20Thesis/Ludo1.pdf), [2012](../Research%20and%20Thesis/Ludo2.pdf), [2023](../Research%20and%20Thesis/Incorporating_Feature_Penalty_in_Reinforcement_Learning_for_Ludo_Game.pdf), [2026](../Research%20and%20Thesis/P3-2026-issue%201-%20Edu%20Ludo.pdf).

# Recommended Main Question and Experiment
> In four-player Ludo, how do training opponents and reward design independently—and interactively—affect PPO’s learning speed, performance against unfamiliar opponents, and behavior?

### What we change

1. **Training opponents:** fixed heuristic players or self-play opponents.
2. **Rewards:** feedback at the game's end, or additional human-designed feedback during play.

**Reward shaping** means adding feedback to the original task reward to guide learning. For example, an agent might receive its normal final-outcome reward plus a small reward for capturing a piece. Penalties can also be shaping. Exact events and values are undecided. Extra rewards can encourage behavior that does not improve winning, so their usefulness must be tested.

| Condition | Practices against | Receives |
| --- | --- | --- |
| A | Fixed heuristic opponents | Final-outcome rewards |
| B | Fixed heuristic opponents | Final-outcome rewards + shaping |
| C | Self-play opponents | Final-outcome rewards |
| D | Self-play opponents | Final-outcome rewards + shaping |

Each condition needs several independently trained agents. One lucky training run is insufficient evidence.

### What "independently" means

Change one factor while keeping the other fixed:

- **A versus B:** Does shaping help against fixed opponents?
- **C versus D:** Does shaping help during self-play?
- **A versus C:** Does self-play help with sparse rewards?
- **B versus D:** Does self-play help with shaped rewards?

Comparing only B with C changes both factors simultaneously. If C performs better, we cannot tell whether self-play helped, removing shaping helped, or both contributed.

### What "interactively" means

Does the effect of shaping depend on the training opponents?

**Hypothetical example only — these are not our results.** All agents are evaluated against the same held-out opponent pool:

| Training regime | Sparse | Shaped | Shaping effect |
| --- | --- | --- | --- |
| Fixed opponents | 35% | 45% | +10 percentage points |
| Self-play | 50% | 48% | -2 percentage points |

Here, shaping helps with fixed opponents but slightly hurts with self-play. Its effect depends on the training regime: that is an interaction. The difference between the shaping effects is -12 percentage points on this win-rate scale. Repeated runs and uncertainty estimates are needed to determine whether observed differences are convincing.

### What we keep comparable and measure

Keep the PPO implementation, network architecture, board representation, rules, and training budgets comparable. Define the self-play procedure and budget units explicitly. Evaluate with multiple independent training seeds, balanced seats, held-out opponents, and uncertainty estimates.

- **Learning speed:** How performance develops with training experience.
- **Generalization:** Performance against opponents excluded from training. Reserve final test opponents from tuning as well.
- **Behavior:** Captures made/suffered, safe-square usage, active-piece counts, and concentrated versus distributed progress. Account for game length and available choices; these measurements describe behavior rather than prove novel strategies.

**Potential contribution:** Evidence about when a training choice helps and when it does not, through a controlled four-player PPO comparison. We do not assume self-play or shaping will win. The reviewed papers do not establish this exact comparison, but novelty remains unverified. Two-player games can be an optional pilot; a full player-count comparison would double the four conditions.

## Current progress and next steps

- **Completed:** Initial review of the four Ludo papers; candidate-question refinement; cleanup and checking of simulator teaching examples.
- **Not yet completed:** Broader novelty search, validated simulator implementation, or new training experiments.
- **Next engineering step:** Confirm the board route, then explain, approve, implement, and test one file at a time.
- **Advisor discussion:** Is this controlled comparison sufficiently distinct and feasible? Which baselines and behavioral measurements deserve priority? Should two-player work remain a pilot?
