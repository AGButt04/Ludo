# Ludo Rules Reference

Agreed variant as of October 3, 2026. These are design decisions, not a claim that all rules are implemented.

- Keep red as shared square 1. Safe squares are `1, 9, 14, 22, 27, 35, 40, 48`. Rotating the numbering by a whole color interval preserves this set.
- Different players may share safe squares without capture.
- Two same-player pieces form a blockade. On unsafe squares, an opposing single piece cannot pass it. On safe squares, other players may pass the blockade, including with single pieces. Own pieces may pass their own blockade.
- A player may split a blockade by moving one piece the full rolled distance. Splitting never grants a free move; odd rolls can move a single piece but not an intact pair.
- Moving the pair requires an even roll: 2 → 1 square, 4 → 2, 6 → 3.
- On shared-track and private home-path squares, at most two pieces of the same player may occupy a square. A single cannot join a friendly pair, and a pair cannot land on a friendly single or pair. Yard and finish are exempt.
- Opposing blockades may share safe squares without capture; the limit is one pair per player there.
- A player must choose a legal move whenever one exists; passing is allowed only when none exists. Splitting is forced only when every available legal move requires it.
- Example: friendly pairs on squares 3 and 4, roll 2. Pair 3 → 4 is illegal; pair 4 → 5 may move intact if otherwise legal. A single piece may instead split from either pair and move two squares if otherwise legal.
- Opposing blockades may pass each other. Capturing an opposing pair requires a moving pair to land exactly on its square; both captured pieces return to the yard. Safe-square protection still applies.
- An intact pair cannot capture an opposing single piece: landing on that single on an unsafe square is illegal. Splitting the pair and moving one piece may capture the single normally.
- Pairs may form and move in the private home path and finish together, using half an even roll and exact finishing.
- The initial engine ends the game immediately when the first player finishes all four pieces. No further moves are allowed. Continuing for second/third/fourth-place rankings is deferred.
- Board numbering does not decide who starts. The engine must support any participating player starting; seeded random selection versus explicit selection is still to be specified.

**Remaining decisions:** Turn bonuses, consecutive-six handling, starting-player selection, and final two-player seating. Current yard release is one piece on a six, not paired release.

**Implementation boundary:** Mapping, occupancy, safety, counts, shared paths, blockade detection, single-path obstruction, single/pair destinations, landing checks, legal-move generation, applying moves/captures, and winner detection exist. The complete turn loop remains to be implemented. Two-player creation currently selects red and green. `has_blockade()` rejects same-owner shared-square stacks larger than two, consistent with the agreed occupancy limit.
