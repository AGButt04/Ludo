"""Personal-agent helpers: recognize wins and threats without changing the board."""
import unittest
from copy import deepcopy

from Agents.AGB import PersonalAgent
from Game.models import initial_state, Move
from Game.rules import legal_moves


class PersonalAgentChecks(unittest.TestCase):
    def test_protective_moves(self):
        cases = (
            # Both can reach safe squares; protect the more advanced piece.
            ("advanced first", [(0, 0, 17), (0, 1, 30), (1, 0, 1), (2, 0, 1)], 5, [(1,)]),
            # Red 30->32 remains in Yellow's reach; Red 20->22 is safe.
            ("skip unsavable", [(0, 0, 20), (0, 1, 30), (1, 0, 5), (2, 0, 1)], 2, [(0,)]),
            ("still threatened", [(0, 0, 16), (1, 0, 1)], 1, []),
            # Capture the attacker on unsafe square 16 using another red piece.
            ("indirect protection", [(0, 0, 18), (0, 1, 14), (1, 0, 3)], 2, [(1,)]),
            ("no threats", [], 6, []),
        )
        for label, placements, roll, expected in cases:
            with self.subTest(case=label):
                state = initial_state(4)
                state.dice_roll = roll
                for owner, piece, position in placements:
                    state.players[owner].pieces[piece].position = position
                moves = legal_moves(state, roll)
                before, original_moves = deepcopy(state), deepcopy(moves)
                actual = PersonalAgent().protective_moves(state, moves)
                self.assertEqual([move.piece_ids for move in actual], expected)
                self.assertEqual(state, before)
                self.assertEqual(moves, original_moves)

    def test_threatened_pieces_order_and_owner(self):
        state = initial_state(4)
        self.assertEqual(PersonalAgent().threatened_pieces(state), [])
        state.players[0].pieces[0].position = 16
        state.players[0].pieces[1].position = 30
        state.players[1].pieces[0].position = 1
        state.players[2].pieces[0].position = 1
        before = deepcopy(state)
        pieces = PersonalAgent().threatened_pieces(state)
        self.assertEqual([(p.player_id, p.piece_id) for p in pieces], [(0, 1), (0, 0)])
        self.assertEqual(state, before)
        state = initial_state(4)
        state.current_player_index = 1
        state.players[1].pieces[0].position = 3
        state.players[0].pieces[0].position = 14
        before = deepcopy(state)
        pieces = PersonalAgent().threatened_pieces(state)
        self.assertEqual([(p.player_id, p.piece_id) for p in pieces], [(1, 0)])
        self.assertEqual(state, before)

    def test_capture_threats(self):
        # Positions are relative to each owner; expected threats are hand-calculated.
        cases = (
            ("single capture", [(0, 0, 16), (1, 0, 1)], [(1, 2)]),
            ("later opponent", [(0, 0, 30), (2, 0, 1)], [(2, 3)]),
            ("split pair counted once", [(0, 0, 16), (1, 0, 1), (1, 1, 1)], [(1, 2)]),
            ("pair captures pair", [(0, 0, 16), (0, 1, 16), (1, 0, 1), (1, 1, 1)], [(1, 4)]),
            ("single cannot capture pair", [(0, 0, 16), (0, 1, 16), (1, 0, 1)], []),
            # Yellow's pair at absolute 15 blocks Green's route to Red at 16.
            ("blocked route", [(0, 0, 16), (1, 0, 1), (2, 0, 41), (2, 1, 41)], [(2, 1)]),
        )
        for label, placements, expected in cases:
            with self.subTest(case=label):
                state = initial_state(4)
                state.dice_roll, state.remaining_rolls = 6, [4]
                for owner, piece, position in placements:
                    state.players[owner].pieces[piece].position = position
                before = deepcopy(state)
                self.assertEqual(PersonalAgent().capture_threats(state, 0, 0), expected)
                self.assertEqual(state, before)

    def test_capture_threats_protected_positions_and_finished_game(self):
        for position in (0, 14, 52, 57):
            with self.subTest(position=position):
                state = initial_state(4)
                state.players[0].pieces[0].position = position
                state.players[1].pieces[0].position = 1
                before = deepcopy(state)
                self.assertEqual(PersonalAgent().capture_threats(state, 0, 0), [])
                self.assertEqual(state, before)
        state = initial_state(4)
        state.players[0].pieces[0].position = 16
        state.players[1].pieces[0].position = 1
        for piece in state.players[3].pieces:
            piece.position = 57
        before = deepcopy(state)
        self.assertEqual(PersonalAgent().capture_threats(state, 0, 0), [])
        self.assertEqual(state, before)

    def test_simulation_preserves_original_state(self):
        state = initial_state(4)
        state.dice_roll, state.remaining_rolls = 6, [4]
        before = deepcopy(state)
        simulated = PersonalAgent().simulate_move(state, Move(0, (0,)))
        self.assertEqual(state, before)
        self.assertIsNot(simulated, state)
        self.assertEqual(simulated.players[0].pieces[0].position, 1)
        self.assertEqual(simulated.dice_roll, 4)
        self.assertEqual(simulated.remaining_rolls, [])

    def test_winning_choices(self):
        for positions, roll, expected in (
            ([57, 57, 57, 56], 1, [(3,)]),
            ([57, 57, 55, 55], 4, [(2, 3)]),
            ([57, 57, 56, 56], 1, []),  # Each candidate finishes only one piece.
            ([57, 57, 57, 55], 1, []),
            ([0, 0, 0, 0], 3, []),
        ):
            with self.subTest(positions=positions, roll=roll):
                state = initial_state(4)
                state.current_player_index = 2  # Also check a player other than red.
                for piece, position in zip(state.players[2].pieces, positions):
                    piece.position = position
                state.dice_roll = roll
                moves = legal_moves(state, roll)
                before, original_moves = deepcopy(state), deepcopy(moves)
                winning = PersonalAgent().winning_moves(state, moves)
                self.assertEqual([move.piece_ids for move in winning], expected)
                self.assertEqual(state, before)
                self.assertEqual(moves, original_moves)
