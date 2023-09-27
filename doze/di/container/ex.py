from typing import List

from doze.ex import DozeException


class NameAlreadyDefinedException(DozeException):
    """ Raised when a component name is already used by another component. """
    pass


class UnknownComponentException(DozeException):
    """ Raised when component is unknown (either by type lookup or by name). """
    pass


class TooManyDefinitionsException(DozeException):
    """ Raised when a single component is required (typically, by name) but more than one was found. """
    pass


class TypeMismatchException(DozeException):
    pass


class CyclicDependencyException(DozeException):
    """
    Indicates that a cyclic reference detected within components graph.
    """

    def __init__(self, message: str, cyclic_list: List[str]):
        """
        Class initializer.

        :param message: Error message.
        :param cyclic_list: List of dependencies that generates a cyclic reference.
        """
        super().__init__(message)

        self.cyclic_list: List[str] = cyclic_list
