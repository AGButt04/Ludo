"""Check recorded transitions independently of legal_moves and destination helpers."""
import json
import unittest
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from Game.audit import save_trace
from run_game import run_game


class TraceChecks(unittest.TestCase):
    def check_game(self, trace, result):
        self.assertEqual(trace[0]['event'], 'start')
        previous = trace[0]['state']
        counts = {'move': 0, 'roll': 0, 'rejection': 0, 'forfeit': 0}
        safe = {1, 9, 14, 22, 27, 35, 40, 48}

        def square(owner, position):
            return (13 * owner + position - 1) % 52 + 1 if 1 <= position <= 51 else None

        for event in trace[1:-1]:
            with self.subTest(seed=result.seed, turn=event['turn'], event=event['event']):
                before, after = event['before'], event['after']
                self.assertEqual(before, previous)
                previous = after
                kind = event['event']
                if kind in counts:
                    counts[kind] += 1
                owner = before['current_player_id']
                old = {(p['player_id'], p['piece_id']): p['position'] for p in before['pieces']}
                new = {(p['player_id'], p['piece_id']): p['position'] for p in after['pieces']}
                self.assertEqual(old.keys(), new.keys())
                self.assertTrue(all(0 <= pos <= 57 for pos in new.values()))
                expected = old.copy()
                if kind == 'move':
                    move = event['move']
                    self.assertEqual(move['player_id'], owner)
                    selected = [(owner, piece) for piece in move['piece_ids']]
                    start = old[selected[0]]
                    roll = before['dice_roll']
                    if len(selected) == 2:
                        self.assertEqual(old[selected[1]], start)
                        self.assertEqual(roll % 2, 0)
                        self.assertNotIn(start, (0, 57))
                        destination = start + roll // 2
                    elif start == 0:
                        self.assertEqual(roll, 6)
                        destination = 1
                    else:
                        destination = start + roll
                    self.assertLessEqual(destination, 57)
                    landing = square(owner, destination)
                    for key, position in old.items():
                        if key in selected:
                            expected[key] = destination
                        elif key[0] != owner and landing is not None and landing not in safe and square(key[0], position) == landing:
                            expected[key] = 0
                self.assertEqual(new, expected)  # Also proves rolls/passes leave pieces unchanged.
                next_owner = (owner + 1) % result.num_players
                if kind == 'roll':
                    rolls = event['rolls']
                    self.assertTrue(1 <= len(rolls) <= 3)
                    self.assertTrue(all(1 <= value <= 6 for value in rolls))
                    self.assertTrue(all(value == 6 for value in rolls[:-1]))
                    self.assertEqual(event['cancelled'], rolls == [6, 6, 6])
                    if event['cancelled']:
                        expected_turn = (next_owner, None, [])
                    else:
                        self.assertNotEqual(rolls[-1], 6)
                        expected_turn = (owner, rolls[0], rolls[1:])
                elif kind == 'rejection':
                    self.assertEqual(before, after)
                    continue
                elif kind == 'forfeit':
                    expected_turn = (next_owner, None, [])
                elif all(new[(owner, piece)] == 57 for piece in range(4)):
                    expected_turn = (owner, None, [])
                elif before['remaining_rolls']:
                    remaining = before['remaining_rolls']
                    expected_turn = (owner, remaining[0], remaining[1:])
                else:
                    expected_turn = (next_owner, None, [])
                self.assertEqual((after['current_player_id'], after['dice_roll'], after['remaining_rolls']), expected_turn)
        self.assertEqual(trace[-1]['state'], previous)
        self.assertEqual(trace[-1]['result'], asdict(result))
        for event, field in [('move', 'moves_played'), ('roll', 'turns_played'),
                             ('rejection', 'invalid_choices'), ('forfeit', 'forfeited_turns')]:
            self.assertEqual(counts[event], getattr(result, field))

    def test_full_games_and_logging_equivalence(self):
        for count, seed, seat in [(2, 2, 1), (4, 0, 0), (4, 1, 3)]:
            trace = []
            result = run_game(count, seed, starting_player_index=seat, trace=trace)
            self.assertEqual(result, run_game(count, seed, starting_player_index=seat))
            self.check_game(trace, result)

    def test_cancelled_turn_and_cutoff(self):
        trace = []
        with patch('run_game.Dice.roll', side_effect=[6, 6, 6]):
            result = run_game(max_turns=1, trace=trace)
        self.assertEqual([e['event'] for e in trace], ['start', 'roll', 'end'])
        self.assertEqual(trace[-1]['reason'], 'turn_limit')
        self.check_game(trace, result)

    def test_forfeiture_is_recorded(self):
        trace = []
        agent = Mock()
        agent.choose_move.return_value = None
        with patch('run_game.RandomAgent', return_value=agent), patch('run_game.Dice.roll', side_effect=[6, 4]):
            result = run_game(max_turns=1, trace=trace)
        self.assertEqual([e['event'] for e in trace],
                         ['start', 'roll', 'rejection', 'rejection', 'rejection', 'forfeit', 'end'])
        self.check_game(trace, result)

    def test_trace_file_round_trip_and_no_overwrite(self):
        trace = []
        run_game(max_turns=1, trace=trace)
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'trace.jsonl'
            save_trace(trace, str(path))
            self.assertEqual([json.loads(line) for line in path.read_text().splitlines()], trace)
            with self.assertRaises(FileExistsError):
                save_trace(trace, str(path))
