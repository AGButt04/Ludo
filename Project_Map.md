# Ludo RL — Project Map

Updated: October 2, 2026. Tasks 1–9, 11, and 12 complete; Task 10 records rules with open edge cases; future file organization is flexible.

## Current files

Inside `Environment and Implementation/`:

| File | Role |
|---|---|
| `Game/constants.py` | Position boundaries, starts, safe squares, and piece count |
| `Game/models.py` | Piece, Color, Player, GameState, initial_state |
| `Game/dice.py` | Private seeded dice generator |
| `Game/rules.py` | Destinations, coordinate mapping, occupancy, safety, and piece counts |
| `Check.py` | Nine foundation tests plus a current-task demo |
| `README.md` | Project introduction and run command |
| `Code_Walkthrough.md` | Explanation of current code |
| `Infrastructure_Progress.md` | Task status and checks |
| `Research_Progress.md` | Literature, candidate questions, advisor direction |
| `Project_Map.md` | This overview |

There are seven main subfolders: `Game`, `Agents`, `RL`, `Experiments`, `Configs`, `Tests`, and `Results`. Currently, five Python files and five Markdown documents make up the implementation workspace; generated caches and Git metadata are excluded. No fixed final file count is required.

## Future components (not implemented)

| Folder | Planned responsibilities |
|---|---|
| `Game/` | Extend rules with interactions/legal moves; add engine and events |
| `Agents/` | Common interface, random player, heuristic players |
| `RL/` | Environment wrapper, observations, rewards, PPO and self-play training |
| `Experiments/` | Run configurations, evaluate policies, analyze metrics |
| `Configs/` | Reproducible experiment settings |
| `Tests/` | Split checks here if they outgrow `Check.py` |
| `Results/` | Generated checkpoints, logs, tables, plots |

## Connections

```text
Current: initial_state → GameState → Players → Pieces
         Dice → roll value
         rules → candidate destination using constants

Planned: configuration → training → RL interface → game engine
                              ↓
                         saved policies → evaluation → analysis → findings
```

The engine will coordinate the current components, enforce rules, and record events. Rewards belong in the RL layer. No complete game loop exists yet.

Next discussion: blockade detection and remaining interaction rules, then legal moves. Continue one approved task at a time, with tests. A complete random-agent game comes before PPO.
