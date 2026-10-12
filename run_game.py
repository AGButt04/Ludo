from Game.models import initial_state, GameResult
from Game.dice import Dice
from Agents.random_agent import RandomAgent
from Game.rules import legal_moves, has_won
from Game.engine import play_turn, roll_turn

def run_game(num_players=4, seed=0, max_turns=10000, starting_player_index = 0) -> GameResult:
    if type(seed) is not int:
        raise TypeError("Seed must be an integer.")
    if type(max_turns) is not int:
        raise TypeError("Max turns must be an integer.")
    if max_turns <= 0:
        raise ValueError("Max turns has to be positive.")
        
    state = initial_state(num_players)
    
    if type(starting_player_index) is not int:
        raise TypeError("Starting player index must be an integer.")
    if not 0 <= starting_player_index < len(state.players):
        raise ValueError("Starting player index must identify a participating seat.")
    
    state.current_player_index = starting_player_index
    dice = Dice(seed)
    random_agents = {}

    game_result = GameResult(
        winner_id=None,
        seed=seed,
        num_players=num_players,
        starting_player_index=starting_player_index,
        max_turns=max_turns,
        turns_played=0,
        moves_played=0,
        truncated=False,
    )

    
    for player in state.players:
        r_agent = RandomAgent(seed + 1 + player.player_id)
        random_agents[player.player_id] = r_agent

    for turn in range(max_turns):
        roll_turn(state, dice)

        while state.dice_roll is not None:
            current_player = state.current_player()
            moves = legal_moves(state, state.dice_roll)

            agent = random_agents[current_player.player_id]
            move = agent.choose_move(state, moves)
            play_turn(state, move)

            if move is not None: 
                game_result.moves_played += 1

            if has_won(state, current_player.player_id):
                game_result.winner_id = current_player.player_id
                game_result.turns_played = turn + 1
                game_result.truncated = False
                
                return game_result
    
    game_result.winner_id = None
    game_result.turns_played = max_turns
    game_result.truncated = True

    return game_result

if __name__ == "__main__":
    result = run_game()

    if result.winner_id is not None:
        print(f"Winner: {result.winner_id} | Turns: {result.turns_played} | Moves: {result.moves_played}")
    else:
        print(f"Turn limit reached | Turns: {result.turns_played} | Moves: {result.moves_played}")
