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

**Status:** Core rules agreed; edge cases below remain open. Safe-square lookup is implemented; blockade movement/enforcement is not.

- Keep red as shared square 1. Safe squares are `1, 9, 14, 22, 27, 35, 40, 48`. Rotating the numbering by a whole color interval preserves this set.
- Different players may share safe squares without capture.
- Two same-player pieces form a blockade. On unsafe squares, an opposing single piece cannot pass it. On safe squares, other players may pass the blockade, including with single pieces. Own pieces may pass their own blockade.
- A player may split a blockade by moving one piece the full rolled distance. Splitting never grants a free move; odd rolls can move a single piece but not an intact pair.
- Moving the pair requires an even roll: 2 → 1 square, 4 → 2, 6 → 3.
- An intact pair cannot land on another friendly blockade. There may be only one blockade per square.
- A player must choose a legal move whenever one exists; passing is allowed only when none exists. Splitting is forced only when every available legal move requires it.
- Example: friendly pairs on squares 3 and 4, roll 2. Pair 3 → 4 is illegal; pair 4 → 5 may move intact if otherwise legal. A single piece may instead split from either pair and move two squares if otherwise legal.
- Opposing blockades may pass each other. Capturing an opposing pair requires a moving pair to land exactly on its square; both captured pieces return to the yard. Safe-square protection still applies.
- Board numbering does not decide who starts. The engine must support any participating player starting; seeded random selection versus explicit selection is still to be specified.

**Remaining decisions before pair movement:** Whether a single piece may land on a friendly blockade (creating a three-piece stack), how opposing pairs coexist on safe squares under the one-blockade limit, how pairs enter/finish the private home path, and whether a pair can capture a single piece on an unsafe square. Turn bonuses remain undecided.

**Next coding step:** Blockade detection using the completed occupancy/count helpers. Moving pairs will require an action that identifies two pieces, rather than only a single piece ID.

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

**Connection:** This takes an absolute shared-square number, not relative progress. Later, convert a piece's position using `to_absolute()` first; do not pass `None` into this helper. Safety prevents captures and allows opponents to pass blockades on that square.

**Completion log:** All 52 shared squares and invalid type/range inputs checked successfully. Nine existing tests also passed. Safe-square examples were checked; `Check.py` now shows the latest task only.

## Task 12 — Count a player's pieces on a square

**Status:** Complete. **File:** `Game/rules.py`.

**Purpose:** Distinguish two pieces belonging to one player from two pieces belonging to different players—the basis of blockade detection.

**Steps:**
1. Define `count_pieces_at(state: GameState, square: int, player_id: int) -> int`.
2. Reject non-integer player IDs with `TypeError` and IDs absent from `state.players` with `ValueError`.
3. Call `pieces_at(state, square)`; it already validates the square.
4. Start a counter at zero. Loop over the returned pieces and increment it when `piece.player_id == player_id`.
5. Return the count. Do not change state or exclude safe squares.

**Check:** Two red pieces on square 14 give red a count of 2. One red and one green there give each a count of 1. An empty square gives 0. Non-integer/absent player IDs raise errors.

**Connection:** A same-owner count of 2 identifies the agreed pair. Counting also handles larger stacks without deciding their rules yet; those remain open. Later legal-move checks will distinguish friendly and opposing blockades.

**Completion log:** Counting, mixed ownership, empty squares, invalid IDs/squares, and nonconsecutive participating IDs passed checks. Nine existing tests also passed. No code corrections needed after the indentation fix. `Check.py` now shows only four piece-count examples.

**October 2 audit:** Removed two stray backticks in `count_pieces_at()` that caused a syntax error. Current demo, nine foundation tests, and targeted mapping/occupancy/safety/count checks passed. README, walkthrough, map, and research status refreshed. Complete move enforcement, game loop, and agents are not implemented yet.

## Task 13 — Represent a chosen move

**Status:** Complete. **File:** `Game/models.py`.

**Purpose:** Give the engine and every agent one format for choosing a single piece or a pair.

**Steps:**
1. Add a `Move` dataclass with `player_id: int` and `piece_ids: tuple[int, ...]`. The tuple lists which pieces will move; it does not contain positions.
2. In `__post_init__`, require an integer player ID in 0–3, and a tuple containing one or two distinct integer piece IDs in 0–3. Reject wrong types (including booleans) with `TypeError`, and invalid values/counts/duplicates with `ValueError`.
3. Keep the class limited to describing a choice. Do not move pieces or calculate destinations here.

**Examples:** `Move(0, (2,))` selects red piece 2. `Move(0, (0, 1))` selects red pieces 0 and 1 together. The comma in `(2,)` makes it a one-item tuple.

**Check:** Both examples construct successfully. Empty tuples, three IDs, duplicate IDs, out-of-range IDs, and wrong types are rejected.

**Connection:** Later legal-move generation returns `Move` objects; an agent chooses one; the engine applies it using the pending roll. State-dependent checks (ownership in this match, pieces forming a pair, clear path, valid destination) belong in the rules engine, not this model.

**Completion log:** Removed state coupling, corrected the piece-ID upper bound, and added count/type/duplicate checks. Single/pair examples and invalid-input checks passed, along with nine existing tests.

## Task 14 — List the shared squares crossed

**Status:** Complete. **File:** `Game/rules.py`.

**Purpose:** Let later legality checks inspect the whole path for blockades, not just the landing square.

**Steps:**
1. Define `shared_path(color: Color, position: int, destination: int) -> list[int]`. Both input positions are relative progress; the returned squares are absolute.
2. Require a `Color` and integer positions (reject booleans); wrong types raise `TypeError`. Require `YARD <= position < destination <= FINISHED`; otherwise raise `ValueError`.
3. Start an empty list. Loop through `range(position + 1, destination + 1)` to exclude the origin and include the destination.
4. Convert each relative position with `to_absolute(color, relative_position)`. Append it only when the result is not `None`.
5. Return the list without changing state.

**Examples/checks:** Red `3 → 5` returns `[4, 5]`; blue `12 → 15` returns `[52, 1, 2]`; red `50 → 54` returns `[51]`; red `52 → 54` returns `[]`; red release `0 → 1` returns `[1]`. Reject equal/backward positions, out-of-range inputs, and wrong types.

**Connection:** This helper traces an already calculated candidate move. It does not check the dice, pair movement, or occupancy. Later rules inspect this path for opposing blockades on unsafe squares; landing/capture checks remain separate.

**Completion log:** Fixed `postion` typo and rejected equal endpoints. Corrected the earlier blue example: the origin square 51 is excluded. Path examples and invalid-input checks passed, as did nine foundation tests. `Check.py` displays only path examples.
