# Sampled legal-choice audit

This preserves the temporary review checker as `Tests/sampled_legal_choices.py`.
It does not change gameplay. The reference calculation is separately written,
but follows our **same chosen rules**, not a third-party certified Ludo engine.

## Rerun

From `Environment and Implementation`:

```sh
python3 -m Tests.sampled_legal_choices
python3 -m unittest discover -s Tests -q
```

To save another report, choose a new filename (existing reports are never overwritten):

```sh
python3 -m Tests.sampled_legal_choices --output Review_Evidence/rerun.json
```

## What it checks

1. Play 64 random-agent games: 2 and 4 players, each with seeds 0–31.
   Starting seat is `seed % num_players`; cutoff is 10,000 turns.
   The runner seeds dice with `seed` and each agent with `seed + 1 + player_id`.
2. At every move/pass, independently enumerate single-piece and pair choices
   from the recorded board and pending die roll. Do not call production rule helpers.
3. Compare the **whole choice set** with the engine's list. Missing choices and
   extra choices both fail. Also reject duplicate/wrong-owner choices, verify the
   selected move belongs to the set, and require an empty set for a pass.
4. Run existing independent transition checks and summary validation on each game.
   For seeds 0–3 at both player counts, verify tracing does not change the result.

Example: friendly pairs at relative positions 3 and 4 with roll 2, no opponents
on the route. Each single may split and move two squares. The pair at 4 may move
to 5, but the pair at 3 cannot move to 4 because that would stack four pieces.
The engine must offer exactly those five choices.

## Evidence and limits

`legal_choices_2026-11-01.json` records the rerun, settings, per-game results,
trace digests, source hashes, Python version and Git base revision. The source
hashes identify the working files, including the newly added checker (which need
not yet be committed). Three full comparison examples are saved under `examples`:
a pass, a single-only choice set, and a choice set containing a pair.

**18,130 comparisons means 18,130 decision-point choice sets**, including empty
sets—not that many unique boards, games, or individually inspected moves.
This is bounded automated evidence, not exhaustive correctness. Random play can
miss rare states; trajectories come from the engine itself; both implementations
could share a mistaken interpretation of the written rules. Focused rule tests
and manual inspection remain useful. It does not establish human-interface or
future RL correctness, benchmark compatibility, or strategy strength.

For a later rerun, compare counts and per-game trace digests; timestamps will
differ. Changed code or Python/random behavior can change trajectories. Preserve
the old report rather than changing the checker just to reproduce its counts.
