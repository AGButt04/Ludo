"""Regression checks for shared validation; separate from the short Check.py demo."""
import unittest
from copy import deepcopy

from Game.models import Color, GameState, Move, Player, initial_state
from Game import rules


class RulesValidationChecks(unittest.TestCase):
    def test_numeric_validators(self):
        """Rolls, relative positions, and absolute squares have different limits."""
        for validate, low, high in [(rules.validate_roll, 1, 6),
                                    (rules.validate_position, 0, 57),
                                    (rules.validate_square, 1, 52)]:
            validate(low)
            validate(high)
            for value in (True, 1.5, '1', None):
                with self.assertRaises(TypeError):
                    validate(value)
            for value in (low - 1, high + 1):
                with self.assertRaises(ValueError):
                    validate(value)

    def test_lookup_by_id(self):
        """Reordered players and pieces must still resolve by their IDs."""
        state = GameState([Player(2), Player(0)])
        state.players[0].pieces.reverse()
        player, pieces = rules.get_move_pieces(state, Move(2, (0, 3)))
        self.assertIs(player, state.players[0])
        self.assertEqual({p.piece_id for p in pieces}, {0, 3})
        with self.assertRaises(ValueError):
            rules.get_move_pieces(state, Move(1, (0,)))
        with self.assertRaises(TypeError):
            rules.get_player(state, True)
        with self.assertRaises(TypeError):
            rules.get_move_pieces(state, None)
        player.pieces.pop()  # Removes piece ID 0 after reversing.
        with self.assertRaises(ValueError):
            rules.get_move_pieces(state, Move(2, (0,)))

    def test_shared_board_rules(self):
        """Mapping, safety, counts, and path obstruction retain their behavior."""
        state = initial_state(4)
        for piece in state.players[1].pieces[:2]:
            piece.position = 43  # Shared square 4.
        self.assertEqual(rules.to_absolute(Color.BLUE, 14), 1)
        self.assertEqual(rules.shared_path(Color.BLUE, 12, 15), [52, 1, 2])
        self.assertEqual(rules.count_pieces_at(state, 4, 1), 2)
        self.assertTrue(rules.has_blockade(state, 4, 1))
        self.assertTrue(rules.single_path_blocked(state, 0, 2, 5))
        for piece in state.players[1].pieces[:2]:
            piece.position = 1  # Shared safe square 14.
        self.assertTrue(rules.opponent_blockade_at(state, 14, 0))
        self.assertFalse(rules.single_path_blocked(state, 0, 12, 15))
        for square in range(1, 53):
            self.assertEqual(rules.is_safe_square(square), square in (1, 9, 14, 22, 27, 35, 40, 48))
        with self.assertRaises(TypeError):
            rules.to_absolute(0, 1)
        with self.assertRaises(ValueError):
            rules.shared_path(Color.RED, 3, 3)
        with self.assertRaises(ValueError):
            rules.opponent_blockade_at(state, 53, 0)

    def test_move_destinations(self):
        """Splits/pairs, release, finishing, and no-mutation behavior remain intact."""
        state = initial_state(4)
        single, pair = Move(0, (0,)), Move(0, (0, 1))
        self.assertEqual(rules.move_destination(state, single, 6), 1)
        self.assertIsNone(rules.move_destination(state, pair, 6))
        for piece in state.players[0].pieces[:2]:
            piece.position = 10
        before = deepcopy(state)
        self.assertEqual(rules.move_destination(state, single, 4), 14)
        self.assertEqual(rules.move_destination(state, pair, 4), 12)
        self.assertIsNone(rules.move_destination(state, pair, 3))
        self.assertEqual(state, before)
        for piece in state.players[0].pieces[:2]:
            piece.position = 55
        self.assertEqual(rules.move_destination(state, pair, 4), 57)
        self.assertIsNone(rules.move_destination(state, pair, 6))
        with self.assertRaises(TypeError):
            rules.move_destination(state, single, True)
        with self.assertRaises(ValueError):
            rules.move_destination(state, single, 7)

    def test_landing_validation(self):
        """Reject invalid destinations and absent players."""
        state = initial_state(2)
        with self.assertRaises(ValueError):
            rules.can_land(state, Move(0, (0,)), 0)
        with self.assertRaises(TypeError):
            rules.can_land(state, Move(0, (0,)), True)
        with self.assertRaises(ValueError):
            rules.can_land(state, Move(3, (0,)), 1)
