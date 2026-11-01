# Ludo RL — Project Map

Updated November 1, 2026. Working engine v1 with persistent traces and a bounded coverage review; full manual play review and RL remain pending.

## Current files

Paths below are relative to `Environment and Implementation/`.

| File | Responsibility |
|---|---|
| `Game/constants.py` | Route boundaries, color starts, safe squares |
| `Game/models.py` | Pieces, players, state, moves, results, fresh matches |
| `Game/dice.py` | Private seeded random generator |
| `Game/rules.py` | Validation, board mapping, destinations, landing/path legality, winning |
| `Game/engine.py` | Apply moves/captures, collect rolls, resolve rolls, forfeit turns |
| `Game/audit.py` | Independent snapshots, transition records, JSONL trace saving |
| `Game/errors.py` | Invalid-move and agent retry-limit exceptions |
| `Agents/random_agent.py` | Choose randomly from legal moves |
| `run_game.py` | Automated game loop and agent snapshot/retry handling |
| `human_play.py` | Human-versus-random terminal interface |
| `Experiments/results_io.py` | Validate, append, and load game summaries |
| `Experiments/run_config.py` | Create/reuse compatible experiment settings |
| `Experiments/batch.py` | Fresh batches, resumable runs, summary statistics |
| `Check.py` | Short capture demo only |
| `Tests/` | All 74 regression tests, including foundations and trace checks |
| `Results/` | Generated experiment files; not source code |

## Connections

```text
Human input / random agent → selected Move
                                  ↓
runner → engine → rules → GameState → Players → Pieces
           ↑
       seeded Dice

experiment settings → run_game → GameResult → JSONL → summary
```

Agents receive copies when called through `play_agent_roll()`; only the engine applies their choice to the live state. Human play uses a separate entry point and does not save random-only research records.

## Pending work

1. Finish the student's manual game review and persistent interface tests; fix demonstrated bugs. Trace collection and a bounded rules/test review are already implemented.
2. Add heuristic opponents and configurable agent assignments. Rotating the starting player is not the same as rotating agent types through seats.
3. Build the RL interface: observations, single/pair actions, legal masks, and separate reward calculation.
4. Connect PPO/self-play, held-out evaluation, behavior metrics, multiple seeds, and uncertainty estimates.

Future organization under `RL/` and `Configs/` is flexible; folder names do not imply implemented functionality. Persistent transition logs are implemented; RL training is not.

## Navigating the tests

| Area | Files under `Tests/` |
|---|---|
| Basics and game rules | `test_foundations.py`, `test_rules_validation.py`, `test_legal_moves.py`, `test_engine.py`, `test_turns.py` |
| Agents and experiments | `test_runner.py`, `test_action_recovery.py`, `test_results_io.py`, `test_run_config.py`, `test_experiment.py` |
| Audit evidence | `test_audit.py`, `test_trace.py` |

Tests are grouped by responsibility; they do not add gameplay features. Run them together with unittest discovery. Foundation checks moved out of `Check.py` so no separate test command is needed.
