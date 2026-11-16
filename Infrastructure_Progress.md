# Infrastructure Progress

Updated November 1, 2026. Working engine v1 and experiment infrastructure; no RL training or research findings yet. New tasks are explained in chat unless the student requests otherwise.

## Current status

- November 13 design handoff: [Personal_Agent_Design.md](Personal_Agent_Design.md)
  records Abdul's proposed heuristic, essential definitions, and open priority decisions.
  Implementation details are intentionally left for discussion. This is a design
  milestone only; no personal-agent implementation or new test results are claimed.

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

## Task 33 — Personal agent: identify immediate wins

**Status:** Complete for these two helpers. `simulate_move()` and `winning_moves()` verified for single/pair wins, non-winning finishes, empty choices, and unchanged input state/choices. All 76 tests pass. Move selection and runner integration are not implemented yet. **File:** `Agents/AGB.py`.
**Purpose:** Implement Rule 1 of `Personal_Agent_Design.md`: recognize a move that wins the whole game, without changing the real board.

1. Create `PersonalAgent`. Add `simulate_move(self, state, move) -> GameState`: deep-copy the state, call `play_turn(copy, move)`, and return the copy. Inputs are a state with a pending roll and a legal move.
2. Add `winning_moves(self, state, moves) -> list[Move]`: remember the current player's ID, simulate each supplied legal move on a fresh copy, and collect moves for which `has_won(copy, player_id)` is true. Return `[]` if none wins.

**Example:** Positions `[57, 57, 57, 56]`, roll 1: moving piece 3 wins. Finishing one piece while others remain outside does not count as winning.
**Checks after review:** Single-piece win, pair finish that wins, non-winning finish, empty choices, and original state/rolls unchanged. No runner integration or fallback priorities yet; known-roll planning comes later. Build the full design gradually and document conflicts when resolved.

## Task 34 — Personal agent: detect single-roll capture threats

**Status:** Complete. Verified single/pair captures, splitting a pair, later opponents, blocked routes, protected positions, ended games, and unchanged inputs. All 78 tests pass. **File:** `Agents/AGB.py`.
**Purpose:** Support Rule 2 by identifying possible captures, without choosing a defensive move yet.
1. Add `capture_threats(self, state, player_id, piece_id) -> list[tuple[int, int]]`. Resolve the target by IDs using existing lookup helpers. Yard, private-home, finished, and safe-square pieces return `[]`.
2. On copies, consider each other player acting with each roll 1–6. Set their current-player index, replace the pending roll, clear remaining rolls, and generate legal choices. Simulate choices; if the target is captured, record `(opponent_id, roll)` once for that roll.
3. Test singles/pairs, unsafe blockades, safe/private squares, and unchanged inputs. Return no threats for an ended game. This is a hypothetical single-roll test on the supplied board, not a forecast of intervening moves, extra rolls, or opponent preferences. Known-roll plans will evaluate threats after our own sequence.

**Example:** Red at relative 16 and Green at relative 1: Green can capture Red with a 2, so include `(1, 2)` if that move is legal. This is possible capture, not a probability estimate.

## Task 35 — Personal agent: list threatened pieces

**Status:** Complete. Ordering, current-player ownership, empty results, and unchanged state verified; all 79 tests pass. **File:** `Agents/AGB.py`.
**Purpose:** Give Rule 2 the current player's threatened pieces, most advanced first; defensive move selection follows later.
1. Add `threatened_pieces(self, state)`: loop through `state.current_player().pieces` and collect pieces whose `capture_threats(state, player.player_id, piece.piece_id)` is nonempty.
2. Sort the collected list by `piece.position`, descending, and return it. Do not change positions or sort the player's original list.
**Checks:** Empty result when safe; multiple threatened pieces ordered by progress; only current player's pieces; original state unchanged. Equal progress does not yet decide which defensive move to choose.

## Task 36 — Personal agent: find protective moves

**Status:** Complete for immediate-move protection. Verified advanced-piece preference, fallback to a savable piece, indirect protection, no-saving/no-threat cases, and unchanged inputs. All 80 tests pass. Full known-roll planning and agent move selection remain pending. **File:** `Agents/AGB.py`.
**Purpose:** Rule 2's immediate-move helper: return legal choices that remove all threats to the most advanced savable piece.
1. Add `protective_moves(self, state, moves)`. Visit `threatened_pieces(state)` in its existing order.
2. For each threatened piece, simulate every supplied legal move independently. Collect moves for which that piece has no capture threats afterward (look it up using its original IDs).
3. Return the collected moves for the first savable piece; otherwise continue to the next piece. Return `[]` if none can be saved. A move may save a piece indirectly, such as capturing its attacker; do not restrict to moves selecting that piece.
**Checks:** Advanced savable piece preferred; unsavable advanced piece skipped; no protection returns empty; indirect protection; state unchanged. Return all qualifying moves without inventing a tie-break. Full stored-roll planning remains Rule 9; this helper alone does not complete the full agent.

## Workflow

Explain → student implements → review/fix → test. Keep chunks understandable, preserve the student's code ownership, and avoid repeating demo edits or adding speculative infrastructure. The user authorized this cleanup; useful tests and existing results are retained.

November 15 preference: resume concise task instructions in this file alongside explanations in chat. Understanding takes priority over presentation deadlines.
