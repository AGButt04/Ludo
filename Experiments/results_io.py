from dataclasses import asdict
from pathlib import Path
import json
from Game.models import GameResult

def save_result(result: GameResult, path: str) -> None:
    """Append one game summary without overwriting earlier games."""
    dict_result = asdict(result)
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(dict_result) + "\n")


def load_results(path: str) -> list[GameResult]:
    """Read each nonblank JSON line back into a GameResult."""
    results = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            data = json.loads(line)
            results.append(GameResult(**data))

    return results
