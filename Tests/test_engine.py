"""Applying choices must update pieces safely without advancing the turn."""
import unittest
from copy import deepcopy

from Game.models import Move, initial_state
from Game.engine import apply_move
from Game.rules import has_won


class EngineChecks(unittest.TestCase):
    def setUp(self):
        self.state = initial_state(4)
        self.red = self.state.players[0].pieces
        self.green = self.state.players[1].pieces

    def test_release_and_split(self):
        """Release moves one piece; splitting leaves its partner behind."""
        self.state.dice_roll = 6
        self.assertIsNone(apply_move(self.state, Move(0, (0,)), 6))
        self.assertEqual(self.red[0].position, 1)
        self.red[1].position = 1
        apply_move(self.state, Move(0, (0,)), 3)
        self.assertEqual([p.position for p in self.red], [4, 1, 0, 0])
        self.assertEqual(self.state.current_player_index, 0)
        self.assertEqual(self.state.dice_roll, 6)

    def test_single_and_pair_capture(self):
        """Capture uses shared squares; reversed pair IDs still work."""
        self.red[0].position = 2
        self.green[0].position = 43  # Absolute square 4.
        apply_move(self.state, Move(0, (0,)), 2)
        self.assertEqual(self.red[0].position, 4)
        self.assertEqual(self.green[0].position, 0)
        self.red[0].position = self.red[1].position = 2
        self.green[0].position = self.green[1].position = 43
        apply_move(self.state, Move(0, (1, 0)), 4)
        self.assertEqual([p.position for p in self.red], [4, 4, 0, 0])
        self.assertEqual([p.position for p in self.green], [0, 0, 0, 0])

    def test_safe_square_and_other_player(self):
        """An opposing pair survives on a safe square; green uses its own route."""
        self.red[0].position = self.red[1].position = 12
        self.green[0].position = self.green[1].position = 1
        apply_move(self.state, Move(0, (0, 1)), 4)
        self.assertEqual(self.red[0].position, 14)
        self.assertEqual(self.green[0].position, 1)
        self.state.current_player_index = 1
        self.red[2].position = 16
        apply_move(self.state, Move(1, (0,)), 2)
        self.assertEqual(self.green[0].position, 3)
        self.assertEqual(self.red[2].position, 0)

    def test_home_finish_and_game_over(self):
        """Private destinations work, and finishing the fourth piece ends play."""
        self.red[0].position = 51
        apply_move(self.state, Move(0, (0,)), 1)
        self.assertEqual(self.red[0].position, 52)
        self.red[0].position = self.red[1].position = 55
        self.red[2].position = self.red[3].position = 57
        self.assertFalse(has_won(self.state, 0))
        apply_move(self.state, Move(0, (0, 1)), 4)
        self.assertTrue(has_won(self.state, 0))
        self.state.current_player_index = 1
        before = deepcopy(self.state)
        with self.assertRaises(ValueError):
            apply_move(self.state, Move(1, (0,)), 6)
        self.assertEqual(self.state, before)

    def test_rejected_moves_leave_state_unchanged(self):
        """Wrong turns, blocked paths, mismatched captures and bad input cannot mutate."""
        self.red[0].position = self.red[1].position = 2
        self.green[0].position = 43
        for move, roll, error in [(Move(1, (0,)), 2, ValueError),
                                  (Move(0, (0, 1)), 4, ValueError),
                                  (Move(0, (0, 1)), 3, ValueError),
                                  (Move(0, (0,)), 7, ValueError),
                                  (None, 2, TypeError)]:
            before = deepcopy(self.state)
            with self.assertRaises(error):
                apply_move(self.state, move, roll)
            self.assertEqual(self.state, before)
        self.green[1].position = 43
        before = deepcopy(self.state)
        with self.assertRaises(ValueError):
            apply_move(self.state, Move(0, (0,)), 3)
        self.assertEqual(self.state, before)
