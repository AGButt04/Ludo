"""Random-agent games should be repeatable, legal, bounded, and quiet."""
import unittest
from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from unittest.mock import patch

from Agents.random_agent import RandomAgent
from Game.models import initial_state
from Game.rules import legal_moves, has_won, to_absolute, is_safe_square
import run_game as runner


class RunnerChecks(unittest.TestCase):
    def test_agent_choices(self):
        state = initial_state(4)
        choices = legal_moves(state, 6)
        before = deepcopy(state)
        first, second = RandomAgent(5), RandomAgent(5)
        selected = [first.choose_move(state, choices) for _ in range(20)]
        self.assertEqual(selected, [second.choose_move(state, choices) for _ in range(20)])
        self.assertTrue(all(move in choices for move in selected))
        self.assertIsNone(first.choose_move(state, []))
        self.assertEqual(state, before)

    def test_full_games(self):
        """Check every resolved roll, including occupied squares and final winners."""
        for count, start, seed in ((4, 0, 0), (4, 3, 1), (2, 0, 2), (2, 1, 3)):
            traces = []
            for repeat in range(2):
                state = initial_state(count)
                trace = []
                real_play = runner.play_turn

                def checked_play(current, move):
                    trace.append((current.current_player_index, current.dice_roll,
                                  tuple(current.remaining_rolls),
                                  None if move is None else move.piece_ids))
                    real_play(current, move)
                    occupied = {}
                    for player in current.players:
                        positions = [p.position for p in player.pieces]
                        self.assertTrue(all(0 <= pos <= 57 for pos in positions))
                        self.assertTrue(all(n <= 2 for pos, n in Counter(positions).items()
                                            if pos not in (0, 57)))
                        for piece in player.pieces:
                            square = to_absolute(player.color, piece.position)
                            if square is not None and not is_safe_square(square):
                                occupied.setdefault(square, set()).add(player.player_id)
                    self.assertTrue(all(len(owners) == 1 for owners in occupied.values()))

                output = StringIO()
                with patch.object(runner, 'initial_state', return_value=state), \
                     patch.object(runner, 'play_turn', side_effect=checked_play), \
                     redirect_stdout(output):
                    winner = runner.run_game(count, seed, starting_player_index=start)
                self.assertIsNotNone(winner)
                self.assertTrue(has_won(state, winner))
                self.assertEqual(sum(has_won(state, p.player_id) for p in state.players), 1)
                self.assertEqual(trace[0][0], start)
                self.assertEqual(output.getvalue(), '')
                traces.append(trace)
            self.assertEqual(traces[0], traces[1])

    def test_cutoff(self):
        self.assertIsNone(runner.run_game(max_turns=1))

    def test_input_validation(self):
        for value in (True, 1.5, '2'):
            with self.assertRaises(TypeError):
                runner.run_game(max_turns=value)
            with self.assertRaises(TypeError):
                runner.run_game(starting_player_index=value)
        for value in (0, -1):
            with self.assertRaises(ValueError):
                runner.run_game(max_turns=value)
        for value in (-1, 4):
            with self.assertRaises(ValueError):
                runner.run_game(starting_player_index=value)
