from Game.models import GameResult
from run_game import run_game
from Experiments.results_io import save_result, load_results
from pathlib import Path

def run_batch(num_games: int, output_path: str, base_seed: int = 0, num_players: int = 4, max_turns: int = 10000) -> list[GameResult]:
    for name, value in (
        ("num_games", num_games),
        ("base_seed", base_seed),
        ("num_players", num_players),
        ("max_turns", max_turns)
    ):    
        if type(value) is not int:
            raise TypeError(f"{name} must be an integer")

    if num_games <= 0 or max_turns <= 0:
        raise ValueError("num_games and max_turns must be positive")

    if num_players not in (2, 4):
        raise ValueError("num_players must be 2 or 4")
    
    if Path(output_path).exists():
        raise FileExistsError("Use a new output file for this batch.")
    
    results = []

    for game in range(num_games):
        seed = base_seed + game
        starting_player_index = game % num_players

        result = run_game(num_players, seed, max_turns, starting_player_index)
        results.append(result)
        save_result(result, output_path)
    
    return results

def summarize_results(results: list[GameResult]) -> dict:
    if results:
        num_players = results[0].num_players

        if any(result.num_players != num_players for result in results):
            raise ValueError("Cannot combine two-player and four-player results.")

    completed = 0
    cutoffs = 0
    total_turns = 0
    total_moves = 0
    wins = {}
    total_games = len(results)

    if results:
        for player_id in range(num_players):
            wins[player_id] = 0
    
    for result in results:
        total_moves += result.moves_played
        total_turns += result.turns_played

        if result.truncated:
            cutoffs += 1
        else:
            completed += 1
            wins[result.winner_id] += 1

    player_win_rate = {}
    for player_id, win_count in wins.items():
        player_win_rate[player_id] = win_count / completed if completed > 0 else None

    # These averages include cutoff games; win rates use only completed games.
    avg_turns = total_turns / total_games if total_games > 0 else None
    avg_moves = total_moves / total_games if total_games > 0 else None

    return {
        "total_games": total_games,
        "completed_games": completed,
        "cutoffs": cutoffs,
        "wins_by_player": wins,
        "win_rates_completed_games": player_win_rate,
        "average_turns_all_games": avg_turns,
        "average_moves_all_games": avg_moves,
    }

    
