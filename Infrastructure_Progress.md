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

**Task 5 review:** `initial_state(num_players)` creates independent two-/four-player matches with correct IDs, yard positions, and state defaults. Invalid inputs are rejected. Corrected the non-integer exception to `TypeError`; all checks passed. Player count is supplied explicitly.

**Current seating:** IDs determine colors; two players currently means red and green. Final seating policy remains open.

## Task 6 — Seeded dice

**Status:** Not started. **File:** `Game/dice.py`.

**Purpose:** Repeat dice sequences for debugging and research.

**Steps:**
1. Import `random`; create a regular `Dice` class.
2. In `__init__(self, seed: int | None = None)`, store `random.Random(seed)` as `self.rng`.
3. Add `roll(self) -> int`, returning `self.rng.randint(1, 6)`.

**Connection:** The future engine stores rolls in `GameState.dice_roll`; Dice does not change state or turns.

**Check:** Every roll is in 1–6. Two instances with the same seed produce matching sequences. Initialize once, not before every roll.

## Task 7 — Candidate destination

**Status:** Not started. **File:** `Game/rules.py`.

**Purpose:** Calculate a possible destination before changing a piece.

**Steps:**
1. Import `YARD`, `TRACK_START`, and `FINISHED`. Define `destination_for_roll(position: int, dice_roll: int) -> int | None`.
2. Reject non-integers/booleans with `TypeError`; reject positions outside 0–57 or rolls outside 1–6 with `ValueError`.
3. Yard: six returns `TRACK_START`; otherwise `None`. Finished: return `None`.
4. Otherwise return position + roll, or `None` if it overshoots `FINISHED`.

**Connection:** The engine supplies position and roll. No state changes, captures, or blockade checks yet. Assumes exact finish and no backward bounce.

**Check:** `(0,6)→1`, `(0,3)→None`, `(10,4)→14`, `(51,1)→52`, `(55,2)→57`, `(56,2)→None`, `(57,1)→None`; also invalid inputs.
