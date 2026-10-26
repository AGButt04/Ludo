# Ludo RL

A senior CS project building a reproducible Ludo simulator and reinforcement learning research platform.

## Research goal

Investigate how training opponents and reward design affect four-player PPO agents' learning speed, performance against unfamiliar opponents, and behavior. The question is provisional; novelty and paper compatibility still need verification.

## Current progress

- Two-/four-player games with movement, captures, safe squares, blockades, turn sequencing, and first-winner termination.
- Seeded random agents and terminal play against three random opponents.
- Batch runs, JSONL results, summaries, and resumable experiments without duplicate games.
- Agent snapshots, invalid-choice recovery, and saved-result validation.

Working gameplay is not a completed correctness audit. Pending: persistent human-interface tests, full-game tracing/review, broader automated checks, heuristic opponents, RL observations/actions/rewards, PPO, self-play, and research evaluation.

## Run

Python 3.10+; no third-party packages currently required. From `Environment and Implementation/`:

```bash
python3 human_play.py                         # Play as red; q quits at your prompt
python3 run_game.py                           # One random-agent game
python3 Check.py                              # Resume demo using temporary files
python3 -m unittest discover -s Tests -q      # Tests/ suite
python3 -m unittest Check -q                  # Additional foundation checks
```

## Read next

- [Project_Map.md](Project_Map.md): files and connections.
- [Code_Walkthrough.md](Code_Walkthrough.md): how the current code works.
- [Rules.md](Rules.md): our specific Ludo variant and research implications.
- [Infrastructure_Progress.md](Infrastructure_Progress.md): tasks and verification status.
- [Research_Progress.md](Research_Progress.md): literature and candidate questions.

Development proceeds in small, explained, and tested steps.
