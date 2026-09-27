# Ludo RL

A senior Computer Science research project building a reproducible Ludo simulator and reinforcement learning experiment platform.

## Research goal

Investigate how training opponents and reward design affect PPO agents’ learning speed, performance against unfamiliar opponents, and behavior in four-player Ludo. The research question is provisional.

## Current progress

- Board constants, piece/player models, and basic game state.
- Fresh two- and four-player match creation.
- Seeded dice and basic destination calculation.
- Nine automated checks for the implemented foundations.

Shared-board mapping, full game rules, PPO training, self-play, and experiment analysis are planned; the simulator is not yet complete.

## Run the checks

Requires Python 3.10 or newer. No third-party packages are needed yet.

From the `Ludo RL` workspace root:

```bash
cd "Environment and Implementation"
python3 Check.py
```

## Project layout

- `Environment and Implementation/` — source code, checks, walkthrough, and progress notes.
- `Research and Thesis/` — research papers and thesis materials.

Development proceeds one small, explained, and tested component at a time.
