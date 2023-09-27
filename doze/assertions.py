from typing import Iterable

from doze.ex import InvalidArgumentException, InvalidStateException


#
# Collection of assertion utilities to assess function/methods argument and state.
#

def assert_not_none(obj: any, message: str):
    """
    Assert that a given object is defined (not 'None'). If assertion fails, raise an InvalidArgumentException.

    :param obj: Object to evaluate.
    :param message: Error message.
    :raises InvalidArgumentException: If 'obj' is None.
    """
    if obj is None:
        raise InvalidArgumentException(message)


def assert_type(obj: any, types: Iterable[type], message: str):
    """
    Assert that a given object is of specific types. The object is also assessed as one of the sub-times. For example,
    if 'obj' is 'KeyError' and 'types' is '[Exception]', assertion will be successful.

    :param obj: Object to assert.
    :param types:  Collection of types the object me be of.
    :param message:  Error message.
    :raises InvalidArgumentException: If object is not of any provided types or sub instance of those types.
    """
    for t in types:
        if isinstance(obj, t):
            return

    raise InvalidArgumentException(message)


def assert_true(true_value: bool, message: str):
    """
    Assert that a given state is 'True'. If not, an exception is raised.

    :param true_value: Value to assert.
    :param message: Error message.
    :raises: InvalidStateException If 'state' is not True.
    """
    if not true_value:
        raise InvalidArgumentException(message)


def assert_state(state: bool, message: str):
    """
    Assert that a given state is 'True'. If not -- raises an exception.
    This method differs from 'assert_true' in that it raises an 'InvalidStateException'. This assertion is intended
    to evaluate a state, while the previous one assumes the value for assertion is an argument evaluation.

    :param state: State to assert.
    :param message: Error message.
    :raises InvalidStateException: If 'state' is not 'True'.
    """
    if not state:
        raise InvalidStateException(message)
