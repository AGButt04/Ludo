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

**Task 5 review:** `initial_state(num_players)` creates independent two-/four-player matches with correct IDs, yard positions, and state defaults. Invalid inputs are rejected. Corrected the non-integer exception to `TypeError`; all checks passed. Player count is supplied explicitly.

**Current seating:** IDs determine colors; two players currently means red and green. Final seating policy remains open.

**Latest verification:** All nine tests in `Check.py` passed, including seeded dice, movement boundaries, and invalid movement inputs. Candidate destinations do not yet account for other pieces, safe squares, or blockades.

## Task 8 — Map a piece to the shared board

**Status:** Not started. **Files:** `Game/constants.py`, `Game/rules.py`.

**Purpose:** Convert relative progress into a shared square so we can later detect captures, safe squares, and blockades.

**Steps:**
1. In `constants.py`, add `START_SQUARES = (1, 14, 27, 40)` for red, green, yellow, blue. This defines our logical numbering in the direction of travel.
2. In `rules.py`, import `Color` from `Game.models` and the needed constants: `YARD`, `FINISHED`, `TRACK_START`, `TRACK_END`, `TRACK_LENGTH`, `START_SQUARES`.
3. Define `to_absolute(color: Color, position: int) -> int | None`.
4. Require `isinstance(color, Color)` and `type(position) is int`; otherwise raise `TypeError`. Positions outside `YARD`–`FINISHED` raise `ValueError`.
5. For valid positions outside `TRACK_START`–`TRACK_END`, return `None`: yard, private home path, and finish have no shared square.
6. Set `start = START_SQUARES[color]`, then return `((start - 1 + position - 1) % TRACK_LENGTH) + 1`. Subtracting one uses zero-based arithmetic; modulo wraps the track; adding one restores square numbers 1–52.

**Connection:** Call `to_absolute(player.color, piece.position)`. Do not change the piece or store a duplicate absolute position.

**Check:** Each color at position `1` maps to its start. Red `14` and green `1` both map to `14`; blue `14` wraps to `1`. Positions `0`, `52`, `56`, and `57` return `None`. Invalid colors, fractional/boolean positions, and positions `-1`/`58` raise errors.

**Scope:** Coordinate conversion only—no 2D display or interaction rules yet.

**Completion log:** Pending your code and our review.
