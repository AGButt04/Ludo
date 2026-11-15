from copy import deepcopy
from Game.models import GameState, Move
from Game.engine import play_turn
from Game.rules import has_won, get_move_pieces
from Game.constants import TRACK_START, TRACK_END, YARD
from Game.rules import to_absolute, is_safe_square, legal_moves


class PersonalAgent:
    def simulate_move(self, state: GameState, move: Move) -> GameState:
        state_copy = deepcopy(state)
        play_turn(state_copy, move)

        return state_copy

    def winning_moves(self, state, moves) -> list[Move]:
        win_moves = []
        player_id = state.current_player().player_id

        for move in moves:
            state_copy = self.simulate_move(state, move)

            if has_won(state_copy, player_id):
                win_moves.append(move)
        
        return win_moves
    
    def capture_threats(self, state, player_id, piece_id) -> list[tuple[int, int]]:
        player, pieces = get_move_pieces(
            state, Move(player_id, (piece_id, ))
        )

        target = pieces[0]

        for participant in state.players:
            if has_won(state, participant.player_id):
                return []

        if not TRACK_START <= target.position <= TRACK_END:
            return []
        
        square = to_absolute(player.color, target.position)

        if is_safe_square(square):
            return []
        
        threats = []

        for index, opponent in enumerate(state.players):
            if opponent.player_id == player_id:
                continue
            
            opponent_state = deepcopy(state)
            opponent_state.current_player_index = index
            opponent_state.remaining_rolls = []

            for roll in range(1, 7):
                opponent_state.dice_roll = roll
                moves = legal_moves(opponent_state, roll)

                for move in moves:
                    result_state = self.simulate_move(opponent_state, move)

                    _, pieces_after = get_move_pieces(
                        result_state, Move(player_id, (piece_id, ))
                    )

                    if pieces_after[0].position == YARD:
                        threats.append((opponent.player_id, roll))
                        break

        return threats



