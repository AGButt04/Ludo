"""Check one-roll recovery separately from the game runner."""
import unittest
from copy import deepcopy
from unittest.mock import Mock, patch

from Game.models import initial_state, Move
from Game.errors import AgentRetryLimitError
from run_game import play_agent_roll, run_game


class ActionRecoveryChecks(unittest.TestCase):
    def test_agent_changes_stay_in_snapshot(self):
        state = initial_state(4)
        state.dice_roll, state.remaining_rolls = 6, [4]

        def choose(snapshot, moves):
            snapshot.players[1].pieces[0].position = 57
            snapshot.remaining_rolls.clear()
            snapshot.current_player_index = 2
            return moves[0]

        self.assertTrue(play_agent_roll(state, Mock(choose_move=choose), []))
        self.assertEqual(state.players[1].pieces[0].position, 0)
        self.assertEqual(state.players[0].pieces[0].position, 1)
        self.assertEqual(state.current_player_index, 0)
        self.assertEqual(state.dice_roll, 4)

    def test_retry_receives_fresh_state_and_choices(self):
        state = initial_state(4)
        state.dice_roll, state.remaining_rolls = 6, [4]
        original = deepcopy(state)
        seen = []

        def choose(snapshot, moves):
            self.assertEqual(snapshot, original)
            self.assertEqual(moves, [Move(0, (i,)) for i in range(4)])
            seen.append(snapshot)
            if len(seen) == 1:
                snapshot.players[1].pieces[0].position = 57
                snapshot.remaining_rolls.clear()
                moves[0].player_id = 1
                moves.clear()
                return None
            return moves[0]

        rejections = []
        self.assertTrue(play_agent_roll(state, Mock(choose_move=choose), rejections))
        self.assertEqual(len(rejections), 1)
        self.assertIsNot(seen[0], seen[1])
        self.assertEqual(state.players[1].pieces[0].position, 0)
        self.assertEqual(state.dice_roll, 4)

    def test_runner_continues_after_forfeiture(self):
        """Keep red's earlier move, discard its unused rolls, then let green win."""
        state = initial_state(4)
        for piece in state.players[1].pieces:
            piece.position = 57
        state.players[1].pieces[0].position = 51
        agents = [Mock() for _ in range(4)]
        agents[0].choose_move.side_effect = [Move(0, (0,)), None, None, None]
        agents[1].choose_move.return_value = Move(1, (0,))
        with patch('run_game.initial_state', return_value=state), \
             patch('run_game.RandomAgent', side_effect=agents), \
             patch('run_game.Dice.roll', side_effect=[6, 6, 4, 6, 2]):
            result = run_game(max_turns=2)
        self.assertEqual((result.winner_id, result.turns_played, result.moves_played), (1, 2, 2))
        self.assertFalse(result.truncated)
        self.assertEqual((result.invalid_choices, result.forfeited_turns), (3, 1))
        self.assertEqual([p.position for p in state.players[0].pieces], [1, 0, 0, 0])
        self.assertEqual(agents[0].choose_move.call_count, 4)
        self.assertEqual(agents[1].choose_move.call_count, 1)
        agents[2].choose_move.assert_not_called()
        agents[3].choose_move.assert_not_called()
        self.assertIsNone(state.dice_roll)
        self.assertEqual(state.remaining_rolls, [])

    def test_retry_budget_resets_for_each_roll(self):
        state = initial_state(4)
        agents = [Mock() for _ in range(4)]
        invalid = Move(1, (0,))
        agents[0].choose_move.side_effect = [
            invalid, invalid, Move(0, (0,)),
            invalid, invalid, Move(0, (1,)), Move(0, (0,)),
        ]
        with patch('run_game.initial_state', return_value=state), \
             patch('run_game.RandomAgent', side_effect=agents), \
             patch('run_game.Dice.roll', side_effect=[6, 6, 4]):
            result = run_game(max_turns=1)
        self.assertEqual(result.moves_played, 3)
        self.assertEqual((result.invalid_choices, result.forfeited_turns), (4, 0))
        self.assertEqual(agents[0].choose_move.call_count, 7)
        self.assertEqual([p.position for p in state.players[0].pieces], [5, 1, 0, 0])

    def test_invalid_then_valid(self):
        state = initial_state(4)
        state.dice_roll, state.remaining_rolls = 6, [3]
        agent = Mock()
        agent.choose_move.side_effect = [Move(1, (0,)), Move(0, (0,))]
        rejections = []
        self.assertTrue(play_agent_roll(state, agent, rejections))
        self.assertEqual(agent.choose_move.call_count, 2)
        self.assertEqual(len(rejections), 1)
        self.assertEqual([p.position for p in state.players[0].pieces], [1, 0, 0, 0])
        self.assertEqual(state.current_player_index, 0)
        self.assertEqual(state.dice_roll, 3)

    def test_three_rejections_preserve_state(self):
        state = initial_state(4)
        state.dice_roll, state.remaining_rolls = 6, [4]
        before = deepcopy(state)
        agent = Mock()
        agent.choose_move.return_value = None  # Passing is illegal when six allows release.
        rejections = []
        with self.assertRaises(AgentRetryLimitError):
            play_agent_roll(state, agent, rejections)
        self.assertEqual(agent.choose_move.call_count, 3)
        self.assertEqual(len(rejections), 3)
        self.assertEqual(state, before)

    def test_forced_pass_never_asks_agent(self):
        state = initial_state(4)
        state.dice_roll = 3
        agent = Mock()
        rejections = []
        self.assertFalse(play_agent_roll(state, agent, rejections))
        agent.choose_move.assert_not_called()
        self.assertEqual(rejections, [])
        self.assertEqual(state.current_player_index, 1)
        self.assertIsNone(state.dice_roll)

    def test_unexpected_error_is_not_retried(self):
        state = initial_state(4)
        state.dice_roll = 6
        agent = Mock()
        agent.choose_move.side_effect = RuntimeError('Agent bug')
        with self.assertRaises(RuntimeError):
            play_agent_roll(state, agent, [])
        self.assertEqual(agent.choose_move.call_count, 1)
