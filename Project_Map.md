# Ludo RL — Project Map

**Status:** Folders created; Python/configuration files below are planned, not implemented. We will approve and build one small part at a time.

**Location:** Everything below lives inside `Environment and Implementation/`. Research papers stay in `Research and Thesis/`.

## Bird’s-eye view

```text
Environment and Implementation/
├── Code_Walkthrough.md       Teaching examples and agreed assumptions
├── Research_Progress.md      Research questions, literature, advisor updates
├── PROJECT_MAP.md            This map
├── pyproject.toml            Planned dependencies and test configuration
├── game/                    Ludo simulator
├── agents/                  Ways to choose moves
├── rl/                      Learning interface and PPO training
├── experiments/             Run, evaluate, and analyze experiments
├── configs/                 Experiment settings
├── tests/                   Correctness checks
└── results/                 Generated outputs
```

## Planned files and responsibilities

| Folder | Files | Task for each file |
|---|---:|---|
| `game/` | 6 | `constants.py`: board boundaries, starts, colors, safe squares. `models.py`: Piece, Player, GameState. `rules.py`: coordinate mapping, destinations, legal moves, capture/blockade checks. `engine.py`: seeded dice, apply moves, turns, reset, victory. `events.py`: structured roll/move/capture/finish records. `__init__.py`: marks the Python package. |
| `agents/` | 4 | `base.py`: common action-selection interface. `random_agent.py`: uniformly choose a legal move. `heuristic_agent.py`: aggressive, defensive, fast, and mixed strategies. `__init__.py`: package marker. |
| `rl/` | 5 | `environment.py`: reset/step, opponent turns, action masks, episode endings. `observations.py`: encode state for the learner. `rewards.py`: sparse/shaped feedback and penalties. `train.py`: connect a PPO library, self-play opponents, checkpoints, policy loading. `__init__.py`: package marker. |
| `experiments/` | 4 | `run.py`: read settings and launch training/evaluation runs. `evaluate.py`: frozen-policy games, opponent lineups, seats, game logs. `analyze.py`: aggregate seeds, uncertainty, behavioral metrics, tables/plots. `__init__.py`: package marker. |
| `configs/` | 1 | `experiment.json`: ruleset choice, agent settings, reward mode, seeds, budgets, evaluation settings, output location. Additional configurations can be added later. |
| `tests/` | 7 | `test_constants.py`: board definitions. `test_models.py`: initialization and independence. `test_rules.py`: legal moves and interactions. `test_engine.py`: turn sequences, deterministic replay, complete games. `test_agents.py`: legal choices and heuristic examples. `test_environment.py`: observations, masks, reset/step, termination. `test_rewards.py`: event-to-reward calculations. |
| `results/` | 0 fixed | Generated per-run configurations, logs, checkpoints, metrics, and plots. File counts depend on experiments. |

**Count:** 7 subfolders and 31 planned fixed project files: 27 inside subfolders plus 4 at the root. Three root documents exist now; the other 28 files will be created gradually. Counts describe the initial design, not a permanent limit. Each Python package includes its small `__init__.py` file. Generated output folders/files are excluded.

## How they connect

```text
configs/experiment.json
          ↓
experiments/run.py
          ├── rl/train.py → rl/environment.py → game/engine.py
          │                      │                    ├── models.py
          │                      ├── observations.py  ├── rules.py → constants.py
          │                      ├── rewards.py       └── events.py
          │                      └── agents/ (opponents)
          │
          └── experiments/evaluate.py → frozen agents + engine
                         ↓
                      results/
                         ↓
                 experiments/analyze.py
                         ↓
                Tables, plots, findings
```

The engine returns state changes and events; the RL layer turns them into observations and rewards. Agents select legal moves without changing the state themselves. Evaluation can load PPO policies through the same observation/mask conventions. The simulator does not depend on PPO or rewards.

## Build order

1. Approve the board route, then `constants.py` and its tests.
2. Build models, movement/rule functions, and the engine incrementally with tests.
3. Add the random agent and run complete games; then heuristics and event logs.
4. Add the RL interface, reward options, and a small PPO training run.
5. Add self-play and experiment controls; evaluate and analyze pilot runs.

Start with command-line controls. A visual board or dashboard can be added after the engine works; it is not required to begin research experiments. Tests grow alongside implementation rather than being postponed until the end.
