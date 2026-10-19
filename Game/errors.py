class InvalidMoveError(ValueError):
    """The requested action is not legal in the current game."""
    pass

class AgentRetryLimitError(RuntimeError):
    """ The agent exhausted its allowed attempts for the current roll"""
    pass

