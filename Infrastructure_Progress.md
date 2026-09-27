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
