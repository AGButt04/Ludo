"""Legal choices are checked separately from the short terminal demo."""
import unittest
from copy import deepcopy

from Game.models import initial_state
from Game.rules import legal_moves


class LegalMoveChecks(unittest.TestCase):
    def setUp(self):
        self.state = initial_state(4)
        self.red = self.state.players[0].pieces
        self.green = self.state.players[1].pieces

    def choices(self, roll):
        return {move.piece_ids for move in legal_moves(self.state, roll)}

    def test_yard_and_current_player(self):
        """Only six releases pieces, and only the current player gets choices."""
        self.assertEqual(self.choices(3), set())
        self.state.current_player_index = 2
        moves = legal_moves(self.state, 6)
        self.assertEqual(len(moves), 4)
        self.assertTrue(all(move.player_id == 2 for move in moves))

    def test_split_pair_and_no_mutation(self):
        """Even rolls offer a pair move as well as either split."""
        self.red[0].position = self.red[1].position = 10
        before = deepcopy(self.state)
        self.assertEqual(self.choices(4), {(0,), (1,), (0, 1)})
        self.assertEqual(self.choices(3), {(0,), (1,)})
        self.assertEqual(self.state, before)

    def test_unsafe_blockade(self):
        """Singles cannot cross an enemy pair; a pair can land on or pass it."""
        self.red[0].position = self.red[1].position = 2
        self.green[0].position = self.green[1].position = 43  # Absolute 4.
        self.assertEqual(self.choices(3), set())
        self.assertEqual(self.choices(4), {(0, 1)})
        self.assertIn((0, 1), self.choices(6))

    def test_safe_blockade(self):
        """Safe enemy pairs allow both passage and pair coexistence."""
        self.red[0].position = self.red[1].position = 12
        self.green[0].position = self.green[1].position = 1  # Absolute 14.
        self.assertEqual(self.choices(4), {(0,), (1,), (0, 1)})

    def test_capacity_and_capture_size(self):
        """No third friendly piece, and intact pairs cannot capture singles."""
        self.red[0].position = self.red[1].position = 2
        self.red[2].position = 4
        self.assertNotIn((0, 1), self.choices(4))
        self.red[3].position = 4
        self.assertNotIn((0,), self.choices(2))
        self.red[2].position = self.red[3].position = 0
        self.green[0].position = 43  # Absolute 4.
        self.assertNotIn((0, 1), self.choices(4))
        self.assertIn((0,), self.choices(2))

    def test_home_and_finish(self):
        """Home squares keep capacity limits; finish allows all four pieces."""
        self.red[0].position = self.red[1].position = 53
        self.red[2].position = 55
        self.assertNotIn((0, 1), self.choices(4))
        self.red[0].position = self.red[1].position = 55
        self.red[2].position = self.red[3].position = 57
        self.assertEqual(self.choices(4), {(0, 1)})
        self.assertEqual(self.choices(6), set())
