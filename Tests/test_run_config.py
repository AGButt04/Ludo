"""Run settings must be reusable without relabelling existing results."""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from Experiments.run_config import prepare_run


class RunConfigChecks(unittest.TestCase):
    def test_create_and_reuse(self):
        with TemporaryDirectory() as root:
            folder = Path(root) / 'nested' / 'run'
            path = prepare_run(str(folder), 0, 4, 10000)
            self.assertEqual(path, folder / 'games.jsonl')
            self.assertFalse(path.exists())
            config = folder / 'config.json'
            before = config.read_bytes()
            self.assertEqual(json.loads(before)['num_players'], 4)
            self.assertEqual(prepare_run(str(folder), 0, 4, 10000), path)
            self.assertEqual(config.read_bytes(), before)
            for settings in ((1, 4, 10000), (0, 2, 10000), (0, 4, 50)):
                with self.assertRaises(ValueError):
                    prepare_run(str(folder), *settings)
                self.assertEqual(config.read_bytes(), before)

    def test_unlabelled_results(self):
        with TemporaryDirectory() as root:
            results = Path(root) / 'games.jsonl'
            results.write_text('existing data\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                prepare_run(root, 0, 4, 10000)
            self.assertFalse((Path(root) / 'config.json').exists())
            self.assertEqual(results.read_text(), 'existing data\n')

    def test_invalid_inputs_create_nothing(self):
        with TemporaryDirectory() as root:
            folder = Path(root) / 'run'
            for settings, error in (((True, 4, 10), TypeError),
                                    (('0', 4, 10), TypeError),
                                    ((0, 3, 10), ValueError),
                                    ((0, 4, 0), ValueError),
                                    ((0, 4, True), TypeError)):
                with self.assertRaises(error):
                    prepare_run(str(folder), *settings)
                self.assertFalse(folder.exists())

    def test_bad_saved_config_is_preserved(self):
        with TemporaryDirectory() as root:
            prepare_run(root, 0, 4, 10)
            path = Path(root) / 'config.json'
            config = json.loads(path.read_text())
            config['schema_version'] = True
            path.write_text(json.dumps(config), encoding='utf-8')
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                prepare_run(root, 0, 4, 10)
            self.assertEqual(path.read_bytes(), before)
            path.write_text('invalid JSON', encoding='utf-8')
            with self.assertRaises(json.JSONDecodeError):
                prepare_run(root, 0, 4, 10)
            self.assertEqual(path.read_text(), 'invalid JSON')
