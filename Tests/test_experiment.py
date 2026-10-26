"""Resuming must preserve saved games and reproduce uninterrupted runs."""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from Experiments.batch import run_experiment
from Experiments.results_io import save_result


class ExperimentChecks(unittest.TestCase):
    def test_stop_resume_and_repeat(self):
        with TemporaryDirectory() as root:
            folder = str(Path(root) / 'resumed')
            first = run_experiment(5, folder, max_new_games=2)
            self.assertEqual(len(first), 2)
            path = Path(folder) / 'games.jsonl'
            original = path.read_bytes()
            resumed = run_experiment(5, folder)
            self.assertEqual([r.seed for r in resumed], list(range(5)))
            self.assertEqual([r.starting_player_index for r in resumed], [0, 1, 2, 3, 0])
            self.assertTrue(path.read_bytes().startswith(original))
            self.assertEqual(len(path.read_text().splitlines()), 5)
            before = path.read_bytes()
            with patch('Experiments.batch.run_game') as play:
                self.assertEqual(run_experiment(5, folder), resumed)
                play.assert_not_called()
            self.assertEqual(path.read_bytes(), before)
            full = run_experiment(5, str(Path(root) / 'full'))
            self.assertEqual(resumed, full)

    def test_fill_gap_sort_and_extend(self):
        """Missing IDs are filled even if saved records are out of order."""
        with TemporaryDirectory() as root:
            source = run_experiment(3, str(Path(root) / 'source'), max_turns=1)
            folder = str(Path(root) / 'gaps')
            from Experiments.run_config import prepare_run
            path = prepare_run(folder, 0, 4, 1)
            save_result(source[2], str(path))
            save_result(source[0], str(path))
            self.assertEqual(run_experiment(3, folder, max_turns=1), source)
            extended = run_experiment(4, folder, max_turns=1)
            self.assertEqual(extended[:3], source)
            self.assertEqual(len(extended), 4)

    def test_invalid_saved_data_does_not_append(self):
        """Reject mismatches, duplicates, bad outcomes and incomplete JSON."""
        with TemporaryDirectory() as root:
            folder = str(Path(root) / 'run')
            run_experiment(1, folder, max_turns=1)
            path = Path(folder) / 'games.jsonl'
            original = path.read_text()
            record = json.loads(original)
            invalid = [original + original, original + '{']
            for field, value in [('seed', 99), ('num_players', 2),
                                 ('starting_player_index', 1), ('max_turns', 2),
                                 ('winner_id', 0), ('truncated', False)]:
                changed = dict(record)
                changed[field] = value
                invalid.append(json.dumps(changed) + '\n')
            for text in invalid:
                path.write_text(text)
                with patch('Experiments.batch.run_game') as play:
                    with self.assertRaises((TypeError, ValueError)):
                        run_experiment(2, folder, max_turns=1)
                    play.assert_not_called()
                self.assertEqual(path.read_text(), text)
            path.write_text(original)
            with self.assertRaises(ValueError):
                run_experiment(2, folder, max_turns=2)
            self.assertEqual(path.read_text(), original)

    def test_invalid_limits_create_nothing(self):
        with TemporaryDirectory() as root:
            folder = Path(root) / 'run'
            for value in (True, 1.5, 0, -1):
                with self.assertRaises((TypeError, ValueError)):
                    run_experiment(value, str(folder))
                with self.assertRaises((TypeError, ValueError)):
                    run_experiment(5, str(folder), max_new_games=value)
                self.assertFalse(folder.exists())
