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
