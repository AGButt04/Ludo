# Infrastructure Progress

Explain → implement → check → mark complete. Work one task at a time.

## Completed

| Task | File | Verified |
|---|---|---|
| 1. Board constants | `Game/constants.py` | Position values and path boundaries |
| 2. Piece | `Game/models.py` | IDs, yard default, independent positions, string output |
| 3. Player | `Game/models.py` | Four independent pieces, ownership; automatic ID-to-color mapping |
| 4. GameState | `Game/models.py` | Defaults, current-player lookup, storing a roll without moving pieces |
| 5. Fresh match | `Game/models.py` | Two/four players, independent matches, defaults, invalid-input rejection |
| 6. Seeded dice | `Game/dice.py` | Rolls in 1–6 and matching sequences for matching seeds |
| 7. Candidate destination | `Game/rules.py` | Yard release, movement, home entry, exact finish, overshoot, invalid inputs |
| 8. Shared-board mapping | `Game/rules.py` | Starting squares, overlap, wraparound, non-track positions, invalid inputs |
| 9. Square occupancy | `Game/rules.py` | Multiple occupants, empty squares, square 52, non-track exclusion, invalid inputs |

**Task 5 review:** `initial_state(num_players)` creates independent two-/four-player matches with correct IDs, yard positions, and state defaults. Invalid inputs are rejected. Corrected the non-integer exception to `TypeError`; all checks passed. Player count is supplied explicitly.

**Current seating:** IDs determine colors; two players currently means red and green. Final seating policy remains open.

**Latest verification:** All nine tests in `Check.py` passed, including seeded dice, movement boundaries, and invalid movement inputs. Candidate destinations do not yet account for other pieces, safe squares, or blockades.

**Task 8 verification (October 1):** Mapping and validation checks passed, alongside the nine existing tests. `python3 Check.py` runs only the current-task demo; `python3 -m unittest Check -v` runs the existing test suite.

**Task 9 verification (October 1):** Current demo, boundary/invalid-input checks, and nine existing tests passed.

## Delivery target — Before January 2027

- **October target:** Settle interaction/turn rules; implement legal moves, captures, turns, and winning. Reach a complete random-agent game.
- **November target:** Add hand-crafted heuristic agents, repeatable match runs, and event logs; test difficult rule interactions.
- **December target:** Fix defects, verify seating/reproducibility, and prepare a documented engine demonstration. Add manual play if desired. RL integration follows the verified engine.

These are planning targets, not completion guarantees. Continue one small approved task at a time.

## Task 10 — Safe squares and blockades

**Status:** Core rules agreed; edge cases below remain open. Rules are not implemented yet.

- Keep red as shared square 1. Safe squares are `1, 9, 14, 22, 27, 35, 40, 48`. Rotating the numbering by a whole color interval preserves this set.
- Different players may share safe squares without capture.
- Two same-player pieces form a blockade. An opposing single piece cannot pass it, including on safe squares. Own pieces may pass their own blockade.
- A player may split a blockade by moving one of its pieces normally.
- Moving the pair requires an even roll: 2 → 1 square, 4 → 2, 6 → 3.
- Opposing blockades may pass each other. Capturing an opposing pair requires a moving pair to land exactly on its square; both captured pieces return to the yard. Safe-square protection still applies.
- Board numbering does not decide who starts. The engine must support any participating player starting; seeded random selection versus explicit selection is still to be specified.

**Remaining decisions before pair movement:** How to handle three/four same-color pieces on a square, how pairs enter/finish the private home path, and whether a pair can capture a single piece on an unsafe square. Turn bonuses remain undecided.

**Next coding step:** Add safe-square constants and a lookup helper, then blockade detection. Moving pairs will require an action that identifies two pieces, rather than only a single piece ID.

## Task 11 — Identify safe squares

**Status:** Complete. **Files:** `Game/constants.py`, `Game/rules.py`.

**Purpose:** Tell capture rules whether a shared square protects its occupants.

**Steps:**
1. In `constants.py`, add `SAFE_SQUARES = (1, 9, 14, 22, 27, 35, 40, 48)`.
2. Import `SAFE_SQUARES` into `rules.py`.
3. Define `is_safe_square(square: int) -> bool`.
4. Reject non-integers (including booleans) with `TypeError`; reject values outside `1`–`TRACK_LENGTH` with `ValueError`.
5. Return `square in SAFE_SQUARES`. The `in` operator checks membership and gives `True` or `False`.

**Check:** Squares `1`, `9`, and `48` return `True`; `2` and `52` return `False`. Inputs `0`/`53` raise `ValueError`; `True`/`1.5` raise `TypeError`.

**Connection:** This takes an absolute shared-square number, not relative progress. Later, convert a piece's position using `to_absolute()` first; do not pass `None` into this helper. Safety prevents captures, not blockade obstruction.

**Completion log:** All 52 shared squares and invalid type/range inputs checked successfully. Nine existing tests also passed. `Check.py` now prints only the safe-square examples. Blockade detection comes next.
