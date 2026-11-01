"""Short capture demo: python3 Check.py. Permanent checks live in Tests/."""
from Game.models import initial_state, Move
from Game.audit import snapshot_state
from Game.engine import play_turn


if __name__ == "__main__":
    state = initial_state(4)
    state.players[0].pieces[0].position = 14
    state.players[1].pieces[0].position = 3
    state.dice_roll = 2

    before = snapshot_state(state)
    play_turn(state, Move(0, (0,)))
    after = snapshot_state(state)

    assert after["pieces"][0]["position"] == 16
    assert after["pieces"][4]["position"] == 0

    for index in range(16):
        if index not in (0, 4):
            assert before["pieces"][index] == after["pieces"][index]

    print("Red moved to:", after["pieces"][0]["position"])
    print("Green returned to:", after["pieces"][4]["position"])
