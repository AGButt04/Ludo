"""Predictable dice sequences check turn handling without random test outcomes."""
import unittest
from copy import deepcopy
from unittest.mock import Mock

from Game.models import Move, initial_state
from Game.engine import roll_turn, play_turn


class RollTurnChecks(unittest.TestCase):
    def test_sequences(self):
        """Store each usable sequence without moving pieces or changing players."""
        for sequence in ([3], [6, 4], [6, 6, 2]):
            with self.subTest(sequence=sequence):
                state = initial_state(4)
                before = deepcopy(state.players)
                dice = Mock()
                dice.roll.side_effect = sequence
                roll_turn(state, dice)
                self.assertEqual(state.dice_roll, sequence[0])
                self.assertEqual(state.remaining_rolls, sequence[1:])
                self.assertEqual(state.current_player_index, 0)
                self.assertEqual(state.players, before)
                self.assertEqual(dice.roll.call_count, len(sequence))

    def test_three_sixes(self):
        """Cancel all rolls, preserve pieces, and advance once, including wraparound."""
        for count, start in ((4, 0), (4, 3), (2, 1)):
            state = initial_state(count)
            state.current_player_index = start
            state.players[0].pieces[0].position = 10
            before = deepcopy(state.players)
            dice = Mock()
            dice.roll.side_effect = [6, 6, 6]
            roll_turn(state, dice)
            self.assertIsNone(state.dice_roll)
            self.assertEqual(state.remaining_rolls, [])
            self.assertEqual(state.current_player_index, (start + 1) % count)
            self.assertEqual(state.players, before)
            self.assertEqual(dice.roll.call_count, 3)

    def test_rejected_rolls(self):
        """Pending rolls or a winner prevent rolling and leave state unchanged."""
        for scenario in ('current', 'remaining', 'winner'):
            state = initial_state(4)
            if scenario == 'current':
                state.dice_roll = 3
            elif scenario == 'remaining':
                state.remaining_rolls = [4]
            else:
                for piece in state.players[1].pieces:
                    piece.position = 57
            before = deepcopy(state)
            dice = Mock()
            with self.assertRaises(ValueError):
                roll_turn(state, dice)
            dice.roll.assert_not_called()
            self.assertEqual(state, before)

    def test_independent_roll_lists(self):
        """One game's remaining rolls must not leak into another game."""
        first, second = initial_state(2), initial_state(2)
        first.remaining_rolls.append(3)
        self.assertEqual(second.remaining_rolls, [])


class PlayTurnChecks(unittest.TestCase):
    def test_one_choice_per_roll(self):
        """Use [6, 6, 3] in order; only the selected piece moves each time."""
        state = initial_state(4)
        dice = Mock()
        dice.roll.side_effect = [6, 6, 3]
        roll_turn(state, dice)
        play_turn(state, Move(0, (0,)))
        self.assertEqual([p.position for p in state.players[0].pieces], [1, 0, 0, 0])
        self.assertEqual((state.dice_roll, state.remaining_rolls), (6, [3]))
        play_turn(state, Move(0, (1,)))
        self.assertEqual((state.dice_roll, state.remaining_rolls), (3, []))
        self.assertEqual(state.current_player_index, 0)
        play_turn(state, Move(0, (0,)))
        self.assertEqual([p.position for p in state.players[0].pieces], [4, 1, 0, 0])
        self.assertIsNone(state.dice_roll)
        self.assertEqual(state.current_player_index, 1)

    def test_forced_pass_consumes_roll(self):
        """An unusable six keeps later rolls; the last unusable roll ends the turn."""
        state = initial_state(2)
        state.current_player_index = 1
        for piece, position in zip(state.players[1].pieces, [55, 56, 57, 57]):
            piece.position = position
        state.dice_roll, state.remaining_rolls = 6, [3]
        before = deepcopy(state.players)
        play_turn(state, None)
        self.assertEqual((state.dice_roll, state.remaining_rolls), (3, []))
        self.assertEqual(state.current_player_index, 1)
        play_turn(state, None)
        self.assertIsNone(state.dice_roll)
        self.assertEqual(state.current_player_index, 0)
        self.assertEqual(state.players, before)

    def test_rejections_preserve_state(self):
        """Missing roll, voluntary pass, and illegal choice cannot consume rolls."""
        for scenario in ('missing', 'pass', 'wrong_player', 'no_moves', 'ended'):
            state = initial_state(4)
            state.dice_roll = 6
            move = Move(0, (0,))
            if scenario == 'missing':
                state.dice_roll = None
            elif scenario == 'pass':
                move = None
            elif scenario == 'wrong_player':
                move = Move(1, (0,))
                state.remaining_rolls = [2]
            elif scenario == 'no_moves':
                state.dice_roll = 3
            else:
                for piece in state.players[1].pieces:
                    piece.position = 57
            before = deepcopy(state)
            with self.assertRaises(ValueError):
                play_turn(state, move)
            self.assertEqual(state, before)

    def test_win_discards_remaining_rolls(self):
        """A win is successful completion, not an exception or another turn."""
        state = initial_state(4)
        for piece in state.players[0].pieces:
            piece.position = 57
        state.players[0].pieces[0].position = 51
        state.dice_roll, state.remaining_rolls = 6, [2]
        self.assertIsNone(play_turn(state, Move(0, (0,))))
        self.assertEqual(state.players[0].pieces[0].position, 57)
        self.assertEqual((state.dice_roll, state.remaining_rolls), (None, []))
        self.assertEqual(state.current_player_index, 0)

    def test_capture_and_finish_give_no_bonus(self):
        """Neither a capture nor finishing one piece extends an exhausted sequence."""
        for capture in (True, False):
            state = initial_state(4)
            state.players[0].pieces[0].position = 2 if capture else 55
            if capture:
                state.players[1].pieces[0].position = 43
            state.dice_roll = 2
            play_turn(state, Move(0, (0,)))
            self.assertIsNone(state.dice_roll)
            self.assertEqual(state.current_player_index, 1)
            if capture:
                self.assertEqual(state.players[1].pieces[0].position, 0)
