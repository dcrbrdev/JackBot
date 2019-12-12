

class ObserverNotRegisteredError(Exception):
    """
    Exception responsible for missing Observer registry
    """
    pass


class ObserverAlreadyRegisteredError(Exception):
    """
    Exception responsible for duplicated Observer registry
    """
    pass
