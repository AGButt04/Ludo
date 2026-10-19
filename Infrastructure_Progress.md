# Infrastructure Progress

Updated October 16, 2026. Tasks 1–20 and 22–25 are complete; Tasks 26–27 are complete; next return to deferred Task 21. Rule decisions and remaining questions live in [Rules.md](Rules.md).

## Current focus — Understand the existing code

The student requested a code-understanding phase; on October 18 they selected Tasks 28–29 for the next session (October 19), with explanations before implementation. Work through small reading groups: student writes purpose/input/output/side-effect comments, then explains concrete examples; review comments and ask prediction questions before advancing. Correct inaccurate comments briefly, as requested; let the student draft each new group first.

October 18 bookmark: reviewed models, dice, movement/mapping, occupancy, blockades, legal choices, and `apply_move()`. Reviewed/corrected comments for `roll_turn()` and `play_turn()` at the end of the session; start next time with a brief explanation check for those two. Validation/lookup helpers and `has_won()` still need a focused review, followed by agents/runner and results/configuration/batches. Understanding review is not yet complete; Task 21 remains deferred.

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

- Last regression run (October 17): **49 tests passed**. Batch checks also covered repeatability, file preservation, empty/all-cutoff inputs, and mixed player-count rejection.
- `python3 Check.py`: resume demo in a temporary folder—save two games, resume to five, then call again with no new games. Checks preserved results and unchanged file; temporary files are automatically removed.
- `python3 run_game.py`: one random-agent game with a short outcome summary.
- Win rates use completed games; average turns/moves include all games. Cutoffs are reported separately, not treated as draws or losses.
- A turn is a full roll sequence, including cancelled turns. A move is one applied single/pair action; forced passes are not moves.
- JSONL files currently contain game summaries, not move traces or complete research metadata. Passing checks does not replace the deferred audit.

Full regression command (from this folder):

```bash
python3 -m unittest Check Tests.test_rules_validation Tests.test_legal_moves Tests.test_engine Tests.test_turns Tests.test_runner Tests.test_results_io Tests.test_run_config Tests.test_experiment -q
```

## Task 21 — Full-game audit (deferred)

Postponed at the student's request; not implemented or reviewed. Return before relying on experimental findings.

1. **Trace:** Add optional logging in `run_game.py` and a new `Game/audit.py`. Record settings, full roll sequences (including cancelled turns), legal choices, selected move/pass, captures, all piece positions before/after, and next player. Include relative and absolute positions; preserve cancelled rolls without extra dice calls.
2. **Check transitions:** Verify movement, captures, safe squares, blockades, occupancy, finishing, forced passes, and turn changes. Report seed/turn on failure. Use hand-calculated cases as well as automated checks; reusing legal_moves alone can repeat its bugs.
3. **Review:** Inspect one full seeded four-player game in manageable sections, then check multiple seeds/player counts/starting seats. Confirm logging does not change gameplay. Record coverage, fixes, and remaining gaps before marking complete.

Return to the optional trace after the newly prioritized Tasks 28–29. The full audit is still unfinished.

## Task 26 — Reuse the demo and identify experiment runs

**Status:** Complete. Fixed-file demo and config creation/reuse verified. Fixed seed type, added range checks, and completed config comparison, orphan-results rejection, and results-path return. All 45 tests pass; configuration tests use temporary folders. **Files:** `Check.py`, new `Experiments/run_config.py`.
**Purpose:** Stop duplicate demo files and give each experiment run fixed, recorded settings.

1. In `Check.py`, use `Results/demo_batch.jsonl` instead of a timestamp. If it exists, load and summarize it; otherwise run/save the eight-game demo. Print whether results were loaded or generated. Leave old files untouched.
2. Add `prepare_run(run_dir, base_seed, num_players, max_turns) -> Path`: validate the settings, then create/read `config.json` inside that directory. Store those settings plus `schema_version=1`, `rules_version=1`, `agent_type="random"`, and `starting_seat_policy="rotate"`. If an existing config differs, raise an error; never overwrite it. Return the path to `games.jsonl` inside that directory. Reject existing game data without a config instead of assigning it new settings.
3. The directory identifies the run, e.g. `Results/random_run_001/`. Game ID is its zero-based index `i`; seed is `base_seed + i`, starting seat is `i % num_players`. For this initial format, derive the ID from the saved seed; no new GameResult field is needed. Version labels must change when incompatible rules/record formats change.

**Check:** Repeating the demo creates no extra records; identical config is accepted; changed config or unlabelled existing game data is rejected. Validate all inputs before creating files.

## Task 27 — Resume an experiment without duplicate games

**Status:** Complete. No implementation corrections needed in the final review. Verified two games → resume to five → repeat with zero new games; results match an uninterrupted run. Gap filling, extension, invalid records/settings, and unchanged saved data on rejection also checked. All 49 tests pass; checks used temporary directories. **File:** `Experiments/batch.py`.
**Purpose:** Request a total number of games and run only those not already recorded.

1. Add `run_experiment(target_games, run_dir, base_seed=0, num_players=4, max_turns=10000, max_new_games=None) -> list[GameResult]`. Keep the existing fresh-file `run_batch()` available. Validate positive integer counts (reject booleans); `max_new_games=None` means no per-call limit. Obtain the results path through `prepare_run()`.
2. Load saved results (or start empty if the file is missing). Verify each result matches the config, its derived game ID is in `0..target_games-1`, its starting seat matches that ID, and no IDs repeat. Reject inconsistent winner/cutoff records. Reject malformed data visibly, including an incomplete last JSON line; automatic crash-file repair is outside this task.
3. Loop through target game IDs, skipping those saved. Run each missing game with its assigned seed/seat and append immediately. Stop after `max_new_games` new games if supplied. Return all saved/new results in game-ID order. A saved cutoff is a recorded trial and is not rerun. Do not put target_games in the fixed config, so a run can later grow.

**Example:** Target 20 with `max_new_games=8` saves eight games. Call again without that limit: run only the remaining 12. Call a third time: run zero games and return the same 20 records.

**Check:** Resumed results equal an uninterrupted run; no duplicates or changed earlier lines; seeds/seats stay consistent; changed settings, duplicate IDs, and malformed records fail before new games are appended. One process writes each run—parallel writers and automatic recovery are deferred.

**Next-session order:** Task 28 → Task 29 → return to Task 21 trace and review. Implement and review one task at a time; no RL libraries yet.

## Task 28 — Recover from invalid choices

**Status:** In progress. Invalid-action guards, retries, and runner forfeiture handling verified. Three rejected choices forfeit the remaining turn, preserve earlier valid moves, and let the game continue. Retry limits reset per roll; forced passes never ask the agent. All 55 tests pass. Saving rejection/forfeiture records and recording the retry policy in experiment settings remain.
**Purpose:** Reject invalid human/agent choices and allow another attempt without losing the game.

**Current coding step:** Add required integer fields `invalid_choices` and `forfeited_turns` to `GameResult`; initialize both to zero in `run_game`. Count `len(rejections)` after a successful helper return and in the retry-limit handler before its `break`; increment forfeitures only in that handler. These are whole-game totals. Example: two rejected choices then a valid move adds 2 invalid choices and 0 forfeitures. Review tests and saved-record compatibility next; do not treat missing counters in old records as measured zeros. Update experiment schema/policy settings before resuming saved runs.

- Explain and implement a distinct invalid-action signal at the action boundary. Handle expected rejection in the caller; do not broadly catch unrelated engine exceptions as invalid moves.
- Request a fresh choice after rejection, preserving all piece positions, current player, pending rolls, and move/turn counts. Do not reroll or silently substitute a different move.
- Agreed October 19: allow at most **three rejected attempts per pending roll** for an automated agent (three attempts total if all fail). Reset the counter for the next roll. Human input may retry until valid or quit.
- After the third rejected attempt, the caller handles `AgentRetryLimitError` by forfeiting the rest of that agent's turn: clear current/later rolls, advance once, and continue the game. Preserve earlier valid moves from that turn. Record rejections and forfeitures separately from wins/cutoffs; never substitute a move. Explain the record format before implementing persistence.
- With no legal moves, neither agent nor human is asked for a choice: automatically call `play_turn(state, None)`. Consume only that roll; continue with stored rolls, or advance if none remain. No retry is charged and no fresh roll is generated during this pass.
- Check invalid choice → valid choice succeeds; wrong player, illegal pair, invalid pass, and malformed input cannot mutate state. Check retry exhaustion and ensure unexpected errors remain visible.

## Task 29 — Play against random agents in the terminal

**Status:** Planned; depends on Task 28. Start with a text interface, not a graphical board.
**Purpose:** Let the student play and inspect the engine directly.

- Add a separate human-play entry point using the existing engine, with one human seat and random opponents. Keep automated experiment runs free of input prompts.
- Show colors/player IDs, all piece positions (relative and shared absolute where applicable), current/remaining rolls, and numbered legal choices. Explain captures, forced passes, cancelled turns, and the winner.
- Parse input separately from game execution; reject bad entries and ask again. Let the user quit cleanly without reporting a completed game. Use Task 28 recovery for invalid action attempts.
- Automatically consume an unusable roll without prompting; display a short forced-pass message. Process any stored later rolls normally.
- Test invalid text/out-of-range choices followed by valid input, pair selection, no-move handling, and quit/end-of-input. Use a short interactive demo; human games should not be saved as random-only research trials.

**First step tomorrow:** Explain where rejection handling belongs, then implement and test it before adding terminal prompts. No code changes were made when recording this plan.

## Workflow

Explain → student implements → review/fix → test → update this file. Add small tasks of 2–3 connected methods; condense completed instructions after another 8–10 tasks. Keep Check.py limited to the current demo. Broader direction: audit the engine, add heuristic opponents, then RL integration and experiments.
