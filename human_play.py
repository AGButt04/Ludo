from Game.models import GameState, Move, initial_state
from Game.dice import Dice
from Game.engine import roll_turn, play_turn
from Game.rules import legal_moves, has_won, move_destination
from Game.constants import YARD, HOME_START, FINISHED
from Agents.random_agent import RandomAgent
from run_game import play_agent_roll
from Game.errors import AgentRetryLimitError
from Game.engine import forfeit_turn

def position_label(position: int) -> str:
    if position == YARD:
        return "Yard"
    if position == FINISHED:
        return "Done"
    if position >= HOME_START:
        return f"Home {position - HOME_START + 1}"
    return str(position)


def display_turn(state: GameState, moves: list[Move]) -> None:
    print("\n" + "─" * 52)
    print(f"{'Pieces':<16}" + "".join(f'{i:<9}' for i in range(4)))
    for player in state.players:
        name = player.color.name + (" (you)" if player.player_id == 0 else "")
        positions = "".join(f'{position_label(p.position):<9}' for p in player.pieces)
        print(f"{name:<16}{positions}")
    print("Positions show each piece's relative progress.")
    remaining = ", ".join(map(str, state.remaining_rolls)) or "none"
    print(f"\nYour roll: {state.dice_roll} | Remaining: {remaining}\n")

    for number, move in enumerate(moves, start=1):
        player = state.current_player()
        piece = next(p for p in player.pieces if p.piece_id == move.piece_ids[0])
        destination = move_destination(state, move, state.dice_roll)
        selection = " + ".join(map(str, move.piece_ids))
        label = "Pair" if len(move.piece_ids) == 2 else "Piece"
        print(f"  {number}. {label} {selection}: {position_label(piece.position)} → {position_label(destination)}")
    print("  q. Quit\n")


def display_changes(state: GameState, before: dict, name: str, roll: int) -> None:
    """Describe actual movement and captures after an action succeeds."""
    changes = []
    for player in state.players:
        for piece in player.pieces:
            old = before[(player.player_id, piece.piece_id)]
            if old == piece.position:
                continue
            if piece.position == YARD:
                changes.append(f"captured {player.color.name} piece {piece.piece_id}")
            else:
                changes.append(f"piece {piece.piece_id}: {position_label(old)} → {position_label(piece.position)}")
    print(f"{name} rolled {roll}: " + "; ".join(changes))

def choose_human_move(moves: list[Move]) -> Move | None:
    while True:
        try:
            choice = input("Choose a move number (q to quit): ").strip().lower()
        except EOFError:
            return None
        
        if choice == "q":
            return None

        try:
            number = int(choice)
        except ValueError:
            print("That was not a valid input.")
            continue
        
        if 1 <= number <= len(moves):
            return moves[number - 1]
        
        print("Choose a number from the displayed moves.")

def play_human_game():
    state = initial_state(4)
    dice = Dice(0)
    human_player_id = 0

    agents = {
        player.player_id: RandomAgent(player.player_id + 1)
        for player in state.players
        if player.player_id != human_player_id
    }

    while True:
        name = state.current_player().color.name
        roll_turn(state, dice)
        if state.dice_roll is None:
            print(f"{name}: three sixes — turn cancelled.")

        while state.dice_roll is not None:
            player_id = state.current_player().player_id
            name = state.current_player().color.name
            roll = state.dice_roll
            moves = legal_moves(state, state.dice_roll)
            before = {(p.player_id, piece.piece_id): piece.position
                      for p in state.players for piece in p.pieces}

            if not moves:
                print(f"{name} rolled {roll}: no legal moves; passing.")
                play_turn(state, None)
            elif player_id != human_player_id:
                try:
                    play_agent_roll(state, agents[player_id], [])
                except AgentRetryLimitError:
                    print(f"{name}: three invalid choices; forfeits the remaining turn.")
                    forfeit_turn(state)
                    break
            else:
                display_turn(state, moves)
                move = choose_human_move(moves)

                if move is None:
                    print("Game ended by user.")
                    return
                
                play_turn(state, move)

            if moves:
                display_changes(state, before, name, roll)
            if has_won(state, player_id):
                print(f"\n{name} wins!")
                return


if __name__ == "__main__":
    play_human_game()
