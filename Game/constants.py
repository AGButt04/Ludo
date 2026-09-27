# This file contains the constants for the game.

YARD = 0  # Piece has not entered the board yet.
TRACK_START = 1 # First relative track position of the player.
TRACK_END = 51 # Last relative track position of the player.
HOME_START = 52 # First private home-path position.
HOME_END = 56 # Last private home-path position
FINISHED = 57 # Piece has completed its route.
TRACK_LENGTH = 52 # Physical squares on the shared track.
PIECES_PER_PLAYER = 4 # The number of pieces per player.

# The player only visits 51 shared squares even though there are 52.
# Because the square right behind the starting square is never visited.