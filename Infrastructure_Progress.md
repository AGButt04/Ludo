# Infrastructure Progress

Updated November 1, 2026. Working engine v1 and experiment infrastructure; no RL training or research findings yet. New tasks are explained in chat unless the student requests otherwise.

## Current status

- Two-/four-player random games and four-player human terminal play work under [Rules.md](Rules.md).
- Seeded batches, summaries, config checks, resuming, result validation, and agent-state isolation are implemented.
- Optional persistent traces record starts, rolls/cancellations, moves/passes, rejections, forfeitures, and endings. Snapshots contain relative positions; shared squares and captures can be derived from them.
- Completed a bounded rule-coverage review and inspected four events from seed 0: capture (turn 54), safe-blockade passage (187), cancellation (45), and winning move (505).
- Full manual human game review and persistent interface tests remain pending. This is evidence for working engine v1, not exhaustive correctness.

## Verification and commands

```bash
python3 Check.py                         # Short capture demo only
python3 run_game.py                      # One random-agent game
python3 human_play.py                    # Human red versus three random agents
python3 -m unittest discover -s Tests -q # All 74 tests, including foundations
```

The foundation tests formerly in `Check.py` now live in `Tests/test_foundations.py`; no checks were removed. Before cleanup there were 65 main plus nine foundation tests; now the same 74 are discovered together.

Earlier audit checks covered 16 seeded games (two/four players), 3,846 moves, and selected transition properties. Trace tests check movement arithmetic, captures, continuity, counters, and turn progression without using the engine's destination helper. These do not prove every legal-choice set complete. Additional targeted tests cover friendly pairs, safe release, private home paths, and rejected actions.

Cleanup verification passed: all 74 tests, the capture demo, a random-game run, and a human input/move/quit smoke check. Eight seeded games produced identical results and complete trace hashes before/after; existing result files were unchanged. No gameplay-rule changes were made.

## Completed implementation tasks

| Task | Purpose |
|---|---|
| 1. Board constants | Define track, yard, home path, and finish positions. |
| 2. Piece | Store owner, piece ID, and progress. |
| 3. Player | Assign a color and create four independent pieces. |
| 4. GameState | Store players, current turn, and rolls. |
| 5. Fresh match | Create independent two-/four-player games. |
| 6. Seeded dice | Produce reproducible rolls. |
| 7. Candidate destination | Calculate release, movement, and exact finishing. |
| 8. Shared-board mapping | Convert relative progress to absolute squares. |
| 9. Square occupancy | Find pieces on a shared square. |
| 10. Rule discussion | Document the agreed variant; remaining decisions stay in Rules.md. |
| 11. Safe squares | Identify capture-protected squares. |
| 12. Piece counts | Count one player's pieces at a shared square. |
| 13. Move | Represent selecting one piece or a pair. |
| 14. Shared path | Find shared squares crossed by a move. |
| 15. Blockade detection | Identify same-player pairs. |
| 16. Path obstruction | Block singles at opposing unsafe blockades. |
| 17. Legal choices | Combine destinations, path checks, and landing rules. |
| 18. Apply moves and detect wins | Move pieces, capture opponents, and recognize a winner. |
| 19. Turn progression | Collect rolls, cancel three sixes, consume choices, and advance players. |
| 20. Random-agent games | Run complete seeded games with a turn limit. |
| 22. GameResult | Store outcome, settings, turns, moves, and cutoff status. |
| 23. Return game summaries | Populate GameResult from the runner. |
| 24. Result file I/O | Append and reload game summaries as JSON Lines. |
| 25. Batch games and statistics | Vary seeds, rotate starting seats, save games, and summarize results. |
| 26. Run identity/config | Reuse compatible settings; reject incompatible/orphaned results. |
| 27. Resume experiments | Fill missing games without duplicates; rotate starting seats. |
| 28. Invalid-action recovery | Retry choices; forfeit remaining turn after three rejections; count failures. |
| 30. Agent isolation | Pass fresh deep copies of state and legal choices on each attempt. |
| 31. Result validation | Check field types, ranges, outcomes, and counter bounds before save/load/summary. |
| 32. Documentation | Updated map, walkthrough, rules/status, and run commands. |

## Task 21 — Gameplay audit

**Status:** Trace implementation and bounded automated/selected-event review complete. Full manual review remains open; do not describe the entire game as manually inspected.

`Game/audit.py` provides snapshots, action records, and JSONL saving. `run_game(trace=records)` collects events without changing sampled results. `Results/audit_seed_0.jsonl` preserves the reviewed game. The trace is diagnostic evidence, not PPO experience data or a proof of legal-choice completeness.

## Task 29 — Human terminal play

**Status:** Implemented. Numbered choices, input retries, quit/end-of-input, random opponents, passes, and compact move/capture reports work in focused checks. Student plans to play a full game; persistent interface tests remain pending.

## Next direction

Finish the planned manual review and address demonstrated bugs. Next development discussion: define one simple heuristic agent and how to select opponents in the runner. After that: RL observations/actions/masks, separate rewards, PPO, then controlled experiments. No new RL/network claims yet.

## Workflow

Explain → student implements → review/fix → test. Keep chunks understandable, preserve the student's code ownership, and avoid repeating demo edits or adding speculative infrastructure. The user authorized this cleanup; useful tests and existing results are retained.
