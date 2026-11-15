# Abdul's rule-based Ludo agent

Updated November 13, 2026. Proposed playing preferences, not implemented code.
Goal: imitate Abdul's defensive, progress-focused style in a winner-only game.
Strength must be tested; these are personal heuristics, not proven optimal rules.
Use Rules.md for game mechanics. Discuss implementation separately, step by step.

## Essential concepts

- **Progress:** Distance traveled on the shared path toward private-lane entry.
  Above 50% is well progressed; above 75% is very well progressed.
  Pieces inside the private lane cannot be captured.
- **Threat (initial model):** An opponent could legally capture the piece with
  one roll of 1–6. Check actual legality, not just distance. Extra-roll threats
  and predictions of opponent behavior are outside this initial model.
- **Real protection:** The move removes a threat. Changing the required capture
  roll from 3 to 5 does not improve single-roll odds: both have probability 1/6.
- **Pairs:** Singles cannot capture intact pairs; opposing pairs can. An intact
  pair cannot capture a single. Safe squares still protect pieces.
- **Known rolls:** Consider current and remaining rolls together, in order.
  Do not assume future rolls. No opponent acts between your stored rolls.

## The 10 rule groups

These numbers identify rules, not a complete priority ranking. Winning always
comes first; the other preferences depend on context and the exceptions below.

1. **Win immediately.** Finish the fourth piece whenever possible.

2. **Protect what can actually be saved.** Among pieces whose threats can be
   removed, favor the most progressed. Save a less-progressed piece if moving
   the advanced one would leave it threatened. Escaping single-roll reach with
   an advanced piece can beat reaching a safe square with a less-progressed one.

3. **Deploy versus protect.** Use early sixes to release pieces. When deployment
   conflicts with saving a threatened piece, favor deployment below 50% progress
   and protection above 50%. Redeploy captured pieces promptly when advanced
   pieces do not need saving. Urgent intervention against a near-winner may override.

4. **Capture for useful benefit.** Prefer capture over otherwise comparable safe
   advancement. Capturing a well-advanced opponent can beat private-lane entry
   for an unthreatened piece; capturing a newly released piece does not.
   Accept risk when necessary to stop a near-winner and preserve a chance of first
   place. Entering the private lane is not itself winning.

5. **Secure private-lane entry.** Prefer entry over ordinary safe advancement or
   grouping, unless protection or a valuable capture takes priority. Do not keep
   pieces outside merely to have somewhere to spend rolls.

6. **Leave shelter carefully.** Keep a piece on a safe square when leaving exposes
   it and another useful safe move exists. Leave when a roll or known sequence
   permits useful progress without immediate exposure. A large roll alone does
   not guarantee safety.

7. **Use blockades while useful.** Form pairs to protect pieces or hold opponents
   back. Preserve useful blockades while advancing other pieces, including those
   in the private lane. Move a threatened pair intact when that saves both.
   Split if necessary to avoid risking both pieces together, or if no alternative
   legal move exists. A pair can be rebuilt later.

8. **Ordinary advancement.** With equally safe options and no higher benefit,
   advance trailing shared-track pieces toward the leaders. If the only choices
   move threatened pieces without improving safety, advance the more-progressed
   piece toward home instead.

9. **Judge the full known turn.** Prefer a sequence that achieves several goals.
   Example: with 6 then 3, deploy with the six and protect an advanced piece with
   the three if both are legal. Protection need not happen on the first roll
   when it is secured before opponents act.

10. **Home-lane choices.** Between protected pieces, prefer finishing one over
    advancing another. If neither can finish and no agreed advantage distinguishes
    the moves, use a seeded random tie-break. Do not deliberately keep pieces
    unfinished merely to offer more finishing numbers.

## Still to settle together

Do not silently invent priorities or weights for these cases:

- Exact progress formula and treatment of exactly 50%.
- Valuable capture versus deployment when both are available.
- What qualifies as urgent intervention against a near-winner.
- Partial safety improvement: fewer threats, but not complete safety.
- How to measure a blockade's usefulness; when to split one no longer useful.
- Any remaining conflicts between rules. No general random-action percentage agreed.

## Optional later feature

**Opponent modeling:** Estimate tendencies from observed choices and their legal
alternatives, not hidden strategy labels. Use estimates cautiously; forced moves
do not establish a style. Deferred until the board-based agent works. Whether
memory persists between games is undecided.
