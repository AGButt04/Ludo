# Infrastructure Progress

Completed coding tasks below have been checked. Task 10 records agreed rules with remaining decisions in [RULES.md](RULES.md).

| Task | Purpose |
|---|---|
| 1. Board constants | Define the track, yard, home path, and finish positions. |
| 2. Piece | Store a piece's owner, ID, and progress. |
| 3. Player | Create four independent pieces and assign a color. |
| 4. GameState | Store players, current turn, and pending dice roll. |
| 5. Fresh match | Create independent two- or four-player starting states. |
| 6. Seeded dice | Generate repeatable dice sequences. |
| 7. Candidate destination | Calculate basic movement, release, and exact finishing. |
| 8. Shared-board mapping | Convert relative progress into a shared square. |
| 9. Square occupancy | Find pieces occupying a shared square. |
| 10. Rule discussion | Agree on safe squares and core blockade rules; some edge cases remain open. |
| 11. Safe-square lookup | Identify squares that protect pieces from capture. |
| 12. Piece counts | Count one player's pieces on a square. |
| 13. Move | Represent selecting a single piece or a pair. |
| 14. Shared path | List shared squares crossed by a candidate move. |
| 15. Blockade detection | Identify a same-player pair without enforcing movement rules yet. |

**Workflow:** Group 2–3 connected methods into each task. Explain, implement, test, and mark complete. Keep the instructions until another 8–10 tasks are done, then condense completed tasks into summary rows.

## Task 16 — Check whether a single piece's path is blocked

**Status:** Complete. **File:** `Game/rules.py`.

**Purpose:** Connect occupancy, blockade detection, and path mapping to reject passage through opposing pairs on unsafe squares.

### 1. `opponent_blockade_at(state, square, player_id) -> bool`

- `player_id` identifies the moving player. Call `count_pieces_at(state, square, player_id)` first to reuse its square/player validation; its count is not needed here.
- Loop through `state.players`, skipping the moving player's ID.
- If `has_blockade(state, square, opponent.player_id)` is true for any opponent, return `True`. Otherwise return `False` after the loop.
- This reports presence, even on safe squares. It does not decide whether passage is blocked.

### 2. `single_path_blocked(state, player_id, position, destination) -> bool`

- Validate the moving ID: integer (not bool), and present in `state.players`. Use `TypeError`/`ValueError` respectively.
- Find the matching `Player` by ID; do not use the ID as a list index.
- Get `shared_path(player.color, position, destination)`. This validates relative endpoints and includes the destination, excluding the origin.
- For each returned square, skip safe squares. If `opponent_blockade_at(...)` returns `True` on an unsafe square, return `True`.
- Return `False` after checking the whole path.

**Examples/checks:**
- Red moving relative `2 → 5`, with two green pieces at relative `43` (absolute square 4): blocked (`True`). Landing at red `4` is also blocked.
- Replace that pair with one green piece: not blocked (`False`).
- Two red pieces at square 4 do not block red's path.
- Two green pieces at relative `1` occupy safe square 14: their presence is `True`, but red's path `12 → 15` is not blocked.
- A path wholly in the private home lane has no shared blockers. Reject invalid IDs/endpoints and leave all piece positions unchanged.

**Scope:** Single-piece path obstruction only. `False` does not mean a fully legal move: dice, ownership of the selected piece, landing capacity, and capture checks come later. Do not use this function for moving pairs; they can pass opposing blockades. Existing guards still reject unsupported stacks larger than two when inspected.

**Completion log:** Fixed boolean-ID acceptance and ID-as-index lookup; safe squares are now skipped before blockade checks. Blocked paths/landings, friendly pairs, safe squares, home paths, reordered/nonconsecutive IDs, and invalid inputs passed checks. Nine foundation tests also passed. `Check.py` displays four current-task examples.

## Task 17 — Generate legal choices for a roll

**Status:** Complete: all three methods implemented and checked. **File:** `Game/rules.py`. Import `Move` from `Game.models`.

**Purpose:** Combine our helpers into the actual single/pair choices available to the current player. See [RULES.md](RULES.md) for the agreed variant.

### 1. `move_destination(state: GameState, move: Move, dice_roll: int) -> int | None`

- Validate an integer roll in 1–6. Find the player and selected pieces by their IDs, not list indexes; reject missing IDs with `ValueError`.
- One piece: reuse `destination_for_roll()`.
- Two pieces: require equal relative positions, outside yard/finish, and an even roll. Otherwise return `None`.
- For a valid pair, add `dice_roll // 2` to its position. Return `None` for overshoot, otherwise the destination. Pairs can enter/move through the home path and finish together.

### 2. `can_land(state: GameState, move: Move, destination: int) -> bool`

- Validate the move's player/pieces and an integer destination in `TRACK_START`–`FINISHED`.
- Finish: return `True`; all four pieces may finish.
- Count the owner's other pieces at the relative destination, excluding selected pieces. If that count plus the number moving exceeds two, return `False`. Apply this to track and private home-path squares.
- Private home path: after that capacity check, return `True`.
- Shared track: convert to an absolute square. Safe square: return `True` after the own-capacity check, regardless of other colors.
- Unsafe square: no opponent means `True`; a single may land on one opposing single; a pair may land on an opposing pair. Single-versus-pair and pair-versus-single landings return `False`. Nothing is captured yet.

### 3. `legal_moves(state: GameState, dice_roll: int) -> list[Move]`

- Validate the roll before looping. Use `state.current_player()`.
- Make candidates for each single piece and each distinct pair sharing a non-yard, non-finished relative position. Generate each pair once (for example, piece ID 0 with 1, not also 1 with 0).
- Get each candidate's destination. Skip `None`.
- For singles, reject `single_path_blocked(...)`. Pairs may pass opposing pairs, so do not apply the single-piece restriction to them.
- Keep candidates passing `can_land()`. Return the list; `[]` means no legal move. Do not change state or add a voluntary pass action.

**Check:** Yard release; odd/even pair rolls; splitting; opposing unsafe blockade; safe-square coexistence; no third friendly piece; pair-versus-single landing rejection; pair capture eligibility; exact home finishing; and unchanged state. `python3 Check.py` shows the three legal choices for a pair at position 10 with roll 4.

**Completion:** Shared validators and ID lookup helpers support all three methods. Fixed pair IDs (`piece_id`), landing-check indentation, and returning `moves` rather than `move`. Twenty tests pass, covering foundation rules, validation, legal choices, and unchanged state. Run the full checks with `python3 -m unittest Check Tests.test_rules_validation Tests.test_legal_moves -q`. These methods list choices; applying moves and advancing turns come later.

## Task 18 — Apply a chosen move and detect a winner

**Status:** Complete. `has_won()` and `apply_move()` verified. Moved move validation before reading its fields; movement/capture logic needed no further fixes. All 25 regression tests pass, including captures, safe squares, splitting, finishing, game-over rejection, and unchanged state after rejected moves.

**Purpose:** Turn a legal choice into an actual board change, including captures, then check whether the player has finished.

**Agreed ending:** First winner ends the game. Before applying a move, reject it if `has_won(state, player.player_id)` is true for any player. Full-ranking play is deferred.

### 1. `has_won(state: GameState, player_id: int) -> bool` — `Game/rules.py`

- Find the player with `get_player()`.
- Return whether all four pieces have position `FINISHED`. Use `all(...)` over the player's pieces.

### 2. `apply_move(state: GameState, move: Move, dice_roll: int) -> None` — new `Game/engine.py`

- Import models/constants and the rule helpers you need; rules must not import engine.
- Resolve the move using `get_move_pieces()`. Reject a finished game and any choice absent from `legal_moves(state, dice_roll)` with `ValueError`, before changing anything. Compare player IDs and sets of piece IDs so `(0, 1)` and `(1, 0)` mean the same pair.
- Calculate its destination using `move_destination()`.
- Convert the destination with `to_absolute()`. If it is a shared, unsafe square, find opposing pieces there with `pieces_at()` and return them to `YARD`. Legality already ensures single-versus-single or pair-versus-pair captures. Safe squares and private home/finish never capture.
- Set every selected piece's position to the destination. This function changes the supplied state in place and returns nothing.

**Example:** Red at relative 2, green at relative 43 (shared square 4), roll 2: red moves to 4 and green returns to 0. A red pair at 2 needs roll 4 to capture a green pair at square 4.

**Connection:** Roll → `legal_moves()` → player chooses → `apply_move()` → `has_won()`. Keep the current player and stored dice unchanged for now; turn advancement and extra-roll rules are the next task.

**Checks after implementation:** Single/pair captures, safe-square coexistence, splitting leaves the other piece behind, exact finish/win, and rejected moves leave the entire state unchanged. Keep `Check.py` limited to a short current-task example.

**Run:** `python3 Check.py` shows one capture. Full checks: `python3 -m unittest Check Tests.test_rules_validation Tests.test_legal_moves Tests.test_engine -q`.
