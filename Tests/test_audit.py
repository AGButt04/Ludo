"""Preserve snapshots and compare whole states against hand-calculated moves."""
import unittest
from copy import deepcopy

from Game.audit import snapshot_state
from Game.engine import play_turn
from Game.models import initial_state, Move


class AuditChecks(unittest.TestCase):
    def test_snapshot_is_independent(self):
        state = initial_state(4)
        state.dice_roll, state.remaining_rolls = 6, [4]
        snapshot = snapshot_state(state)
        saved = deepcopy(snapshot)
        self.assertEqual(len(snapshot['pieces']), 16)
        self.assertEqual(
            [(p['player_id'], p['piece_id']) for p in snapshot['pieces']],
            [(player, piece) for player in range(4) for piece in range(4)],
        )
        state.players[0].pieces[0].position = 11
        state.remaining_rolls.clear()
        state.dice_roll = None
        state.current_player_index = 1
        self.assertEqual(snapshot, saved)

    def test_capture_changes_only_selected_and_captured_pieces(self):
        state = initial_state(4)
        state.players[0].pieces[0].position = 14
        state.players[1].pieces[0].position = 3  # Shared square 16.
        state.dice_roll = 2
        expected = snapshot_state(state)
        expected['pieces'][0]['position'] = 16
        expected['pieces'][4]['position'] = 0
        expected['dice_roll'] = None
        expected['current_player_id'] = 1
        play_turn(state, Move(0, (0,)))
        self.assertEqual(snapshot_state(state), expected)

    def test_passage_preserves_opposing_blockade(self):
        # Single crosses safe square 14; pair crosses unsafe square 16.
        for start, green_position, selected, roll, destination in (
            (12, 1, (0,), 4, 16),
            (14, 3, (0, 1), 6, 17),
        ):
            with self.subTest(selected=selected):
                state = initial_state(4)
                for piece_id in selected:
                    state.players[0].pieces[piece_id].position = start
                for piece_id in (0, 1):
                    state.players[1].pieces[piece_id].position = green_position
                state.dice_roll, state.remaining_rolls = roll, [2]
                expected = snapshot_state(state)
                for piece_id in selected:
                    expected['pieces'][piece_id]['position'] = destination
                expected['dice_roll'] = 2
                expected['remaining_rolls'] = []
                play_turn(state, Move(0, selected))
                self.assertEqual(snapshot_state(state), expected)
