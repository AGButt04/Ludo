"""Check result storage using temporary files, not real research results."""
import json
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from tempfile import TemporaryDirectory

from Game.models import GameResult
from Experiments.results_io import save_result, load_results, validate_results
from Experiments.batch import summarize_results


class ResultsIOChecks(unittest.TestCase):
    def test_impossible_totals_rejected_at_all_boundaries(self):
        base = GameResult(None, 0, 4, 0, 1, 1, 0, True, 0, 0)
        cases = [
            replace(base, winner_id=0, truncated=False, turns_played=0),
            replace(base, winner_id=0, truncated=False),
            replace(base, moves_played=4),
            replace(base, moves_played=1, invalid_choices=100),
            replace(base, moves_played=1, invalid_choices=3),
        ]
        for field in ('turns_played', 'moves_played', 'invalid_choices', 'forfeited_turns'):
            for value in (-1, True, 1.5, '2'):
                cases.append(replace(base, **{field: value}))
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'games.jsonl'
            for bad in cases:
                with self.subTest(record=bad):
                    path.write_text('unchanged\n')
                    with self.assertRaises((TypeError, ValueError)):
                        save_result(bad, str(path))
                    self.assertEqual(path.read_text(), 'unchanged\n')
                    path.write_text(json.dumps(asdict(bad)) + '\n')
                    with self.assertRaises((TypeError, ValueError)):
                        load_results(str(path))
                    with self.assertRaises((TypeError, ValueError)):
                        summarize_results([bad])

    def test_counter_boundaries_round_trip(self):
        # These are summary bounds, not proof that a particular game occurred.
        records = [
            GameResult(None, 0, 4, 0, 1, 1, 3, True, 6, 0),
            GameResult(None, 1, 4, 0, 1, 1, 2, True, 7, 1),
            GameResult(None, 2, 4, 0, 1, 1, 0, True, 0, 0),
        ]
        with TemporaryDirectory() as folder:
            path = str(Path(folder) / 'games.jsonl')
            for result in records:
                save_result(result, path)
            self.assertEqual(load_results(path), records)
            self.assertEqual(summarize_results(records)['cutoffs'], 3)

    def test_forfeitures_require_rejections(self):
        result = GameResult(None, 0, 4, 0, 2, 2, 0, True, 6, 2)
        validate_results(result)
        with self.assertRaises(ValueError):
            validate_results(replace(result, invalid_choices=5))

    def test_seed_validation(self):
        result = GameResult(None, -7, 4, 0, 1, 1, 0, True, 0, 0)
        validate_results(result)
        for value in (True, 1.5, '7'):
            with self.subTest(seed=value), self.assertRaises(TypeError):
                validate_results(replace(result, seed=value))

    def test_outcome_validation(self):
        cutoff = GameResult(None, 0, 4, 0, 10, 10, 0, True, 0, 0)
        validate_results(cutoff)
        win = replace(cutoff, winner_id=0, truncated=False, moves_played=20)
        validate_results(win)  # Winning on the last allowed turn is valid.
        for changes in ({'winner_id': 0}, {'turns_played': 9}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_results(replace(cutoff, **changes))
        for value in (None, True, '0', 1.5):
            with self.subTest(winner=value), self.assertRaises(TypeError):
                validate_results(replace(win, winner_id=value))
        for value in (-1, 4):
            with self.subTest(winner=value), self.assertRaises(ValueError):
                validate_results(replace(win, winner_id=value))
        with self.assertRaises(TypeError):
            validate_results(replace(cutoff, truncated=1))

    def test_turn_limits(self):
        result = GameResult(None, 0, 4, 0, 3, 3, 0, True, 9, 3)
        validate_results(result)  # Equality at both limits is allowed.
        for value in (True, 1.5, '3'):
            with self.subTest(max_turns=value), self.assertRaises(TypeError):
                validate_results(replace(result, max_turns=value))
        for changes in ({'max_turns': 0}, {'max_turns': -1},
                        {'turns_played': 4}, {'forfeited_turns': 4}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_results(replace(result, **changes))

    def test_append_and_round_trip(self):
        """Preserve both records, including winner 0, None, and boolean values."""
        win = GameResult(0, 7, 4, 2, 10000, 180, 210, False,
                         invalid_choices=4, forfeited_turns=1)
        cutoff = GameResult(None, 8, 4, 0, 1, 1, 0, True,
                            invalid_choices=0, forfeited_turns=0)
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'nested' / 'games.jsonl'
            save_result(win, str(path))
            save_result(cutoff, str(path))
            self.assertEqual(load_results(str(path)), [win, cutoff])
            self.assertEqual(len(path.read_text(encoding='utf-8').splitlines()), 2)
            with path.open('a', encoding='utf-8') as file:
                file.write('\n  \n')
            self.assertEqual(load_results(str(path)), [win, cutoff])

    def test_empty_file(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'empty.jsonl'
            path.write_text('', encoding='utf-8')
            self.assertEqual(load_results(str(path)), [])

    def test_errors_are_not_hidden(self):
        """Missing files, invalid JSON, and missing fields must surface as errors."""
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'games.jsonl'
            with self.assertRaises(FileNotFoundError):
                load_results(str(path))
            path.write_text('not JSON\n', encoding='utf-8')
            with self.assertRaises(json.JSONDecodeError):
                load_results(str(path))
            path.write_text('{}\n', encoding='utf-8')
            with self.assertRaises(TypeError):
                load_results(str(path))
