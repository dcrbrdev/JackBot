
class DcrDataAPIError(Exception):
    pass


class ObserverNotRegisteredError(Exception):
    pass


class ObserverAlreadyRegisteredError(Exception):
    pass


class DuplicatedUpdateMessageError(Exception):
    pass


class DuplicatedSessionError(Exception):
    pass


class SessionWebSocketNotFoundError(Exception):
    pass
