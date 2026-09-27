# Ludo RL Code Walkthrough

Updated: September 27, 2026. Tasks 1–7 are implemented and checked; the complete game engine is still to come. The source files are authoritative. Work one small section at a time.

## 1. Board constants — `Game/constants.py`

| Relative position | Meaning |
|---|---|
| `0` (`YARD`) | Not released |
| `1–51` | Progress on the shared track |
| `52–56` | Private home path |
| `57` (`FINISHED`) | Finished |

The physical shared track contains 52 squares; a piece's route visits 51. Its route skips the square immediately before its start, consistent with Section II.B of the 2011 paper. Absolute starting squares and color orientation still need confirmation before coordinate mapping.

## 2. Pieces, colors, and players — `Game/models.py`

`Piece` stores `player_id`, `piece_id`, and `position`, defaulting to `YARD`. `@dataclass` generates initialization. `__str__` supplies readable output.

`Color` is an `IntEnum`: red=0, green=1, yellow=2, blue=3. The current implementation automatically assigns `Color(player_id)`. IDs and colors are therefore coupled by design at present.

`Player` creates four separate pieces in `__post_init__`. `field(init=False)` means callers do not supply its pieces or color.

```python
from Game.models import Piece, Player

piece = Piece(player_id=0, piece_id=2)
player = Player(1)  # GREEN; owns four pieces numbered 0–3.
print(piece)
print(player)
```

Player IDs must be integers 0–3. Piece fields and later assignments are not yet validated. Printing a list uses element representations; Player uses `str(piece)` and newline joining to display each piece's custom string.

## 3. Game state and fresh matches — `Game/models.py`

`GameState` stores players, `current_player_index=0`, and `dice_roll=None`. `current_player()` selects by list index, not player ID.

`initial_state(num_players)` is a standalone function: it creates a new state without requiring an existing one. Only integer counts 2 and 4 are accepted.

```python
from Game.models import initial_state

state = initial_state(4)
assert state.current_player() is state.players[0]
assert state.dice_roll is None
```

Two-player creation currently selects IDs 0 and 1: red and green. Final seating/starting-player policies remain open. Each factory call creates fresh objects. A state itself is mutable, not an independent saved-game copy; full validation, winner detection, and any rule-history fields are still future work.

## 4. Seeded dice — `Game/dice.py`

`random.Random(seed)` creates a private generator once in `Dice.__init__`. `roll()` asks it for an integer from 1 through 6.

```python
from Game.dice import Dice

first, second = Dice(42), Dice(42)
assert [first.roll() for _ in range(5)] == [second.roll() for _ in range(5)]
```

The same seed and calls reproduce the same sequence. Do not recreate the generator before each roll. Dice does not change game state; the future engine will control when rolls are permitted and store pending rolls.

## 5. Candidate destinations — `Game/rules.py`

`destination_for_roll(position, dice_roll)` rejects invalid types/ranges, then returns a destination or `None`:

- Yard: six releases to position 1; other rolls cannot move.
- Finished: cannot move again.
- Otherwise: add the roll; overshooting 57 cannot move.

```python
from Game.rules import destination_for_roll

assert destination_for_roll(0, 6) == 1
assert destination_for_roll(51, 1) == 52
assert destination_for_roll(55, 2) == 57
assert destination_for_roll(56, 2) is None
```

This uses six-to-release, exact finish, and no bounce. It does not modify a piece or check captures/blockades. A candidate destination is not yet a fully legal move.

## Checks and next discussion

From this folder, run `python3 Check.py`. Nine unittest methods cover current constants, models, factory, dice, and destination behavior. Passing these checks does not validate the unimplemented game rules.

Next discussed steps: relative-to-absolute mapping, square occupancy/safety, then legal-move generation. These are not yet assigned tasks or implemented code.

The eventual engine will apply moves, handle turns/winning, and emit events. Agents choose actions; the RL interface encodes observations and calculates rewards separately from rules.

Track assignments in [Infrastructure_Progress.md](Infrastructure_Progress.md) and research decisions in [Research_Progress.md](Research_Progress.md).
