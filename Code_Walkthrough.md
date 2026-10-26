# Ludo RL Code Walkthrough

Updated October 26, 2026. This describes implemented code; the full engine audit remains unfinished.

## 1. Positions and models

| Relative position | Meaning |
|---|---|
| 0 | Yard |
| 1–51 | Piece's progress on the shared track |
| 52–56 | Private home path |
| 57 | Finished |

`Game/constants.py` defines a 52-square shared board, with starts red=1, green=14, yellow=27, blue=40. A piece visits 51 shared squares before entering its home path. Paper compatibility must be checked separately.

In `Game/models.py`, `@dataclass` generates constructors. `Piece` stores owner ID, piece ID, and progress. `Player.__post_init__()` assigns `Color(player_id)` and creates four independent pieces. IDs and colors are currently coupled: 0=red, 1=green, 2=yellow, 3=blue.

`GameState` holds players, current-player index, current roll, and remaining rolls. The index selects a player from the list; it is not inherently a player ID. `initial_state(2 or 4)` creates fresh objects; two-player games currently use adjacent red/green seats.

`Move(player_id, piece_ids)` records one choice, e.g. `Move(0, (1, 2))` selects red's pieces 1 and 2. Its constructor checks IDs and selection size; the rules decide whether that pair can move now. Creating a Move does not move anything.

`GameResult` records outcome, seed/settings, turn/move counts, cutoff status, and rejected-choice/forfeiture totals. A turn is a collected roll sequence; a move is one applied single/pair action. A cutoff is not a declared draw.

## 2. Dice and legal moves

`Dice(seed)` owns a private random generator. Reusing it produces a reproducible sequence; do not recreate it before each roll. Dice returns numbers; the engine controls when to roll.

`Game/rules.py` separates questions:

- `destination_for_roll()` calculates single-piece progress: yard + six → 1; 56 + two → no destination.
- `to_absolute()` maps relative progress to a shared square; yard/home/finish return `None`.
- Occupancy, safety, and blockade helpers inspect the shared board without moving pieces.
- `move_destination()` handles the selected single or pair; an even roll moves a pair half the distance.
- `can_land()` checks destination occupancy; path checks enforce blockade restrictions.
- `legal_moves()` tries single/pair selections for the current player and returns all permitted choices. It does not choose one.
- `has_won()` checks whether all four pieces of a player have finished.

Shared validation helpers check types/ranges and resolve player/piece IDs. Model checks remain in `models.py`; mutable fields are not automatically validated on every assignment.

## 3. Engine: one roll versus a whole turn

In `Game/engine.py`:

- `roll_turn()` collects rolls until a non-six or the third six. Three sixes cancel the turn before movement. Otherwise it stores the first roll and the remaining sequence.
- `apply_move()` validates and applies one move and any capture. It does not consume the pending roll.
- `play_turn()` resolves one pending roll: apply a move or forced pass, then use the next stored roll or advance the player. A win discards unused rolls and ends play.
- `forfeit_turn()` discards unused rolls and advances once, preserving earlier moves.

Example: `[6, 6, 4]` is collected once, then resolved with three calls to `play_turn()`, recalculating choices after each action. Remaining rolls are visible before choosing.

## 4. Agents, recovery, and human play

`run_game.py` creates seeded random agents, runs turns until a winner or turn limit, and returns a `GameResult`.

`play_agent_roll()` gives the agent fresh deep copies of state and legal choices on every attempt. Hypothetical changes therefore stay out of the real board. The engine validates the returned choice against the real state. `InvalidMoveError` permits retries; after three rejected choices, the caller handles `AgentRetryLimitError` by forfeiting the remaining turn. Unexpected programming errors still propagate.

With no legal moves, the caller passes automatically without asking an agent. Rejections and forfeitures have separate counters; they are not valid moves.

`human_play.py` lets red choose numbered moves against three random agents. It prints a compact position table and move/capture/pass updates. Bad text or out-of-range choices prompt again; `q` or end-of-input quits without saving a completed trial. Its display is separate from the engine rules.

## 5. Results and experiments

`save_result()` validates a record and appends one JSON object per line (JSONL). `load_results()` reconstructs and validates each `GameResult`. `validate_results()` checks field types/ranges and relationships such as cutoffs having no winner and forfeitures requiring rejected choices.

`summarize_results()` validates before calculating totals. Its win rates use completed games only; mean turns/moves include cutoffs.

`prepare_run()` creates or checks `config.json` and returns the `games.jsonl` path. Current settings record schema version 2, random agents, rotating starts, and the three-attempt forfeiture policy. These labels document behavior; they do not dynamically configure the engine.

`run_batch()` requires a fresh results file. `run_experiment()` resumes a directory: game ID `i` uses seed `base_seed + i` and starting seat `i % num_players`. It checks experiment membership and duplicate IDs, skips saved games, and appends new ones. This supports one writer; parallel writes and automatic damaged-file repair are not implemented. Older incompatible records/settings are not silently migrated.

## 6. Checks and next work

From this directory:

```bash
python3 Check.py                          # Temporary-folder resume demo
python3 -m unittest Check -q              # Foundation checks
python3 -m unittest discover -s Tests -q  # Main suite
```

Passing tests supports the tested behavior, not a proof of all game rules. Full transition tracing/review and persistent human-interface tests remain pending. Then come heuristics and the RL interface; rewards will remain separate from game rules.

See [Rules.md](Rules.md) for the variant and [Infrastructure_Progress.md](Infrastructure_Progress.md) for task status.
