from copy import deepcopy
from Game.models import GameState, Move
from Game.engine import play_turn
from Game.rules import has_won, get_move_pieces
from Game.constants import TRACK_START, TRACK_END, YARD
from Game.rules import to_absolute, is_safe_square, legal_moves


class PersonalAgent:
    # Rule-1:
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
    
    # Emergency priority: Prevent an immediate opponent win.
    def immediate_winning_threats(self, state):
        winning_threats = []

        if player_id is None:
            player_id = state.current_player().player_id


        for participant in state.players:
            if has_won(state, participant.player_id):
                return []

        for index, opponent in enumerate(state.players):
            if opponent.player_id == player_id:
                continue
            
            copy_state = deepcopy(state)
            copy_state.current_player_index = index
            copy_state.remaining_rolls = []

            for roll in range(1, 7):
                copy_state.dice_roll = roll
                moves = legal_moves(copy_state, roll)

                for move in moves:
                    result_state = self.simulate_move(copy_state, move)

                    if has_won(result_state, opponent.player_id):
                        winning_threats.append((opponent.player_id, roll))
                        break
        
        return winning_threats
    
    # Rule-2:
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

    def threatened_pieces(self, state):
        player = state.current_player()
        threatened = []

        for piece in player.pieces:
            threats =  self.capture_threats(
                state, player.player_id, piece.piece_id
            )

            if threats:
                threatened.append(piece)
        
        threatened.sort(key=lambda piece: piece.position, reverse=True)
        return threatened

    def protective_moves(self, state, moves, minimum_position=TRACK_START):
        for piece in self.threatened_pieces(state):
            if piece.position < minimum_position:
                continue

            saving_moves = []

            for move in moves:
                # Simulate this move.
                sim_state = self.simulate_move(state, move)

                # Check this piece's threats in the resulting state.
                threats = self.capture_threats(sim_state, piece.player_id, piece.piece_id)

                # If none remain, append move to saving_moves.
                if not threats:
                    saving_moves.append(move)

            if saving_moves:
                return saving_moves

        return []
    
    # Rule-3:
    def deployment_moves(self, state, moves):
        deploying = []

        for move in moves:
            _, pieces = get_move_pieces(state, move)

            # Legal deployment moves select one piece in the yard.
            if len(pieces) == 1 and pieces[0].position == YARD:
                deploying.append(move)
        
        return deploying
    
    def deployment_or_protection(self, state, moves):
        dep_moves = self.deployment_moves(state, moves)

        if dep_moves:
            protect_moves = self.protective_moves(state, moves, 27)
            
            if protect_moves:
                # Deployment available and advanced piece savable
                return protect_moves
            
            # Deployment available and advanced piece not savable
            return dep_moves

        # Deployment unavailable
        return self.protective_moves(state, moves)

    # Rule-4:
    def captured_pieces(self, state, move):
        after = self.simulate_move(state, move)
        captured = []

        for player in state.players:
            if player.player_id == move.player_id:
                continue
            
            for piece in player.pieces:
                _, pieces_after = get_move_pieces(
                    after, Move(player.player_id, (piece.piece_id, ))
                )

                if piece.position != YARD and pieces_after[0].position == YARD:
                    captured.append(piece)
            
        return captured
    
    def capture_moves(self, state, moves):
        capturing = []

        for move in moves:
            cap_pieces = self.captured_pieces(state, move)

            if cap_pieces:
                capturing.append(move)
        
        return capturing