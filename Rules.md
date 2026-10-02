# Ludo Rules Reference

Agreed variant as of October 2, 2026. These are design decisions, not a claim that all rules are implemented.

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

**Implementation boundary:** Safe-square lookup and pair detection exist. Blockade movement, captures, and mandatory-move enforcement do not yet exist. `has_blockade()` temporarily rejects stacks larger than two until their rules are resolved. Two-player creation currently selects red and green; final seating policy remains open.
