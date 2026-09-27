# Ludo RL Code Walkthrough

**Status:** Teaching examples only; no environment has been implemented. Read the sections in order: later snippets use earlier definitions. Examples use Python 3.10+.

**Workflow:** Explain → agree on assumptions → approve one file → implement and test → update these notes.

## Architecture and build order

`Piece / Player / GameState` → rules engine → random-agent games → RL interface → PPO experiments.

Test each approved part as we build it. The engine handles legal moves, captures, turns, winning, and event logs. Agents choose actions. The RL interface supplies observations, action masks, and rewards; rewards stay separate from rules.

## 1. Positions and board colors

A piece needs two coordinate systems: **relative progress** for movement and an **absolute square** for interactions with other players.

| Relative position | Meaning |
|---|---|
| `0` | Yard |
| `1–51` | Shared track, measured from the piece's own start |
| `52–56` | Private home path |
| `57` | Finished |

**Proposed route, not yet approved:** The shared board has 52 squares, but each color visits 51 before entering its home path. The 2011 paper, Section II.B, supports skipping the square immediately before that color's start. We still need to trace the board and confirm color order, direction, and home entry.

```python
from enum import IntEnum

YARD = 0
TRACK_START = 1
TRACK_END = 51
HOME_START = 52
HOME_END = 56
FINISHED = 57
TRACK_LENGTH = 52
PIECES_PER_PLAYER = 4


class Color(IntEnum):
    RED = 0
    GREEN = 1
    YELLOW = 2
    BLUE = 3


START_SQUARES = (1, 14, 27, 40)  # Indexed by Color.


def require_int_in_range(value: int, low: int, high: int) -> None:
    if type(value) is not int:
        raise TypeError("Expected an integer.")
    if not low <= value <= high:
        raise ValueError(f"Expected a value between {low} and {high}.")


def to_absolute(color: Color, position: int) -> int | None:
    if not isinstance(color, Color):
        raise TypeError("Expected a Color.")
    require_int_in_range(position, YARD, FINISHED)
    if not TRACK_START <= position <= TRACK_END:
        return None
    start = START_SQUARES[color]
    return ((start + position - 2) % TRACK_LENGTH) + 1
```

- `IntEnum` gives names to integer values; `Color.GREEN` indexes entry `1`.
- `%` wraps around the board: blue progress `14` maps to square `1`.
- `int | None` means an integer or no shared square. Yard, home path, and finish return `None`; invalid inputs raise errors.
- Type hints describe expected inputs but do not validate them. The helper rejects fractions and booleans (`True` is otherwise treated as an integer in Python).

**Example:** `to_absolute(Color.GREEN, 1)` and `to_absolute(Color.RED, 14)` both return `14`. This means the pieces share a square; capture legality depends on later rules.

## 2. Pieces and players

A **player ID** identifies a participant; a **color** determines its board route. Keeping them separate allows player `1` to use yellow in a two-player game.

```python
from dataclasses import dataclass, field


@dataclass
class Piece:
    player_id: int
    piece_id: int
    position: int = YARD

    def __post_init__(self) -> None:
        require_int_in_range(self.player_id, 0, 3)
        require_int_in_range(self.piece_id, 0, PIECES_PER_PLAYER - 1)
        require_int_in_range(self.position, YARD, FINISHED)


@dataclass
class Player:
    player_id: int
    color: Color
    pieces: list[Piece] = field(init=False)

    def __post_init__(self) -> None:
        require_int_in_range(self.player_id, 0, 3)
        if not isinstance(self.color, Color):
            raise TypeError("Expected a Color.")
        self.pieces = [
            Piece(self.player_id, piece_id)
            for piece_id in range(PIECES_PER_PLAYER)
        ]

    def positions(self) -> list[int]:
        return [piece.position for piece in self.pieces]

    def has_won(self) -> bool:
        return all(piece.position == FINISHED for piece in self.pieces)
```

- `@dataclass` generates initialization and a readable object representation.
- `field(init=False)` excludes `pieces` from constructor arguments. `__post_init__()` creates a fresh list for each player.
- The list comprehension creates piece IDs `0, 1, 2, 3`. `all(...)` requires every piece to be finished.

**Example:** `Player(1, Color.YELLOW).positions()` returns `[0, 0, 0, 0]`.

**Boundary:** Constructor checks do not protect later assignments. These are mutable models; the eventual engine must validate changes and preserve four pieces per player.

## 3. Initial state and seating

Store the current player's **list index** explicitly. Return a player ID when identifying a winner. The factory below creates only two- or four-player games and requires explicit colors; it does not silently decide two-player seating.

```python
@dataclass
class GameState:
    players: list[Player]
    current_player_index: int = 0
    dice_roll: int | None = None

    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def winner(self) -> int | None:
        for player in self.players:
            if player.has_won():
                return player.player_id
        return None


def create_initial_state(colors: tuple[Color, ...]) -> GameState:
    if len(colors) not in (2, 4):
        raise ValueError("Choose two or four colors.")
    if any(not isinstance(color, Color) for color in colors):
        raise TypeError("Each color must be a Color.")
    if len(set(colors)) != len(colors):
        raise ValueError("Each player needs a different color.")
    players = [Player(i, color) for i, color in enumerate(colors)]
    return GameState(players=players)
```

- `tuple[Color, ...]` means a tuple of colors. `enumerate` supplies an index and a color for each entry.
- The tuple order establishes seating/turn order for this proposal.
- `None` means no pending roll or no winner, depending on the field/method.

**Example:** `create_initial_state((Color.RED, Color.YELLOW))` creates participants `0` and `1` on the proposed opposite routes. This is an illustration, not an approved seating rule.

**Boundary:** This is minimal mutable state, not a complete saved-game snapshot. The factory starts at index `0` for teaching; the starting-player policy is undecided. Direct construction/loading needs validation later. History-dependent rules may require extra fields, and exact resumption also requires RNG state. Winner detection assumes play stops at the first winner.

## 4. Seeded dice

Keep the random-number demonstration separate from turn handling. A dice generator can roll repeatedly; the future game engine decides when a roll is allowed.

```python
import random


class Dice:
    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def roll(self) -> int:
        return self.rng.randint(1, 6)
```

**Example:** Two `Dice(seed=42)` instances produce the same sequence when called the same number of times. The seed makes the sequence reproducible, not constant.

The engine will store a pending roll in `state.dice_roll`, resolve a move or forced pass, and then apply the turn rules. It must prevent replacing an unresolved roll. Later, `reset(seed=...)` must seed the game's RNG; agent randomness also needs controlled seeds.

## 5. Basic destination calculation

**Proposed movement assumptions:** six to leave the yard, exact roll to finish, and no backward bounce. This function calculates a candidate destination without changing state; it does not check captures or blockades.

```python
def destination_for_roll(position: int, dice_roll: int) -> int | None:
    require_int_in_range(position, YARD, FINISHED)
    require_int_in_range(dice_roll, 1, 6)

    if position == YARD:
        return TRACK_START if dice_roll == 6 else None
    if position == FINISHED:
        return None

    destination = position + dice_roll
    return destination if destination <= FINISHED else None
```

`return X if condition else Y` selects between two results. Leaving the yard places a piece at `1`; it does not advance it six track squares.

**Examples:** `destination_for_roll(50, 4) == 54` enters the private path; `(55, 2)` finishes; `(56, 2)` cannot move because it overshoots.

## Checks to implement with approved files

These are readable examples of assertions, not a complete test suite:

```python
assert to_absolute(Color.GREEN, 1) == to_absolute(Color.RED, 14)
assert to_absolute(Color.BLUE, 14) == 1
assert to_absolute(Color.RED, HOME_START) is None

state = create_initial_state((Color.RED, Color.YELLOW))
assert state.players[1].color == Color.YELLOW
assert state.current_player().player_id == 0
assert state.winner() is None
assert state.players[0].pieces is not state.players[1].pieces

first, second = Dice(42), Dice(42)
rolls = [first.roll() for _ in range(100)]
assert rolls == [second.roll() for _ in range(100)]
assert all(1 <= roll <= 6 for roll in rolls)

assert destination_for_roll(0, 3) is None
assert destination_for_roll(0, 6) == 1
assert destination_for_roll(51, 1) == HOME_START
assert destination_for_roll(55, 2) == FINISHED
assert destination_for_roll(56, 2) is None
assert destination_for_roll(57, 1) is None
```

Also test rejected inputs, duplicate colors, invalid player counts, piece independence, and all-four-pieces winning. Add rule tests as each rule is approved.

## Next decision

Trace and approve one color's complete route before implementing `constants.py`. Then proceed through these models and movement examples. Legal-move generation follows, after deciding safe squares, blockades, and relevant turn rules.

Research context: [Research progress](RESEARCH_PROGRESS.md). External code may provide ideas, but it does not establish our rules or correctness.
