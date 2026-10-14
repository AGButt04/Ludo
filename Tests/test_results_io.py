"""Check result storage using temporary files, not real research results."""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from Game.models import GameResult
from Experiments.results_io import save_result, load_results


class ResultsIOChecks(unittest.TestCase):
    def test_append_and_round_trip(self):
        """Preserve both records, including winner 0, None, and boolean values."""
        win = GameResult(0, 7, 4, 2, 10000, 180, 210, False)
        cutoff = GameResult(None, 8, 4, 0, 1, 1, 0, True)
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
