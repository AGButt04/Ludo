"""Small checks for Tasks 1–5. Run with: python3 Check.py"""

import unittest

from Game import constants as board
from Game.models import Color, GameState, Piece, Player, initial_state


class FoundationChecks(unittest.TestCase):
    def test_board_constants(self):
        """The chosen route has 51 shared positions and five private positions."""
        self.assertEqual((board.YARD, board.TRACK_START, board.TRACK_END), (0, 1, 51))
        self.assertEqual((board.HOME_START, board.HOME_END, board.FINISHED), (52, 56, 57))
        self.assertEqual((board.TRACK_LENGTH, board.PIECES_PER_PLAYER), (52, 4))

    def test_piece(self):
        """Pieces keep their own IDs/positions and have readable output."""
        first, second = Piece(0, 2), Piece(1, 3, position=10)
        self.assertEqual((first.player_id, first.piece_id, first.position), (0, 2, board.YARD))
        self.assertEqual(second.position, 10)
        second.position = 14
        self.assertEqual(first.position, board.YARD)
        self.assertEqual(str(first), "Player 0, Piece 2, Position 0")

    def test_players(self):
        """IDs assign colors; each player owns four separate pieces."""
        players = [Player(i) for i in range(4)]
        self.assertEqual([p.color for p in players], [Color.RED, Color.GREEN, Color.YELLOW, Color.BLUE])
        for player in players:
            self.assertEqual([p.piece_id for p in player.pieces], [0, 1, 2, 3])
            self.assertTrue(all(p.player_id == player.player_id for p in player.pieces))
        players[0].pieces[0].position = 10
        others = players[0].pieces[1:] + [p for player in players[1:] for p in player.pieces]
        self.assertTrue(all(p.position == board.YARD for p in others))
        self.assertIn("RED", str(players[0]))
        self.assertIn(str(players[0].pieces[0]), str(players[0]))

    def test_game_state(self):
        """Turns use list indexes; storing a roll does not move pieces."""
        state = GameState([Player(3), Player(0)])
        self.assertEqual(state.current_player_index, 0)
        self.assertIsNone(state.dice_roll)
        self.assertIs(state.current_player(), state.players[0])
        state.current_player_index = 1
        state.dice_roll = 6
        self.assertEqual(state.current_player_index, 1)
        self.assertIs(state.current_player(), state.players[1])
        self.assertEqual(state.dice_roll, 6)
        self.assertTrue(all(p.position == board.YARD for player in state.players for p in player.pieces))
        self.assertIn("Current Player: 0", str(state))
        self.assertIn("Dice Roll: 6", str(state))

    def test_fresh_matches(self):
        """Two/four-player matches start fresh and never share pieces."""
        for count in (2, 4):
            first, second = initial_state(count), initial_state(count)
            self.assertEqual([p.player_id for p in first.players], list(range(count)))
            self.assertEqual(first.current_player_index, 0)
            self.assertIsNone(first.dice_roll)
            self.assertTrue(all(p.position == board.YARD for player in first.players for p in player.pieces))
            for player in first.players:
                for piece in player.pieces:
                    piece.position = 10
            self.assertTrue(all(p.position == board.YARD for player in second.players for p in player.pieces))

    def test_invalid_inputs(self):
        """Wrong types and unsupported IDs/counts must be rejected."""
        for factory in (Player, initial_state):
            for value in (True, 2.0, "2", None):
                with self.subTest(factory=factory.__name__, value=value):
                    with self.assertRaises(TypeError):
                        factory(value)
        for value in (-1, 4):
            with self.assertRaises(ValueError):
                Player(value)
        for value in (0, 1, 3, 5):
            with self.assertRaises(ValueError):
                initial_state(value)


if __name__ == "__main__":
    unittest.main(verbosity=2)
