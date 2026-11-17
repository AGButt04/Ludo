"""Personal-agent helpers: recognize wins and threats without changing the board."""
import unittest
from copy import deepcopy

from Agents.AGB import PersonalAgent
from Game.models import initial_state, Move
from Game.rules import legal_moves


class PersonalAgentChecks(unittest.TestCase):
    def test_capture_progress_ranking(self):
        cases = (
            ("advanced single", [(0, 0, 12), (0, 1, 20), (1, 0, 3), (2, 0, 50)], 4, [(1,)]),
            ("unsafe advanced single", [(0, 0, 12), (0, 1, 20), (1, 0, 3), (2, 0, 50), (3, 0, 35)], 4, [(0,)]),
            ("equal captures retain both choices", [(0, 0, 12), (0, 1, 12), (1, 0, 3)], 4, [(0,), (1,)]),
            ("advanced pair once", [(0, 0, 14), (0, 1, 14), (0, 2, 30), (0, 3, 30), (1, 0, 3), (1, 1, 3), (2, 0, 6), (2, 1, 6)], 4, [(2, 3)]),
        )
        for label, placements, roll, expected in cases:
            with self.subTest(case=label):
                state = initial_state(4)
                state.dice_roll = roll
                for owner, piece, position in placements:
                    state.players[owner].pieces[piece].position = position
                moves = legal_moves(state, roll)
                before, original_moves = deepcopy(state), deepcopy(moves)
                actual = PersonalAgent().preferred_capture_moves(state, moves)
                self.assertEqual([move.piece_ids for move in actual], expected)
                self.assertEqual(state, before)
                self.assertEqual(moves, original_moves)

    def test_preferred_capture_moves(self):
        for exposed_pair in (False, True):
            with self.subTest(exposed_pair=exposed_pair):
                state = initial_state(4)
                state.dice_roll = 4
                for piece_id in (0, 1):
                    state.players[0].pieces[piece_id].position = 14
                    state.players[1].pieces[piece_id].position = 3
                    if exposed_pair:
                        # Blue pair at shared 14 can recapture Red's pair at 16.
                        state.players[3].pieces[piece_id].position = 27
                state.players[0].pieces[2].position = 20
                state.players[2].pieces[0].position = 50  # Shared square 24.
                pair, single = Move(0, (0, 1)), Move(0, (2,))
                moves = legal_moves(state, 4)
                self.assertIn(pair, moves)
                self.assertIn(single, moves)
                before, original_moves = deepcopy(state), deepcopy(moves)
                agent = PersonalAgent()
                self.assertEqual(agent.preferred_capture_moves(state, moves), [single] if exposed_pair else [pair])
                self.assertEqual(agent.preferred_capture_moves(state, [single]), [single])
                self.assertEqual(agent.preferred_capture_moves(state, []), [])
                self.assertEqual(state, before)
                self.assertEqual(moves, original_moves)
        state = initial_state(4)
        state.dice_roll = 6
        self.assertEqual(PersonalAgent().preferred_capture_moves(state, legal_moves(state, 6)), [])

    def test_safe_capture_moves(self):
        for pair in (False, True):
            for exposed in (False, True):
                with self.subTest(pair=pair, exposed=exposed):
                    state = initial_state(4)
                    state.dice_roll = 4 if pair else 2
                    selected = (0, 1) if pair else (0,)
                    for piece_id in selected:
                        state.players[0].pieces[piece_id].position = 14
                        state.players[1].pieces[piece_id].position = 3
                        if exposed:
                            # Yellow starts on shared safe square 14 and can
                            # recapture Red on unsafe square 16 next turn.
                            state.players[2].pieces[piece_id].position = 40
                    move = Move(0, selected)
                    self.assertIn(move, legal_moves(state, state.dice_roll))
                    before = deepcopy(state)
                    actual = PersonalAgent().safe_capture_moves(state, [move])
                    self.assertEqual(actual, [] if exposed else [move])
                    self.assertEqual(state, before)
        state = initial_state(4)
        state.dice_roll = 6
        self.assertEqual(PersonalAgent().safe_capture_moves(state, legal_moves(state, 6)), [])
        self.assertEqual(PersonalAgent().safe_capture_moves(state, []), [])

    def test_win_preventing_moves(self):
        for label, green_position, blue_threat, expected in (
            ("capture prevents win", 51, False, [(0,)]),
            ("private lane cannot be captured", 56, False, []),
            ("another threat remains", 51, True, []),
            ("no emergency", 40, False, []),
        ):
            with self.subTest(case=label):
                state = initial_state(4)
                state.dice_roll = 2
                state.players[0].pieces[0].position = 10
                state.players[0].pieces[1].position = 20
                # Green relative 51 is shared square 12, capturable by Red 10->12.
                for piece, position in zip(state.players[1].pieces, [57, 57, 57, green_position]):
                    piece.position = position
                if blue_threat:
                    for piece, position in zip(state.players[3].pieces, [57, 57, 57, 56]):
                        piece.position = position
                moves = legal_moves(state, 2)
                before, original_moves = deepcopy(state), deepcopy(moves)
                agent = PersonalAgent()
                actual = agent.win_preventing_moves(state, moves)
                self.assertEqual([m.piece_ids for m in actual], expected)
                self.assertEqual(agent.win_preventing_moves(state, []), [])
                self.assertEqual(state, before)
                self.assertEqual(moves, original_moves)

    def test_winning_threats_preserve_perspective_after_turn_advances(self):
        state = initial_state(4)
        state.dice_roll = 2
        state.players[0].pieces[0].position = 20
        for piece, position in zip(state.players[1].pieces, [57, 57, 57, 51]):
            piece.position = position
        agent = PersonalAgent()
        after = agent.simulate_move(state, Move(0, (0,)))
        self.assertEqual(after.current_player().player_id, 1)
        before = deepcopy(after)
        self.assertEqual(agent.immediate_winning_threats(after, player_id=0), [(1, 6)])
        self.assertEqual(after, before)

    def test_immediate_winning_threats(self):
        cases = (
            ("single", {1: [57, 57, 57, 56]}, [(1, 1)]),
            ("pair", {2: [57, 57, 55, 55]}, [(2, 4)]),
            ("multiple opponents", {1: [57, 57, 57, 51], 3: [57, 57, 54, 54]}, [(1, 6), (3, 6)]),
            ("exclude current player", {0: [57, 57, 57, 56]}, []),
            ("two separate unfinished pieces", {1: [57, 57, 55, 56]}, []),
            ("game ended", {1: [57, 57, 57, 56], 2: [57, 57, 57, 57]}, []),
        )
        for label, placements, expected in cases:
            with self.subTest(case=label):
                state = initial_state(4)
                state.dice_roll, state.remaining_rolls = 3, [2]
                for owner, positions in placements.items():
                    for piece, position in zip(state.players[owner].pieces, positions):
                        piece.position = position
                before = deepcopy(state)
                self.assertEqual(PersonalAgent().immediate_winning_threats(state), expected)
                self.assertEqual(state, before)

    def test_capture_moves(self):
        state = initial_state(4)
        state.dice_roll = 2
        state.players[0].pieces[0].position = 14
        state.players[0].pieces[1].position = 20
        state.players[1].pieces[0].position = 3
        moves = legal_moves(state, 2)
        before, original_moves = deepcopy(state), deepcopy(moves)
        agent = PersonalAgent()
        self.assertEqual(agent.capture_moves(state, moves), [Move(0, (0,))])
        self.assertEqual(agent.capture_moves(state, [Move(0, (1,))]), [])
        self.assertEqual(agent.capture_moves(state, []), [])
        self.assertEqual(state, before)
        self.assertEqual(moves, original_moves)

    def test_captured_pieces(self):
        cases = (
            ("single", [(0, 0, 14), (1, 0, 3)], 2, (0,), [(1, 0, 3)]),
            ("pair", [(0, 0, 14), (0, 1, 14), (1, 0, 3), (1, 1, 3)], 4, (0, 1), [(1, 0, 3), (1, 1, 3)]),
            ("safe square", [(0, 0, 20), (1, 0, 9)], 2, (0,), []),
            ("yard pieces are not captures", [], 6, (0,), []),
        )
        for label, placements, roll, selected, expected in cases:
            with self.subTest(case=label):
                state = initial_state(4)
                state.dice_roll = roll
                for owner, piece, position in placements:
                    state.players[owner].pieces[piece].position = position
                before = deepcopy(state)
                captured = PersonalAgent().captured_pieces(state, Move(0, selected))
                self.assertEqual([(p.player_id, p.piece_id, p.position) for p in captured], expected)
                self.assertEqual(state, before)

    def test_deployment_or_protection(self):
        cases = (
            ("below halfway", [(0, 0, 26), (1, 0, 12)], 6, [(1,), (2,), (3,)]),
            # Position 27 itself is safe, so it does not need protection.
            ("halfway boundary is safe", [(0, 0, 27), (1, 0, 12)], 6, [(1,), (2,), (3,)]),
            ("advanced savable", [(0, 0, 28), (2, 0, 1)], 6, [(0,)]),
            ("advanced unsavable", [(0, 0, 30), (2, 0, 1), (1, 0, 20)], 6, [(1,), (2,), (3,)]),
            ("no deployment protect lower", [(0, 0, 20), (1, 0, 5)], 2, [(0,)]),
            ("neither available", [], 3, []),
        )
        for label, placements, roll, expected in cases:
            with self.subTest(case=label):
                state = initial_state(4)
                state.dice_roll = roll
                for owner, piece, position in placements:
                    state.players[owner].pieces[piece].position = position
                moves = legal_moves(state, roll)
                before, original_moves = deepcopy(state), deepcopy(moves)
                actual = PersonalAgent().deployment_or_protection(state, moves)
                self.assertEqual([move.piece_ids for move in actual], expected)
                self.assertEqual(state, before)
                self.assertEqual(moves, original_moves)

    def test_protection_minimum_position(self):
        state = initial_state(4)
        state.dice_roll = 6
        state.players[0].pieces[0].position = 26
        state.players[1].pieces[0].position = 12
        moves = legal_moves(state, 6)
        agent = PersonalAgent()
        self.assertEqual([m.piece_ids for m in agent.protective_moves(state, moves, 26)], [(0,)])
        self.assertEqual(agent.protective_moves(state, moves, 27), [])

    def test_deployment_moves(self):
        for positions, roll, expected in (
            ([0, 0, 10, 20], 6, [(0,), (1,)]),
            ([0, 0, 0, 0], 3, []),
            ([1, 1, 0, 0], 6, []),  # Own pair fills the starting square.
            ([10, 20, 30, 40], 6, []),
        ):
            with self.subTest(positions=positions, roll=roll):
                state = initial_state(4)
                state.current_player_index = 2
                state.dice_roll = roll
                for piece, position in zip(state.current_player().pieces, positions):
                    piece.position = position
                moves = legal_moves(state, roll)
                before, original_moves = deepcopy(state), deepcopy(moves)
                actual = PersonalAgent().deployment_moves(state, moves)
                self.assertEqual([move.piece_ids for move in actual], expected)
                self.assertEqual(PersonalAgent().deployment_moves(state, []), [])
                self.assertEqual(state, before)
                self.assertEqual(moves, original_moves)

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
