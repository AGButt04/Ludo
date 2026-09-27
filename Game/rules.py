from Game.constants import YARD, TRACK_START, FINISHED

def destination_for_roll(position: int, dice_roll: int):
    if type(position) is not int or type(dice_roll) is not int:
        raise TypeError("The type of the dice_roll and position has to be an integer.")
    
    if not YARD <= position <= FINISHED:
        raise ValueError("The position has to be between 0 and 57.")
    if not 1 <= dice_roll <= 6:
        raise ValueError("The dice roll has to be between 1 and 6.")
    
    if position == 0 and dice_roll == 6:
        return TRACK_START
    elif position == 0:
        return None
    elif position == FINISHED:
        return None
    else:
        new_pos = position + dice_roll
        return new_pos if (new_pos <= FINISHED) else None