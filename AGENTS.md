# Working on the Ludo research engine

## Purpose
This is a solo senior CS research project. Build a trustworthy, reproducible Ludo simulator, then random/heuristic agents, then an RL interface and PPO experiments. The student needs to understand the implementation.

The provisional research question concerns how training opponents (fixed heuristics versus self-play) and rewards (sparse versus shaped) affect learning speed, unfamiliar-opponent performance, and behavior in four-player Ludo. Two-player games may be a pilot. Novelty and paper/benchmark compatibility require verification; do not present them as established.

## Working style
- Explain the purpose, syntax, and one concrete Ludo example before new implementation. Keep explanations brief and beginner-friendly.
- The student normally writes the code. Review their work, fix errors in the requested portion, run relevant checks, and explain corrections. Do not implement future tasks unless asked.
- Group new tasks into 2–3 connected methods. When asked for the next task, explain it and add concise steps to `Infrastructure_Progress.md`.
- Mark tasks complete only after checking the code and tests. After roughly 8–10 additional completed tasks, condense their descriptions into short progress rows.
- Preserve the student's edits. Resolve routine coding details independently; ask about unresolved game rules before implementing behavior that depends on them.

## Continuing from a fresh chat
- Read `Infrastructure_Progress.md` for the current task and inspect the relevant code before claiming what is implemented. Files may have changed since the last progress entry.
- Consult `Rules.md` for this project's Ludo variant and unresolved decisions; do not substitute generic Ludo rules.
- Consult `Research_Progress.md` for research discussions and `Code_Walkthrough.md` for teaching explanations when relevant. Verify paper-specific claims against the papers.
- Keep current status in the progress file rather than duplicating it here. Update affected documentation briefly when behavior changes.

## Design boundaries
- Relative position is a piece's progress; absolute position is a shared-track square. Player IDs are not list indexes.
- Keep game rules separate from rewards and agent decisions. Legal-move generation must not mutate state; applying a move is a separate operation.
- Keep randomness seedable. Test agreed rules, including safe squares, pair movement, captures, and exact finishing.
- Build and verify complete random-agent games before connecting PPO. Do not generate the entire planned project at once.

## Checks
Run commands from this directory:
- `python3 Check.py` — only a short, readable demonstration of the current task. Do not make this run the full suite or print lengthy output.
- `python3 -m unittest Check Tests.test_rules_validation Tests.test_legal_moves -q` — existing regression checks. Include additional test modules as they are added.

Keep regression tests separate from the short demonstration. Test relevant edge cases and confirm failed actions leave state unchanged. Report results concisely; distinguish tested components from the unfinished engine.
