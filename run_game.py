from Game.models import initial_state
from Game.dice import Dice
from Agents.random_agent import RandomAgent
from Game.rules import legal_moves, has_won
from Game.engine import play_turn, roll_turn

def run_game(num_players=4, seed=0, max_turns=10000, starting_player_index = 0) -> int | None:
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

            if has_won(state, current_player.player_id):
                return current_player.player_id
    
    return None

if __name__ == "__main__":
    result = run_game()

    if result is not None:
        print(f"The winner is {result}")
    else:
        print("Turn limit reached; no winner determined.")
