# Infrastructure Progress

Updated October 14, 2026. Tasks 1–20 and 22–25 are complete; Task 21 is deferred. Rule decisions and remaining questions live in [Rules.md](Rules.md).

## Completed tasks

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

## Current verification and usage

- Last regression run: **41 tests passed**. Batch checks also covered repeatability, file preservation, empty/all-cutoff inputs, and mixed player-count rejection.
- `python3 Check.py`: eight-game batch demo, saved to a fresh timestamped file in `Results/`, then read back and summarized. This replaces the originally proposed separate batch-module demo.
- `python3 run_game.py`: one random-agent game with a short outcome summary.
- Win rates use completed games; average turns/moves include all games. Cutoffs are reported separately, not treated as draws or losses.
- A turn is a full roll sequence, including cancelled turns. A move is one applied single/pair action; forced passes are not moves.
- JSONL files currently contain game summaries, not move traces or complete research metadata. Passing checks does not replace the deferred audit.

Full regression command (from this folder):

```bash
python3 -m unittest Check Tests.test_rules_validation Tests.test_legal_moves Tests.test_engine Tests.test_turns Tests.test_runner Tests.test_results_io -q
```

## Task 21 — Full-game audit (deferred)

Postponed at the student's request; not implemented or reviewed. Return before relying on experimental findings.

1. **Trace:** Add optional logging in `run_game.py` and a new `Game/audit.py`. Record settings, full roll sequences (including cancelled turns), legal choices, selected move/pass, captures, all piece positions before/after, and next player. Include relative and absolute positions; preserve cancelled rolls without extra dice calls.
2. **Check transitions:** Verify movement, captures, safe squares, blockades, occupancy, finishing, forced passes, and turn changes. Report seed/turn on failure. Use hand-calculated cases as well as automated checks; reusing legal_moves alone can repeat its bugs.
3. **Review:** Inspect one full seeded four-player game in manageable sections, then check multiple seeds/player counts/starting seats. Confirm logging does not change gameplay. Record coverage, fixes, and remaining gaps before marking complete.

Start with explaining the optional trace. No new implementation task is active after Task 25; agree on the next step with the student.

## Workflow

Explain → student implements → review/fix → test → update this file. Add small tasks of 2–3 connected methods; condense completed instructions after another 8–10 tasks. Keep Check.py limited to the current demo. Broader direction: audit the engine, add heuristic opponents, then RL integration and experiments.
