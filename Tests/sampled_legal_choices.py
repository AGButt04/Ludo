"""Reproduce the bounded legal-choice audit; not an exhaustive proof.

Run from the repository root: python3 -m Tests.sampled_legal_choices
Optionally save a new report with --output PATH (never overwrites).
"""
import argparse
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess

from Experiments.results_io import validate_results
from Tests.test_trace import TraceChecks
from run_game import run_game


def expected_choices(state):
    """Calculate choices without importing production rules or constants."""
    safe = {1, 9, 14, 22, 27, 35, 40, 48}

    def square(owner, position):
        return (13 * owner + position - 1) % 52 + 1 if 1 <= position <= 51 else None

    owner, roll = state['current_player_id'], state['dice_roll']
    pieces = state['pieces']
    own = {p['piece_id']: p['position'] for p in pieces if p['player_id'] == owner}
    answer = set()
    
    for size in (1, 2):
        for ids in combinations(sorted(own), size):
            position = own[ids[0]]
            if size == 2:
                if own[ids[1]] != position or position in (0, 57) or roll % 2:
                    continue
                destination = position + roll // 2
            else:
                if position == 57 or (position == 0 and roll != 6):
                    continue
                destination = 1 if position == 0 else position + roll
            
            if destination > 57:
                continue
            
            # Neither a single nor a pair may create a friendly stack above two.
            if destination != 57 and size + sum(
                pos == destination for piece, pos in own.items() if piece not in ids
            ) > 2:
                continue
            
            if size == 1:
                blocked = False
                
                for step in range(position + 1, min(destination, 51) + 1):
                    landing = square(owner, step)
                    
                    if landing in safe:
                        continue
                    
                    occupants = Counter(
                        p['player_id'] for p in pieces
                        if p['player_id'] != owner
                        and square(p['player_id'], p['position']) == landing
                    )
                    
                    if any(count >= 2 for count in occupants.values()):
                        blocked = True
                        break
                
                if blocked:
                    continue
            
            landing = square(owner, destination)
            
            if landing is not None and landing not in safe:
                enemies = sum(
                    p['player_id'] != owner
                    and square(p['player_id'], p['position']) == landing
                    for p in pieces
                )
                
                if enemies and enemies != size:
                    continue
            
            answer.add(ids)
    
    return answer


def require(condition, context):
    if not condition:
        raise AssertionError(context)


def audit():
    checker = TraceChecks()
    counts, games, examples = Counter(), [], []
    comparisons = 0
    for players in (2, 4):
        for seed in range(32):
            trace = []
            result = run_game(players, seed, max_turns=10000,
                              starting_player_index=seed % players, trace=trace)
            require(not result.truncated, (players, seed, 'turn limit reached'))
            validate_results(result)
            checker.check_game(trace, result)
            for event in trace:
                counts[event['event']] += 1
                if event['event'] not in ('move', 'pass'):
                    continue
                expected = expected_choices(event['before'])
                actual = {tuple(move['piece_ids']) for move in event['legal_choices']}
                context = {'players': players, 'seed': seed, 'event': event,
                           'expected': sorted(expected), 'actual': sorted(actual)}
                require(actual == expected, context)
                require(all(move['player_id'] == event['before']['current_player_id']
                            for move in event['legal_choices']), context)
                require(len(actual) == len(event['legal_choices']), context)
                if event['event'] == 'move':
                    require(tuple(event['move']['piece_ids']) in expected, context)
                else:
                    require(not expected, context)
                comparisons += 1
                # Preserve one pass, one single-only menu, and one menu with a pair.
                kind = 'pass' if not expected else ('pair' if any(len(x) == 2 for x in expected) else 'single')
                if not any(example['kind'] == kind for example in examples):
                    examples.append({'kind': kind, **context})
            if seed < 4:
                require(result == run_game(players, seed, max_turns=10000,
                                           starting_player_index=seed % players),
                        (players, seed, 'tracing changed result'))
            games.append({'result': asdict(result), 'trace_sha256': hashlib.sha256(
                json.dumps(trace, sort_keys=True).encode()).hexdigest()})

    root = Path(__file__).resolve().parents[1]
    paths = [*root.glob('Game/*.py'), *root.glob('Agents/*.py'),
             *root.glob('Experiments/*.py'), root / 'run_game.py', root / 'Rules.md',
             Path(__file__).resolve(), root / 'Tests/test_trace.py']
    return {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'python': platform.python_version(),
        'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
        'source_sha256': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(paths)},
        'settings': {'player_counts': [2, 4], 'seeds': list(range(32)),
                     'starting_player_index': 'seed % num_players', 'max_turns': 10000,
                     'agents': 'random', 'trace_on_off_seeds': [0, 1, 2, 3]},
        'status': 'passed', 'games_completed': len(games),
        'legal_choice_set_comparisons': comparisons, 'event_counts': dict(counts),
        'examples': examples, 'games': games,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit()
    if args.output:
        with args.output.open('x') as output:
            json.dump(report, output, indent=2)
            output.write('\n')
    print(f"PASS: {report['games_completed']} games; "
          f"{report['legal_choice_set_comparisons']} legal-choice sets; "
          "8 trace-on/off comparisons.")
