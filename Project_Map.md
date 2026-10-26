# Ludo RL — Project Map

Updated October 26, 2026. Working engine and experiment infrastructure; full audit and RL remain pending.

## Current files

Paths below are relative to `Environment and Implementation/`.

| File | Responsibility |
|---|---|
| `Game/constants.py` | Route boundaries, color starts, safe squares |
| `Game/models.py` | Pieces, players, state, moves, results, fresh matches |
| `Game/dice.py` | Private seeded random generator |
| `Game/rules.py` | Validation, board mapping, destinations, landing/path legality, winning |
| `Game/engine.py` | Apply moves/captures, collect rolls, resolve rolls, forfeit turns |
| `Game/errors.py` | Invalid-move and agent retry-limit exceptions |
| `Agents/random_agent.py` | Choose randomly from legal moves |
| `run_game.py` | Automated game loop and agent snapshot/retry handling |
| `human_play.py` | Human-versus-random terminal interface |
| `Experiments/results_io.py` | Validate, append, and load game summaries |
| `Experiments/run_config.py` | Create/reuse compatible experiment settings |
| `Experiments/batch.py` | Fresh batches, resumable runs, summary statistics |
| `Check.py` | Foundation tests and a short resume demonstration |
| `Tests/` | Rule, engine, runner, recovery, and storage tests |
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

1. Finish interface verification; trace and audit complete games against the written rules.
2. Add heuristic opponents and configurable agent assignments. Rotating the starting player is not the same as rotating agent types through seats.
3. Build the RL interface: observations, single/pair actions, legal masks, and separate reward calculation.
4. Connect PPO/self-play, held-out evaluation, behavior metrics, multiple seeds, and uncertainty estimates.

Future organization under `RL/` and `Configs/` is flexible; folder names do not imply implemented functionality. Persistent transition logs and RL training are not implemented.
