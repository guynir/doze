class DozeException(Exception):
    """
    Framework top-most exception. All other exceptions in this framework inherit from this one.
    """

    def __init__(self, message: str):
        """
        Class initializer.

        :param message:  Error message.
        """
        self._message: str = message

    @property
    def message(self) -> str:
        """
        :return: Error message.
        """
        return self._message


class InvalidArgumentException(DozeException):
    """
    Indicates that the user passed an invalid argument (something that is not supported by the call).
    """
    pass


class InvalidStateException(DozeException):
    """
    Indicates that an object or state is not in expected condition.
    """
    pass
