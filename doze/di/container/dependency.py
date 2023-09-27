import inspect
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Callable

from doze.assertions import assert_true

IGNORED_PARAMETERS_NAMES: List[str] = ["self", "args", "kwargs"]


class DependencyType(Enum):
    """
    Type of requirement. May be 'simple' to indicate a single object, or list/set/dictionary to indicate that this
    requirement represents a collection.
    """

    SIMPLE = 1
    LIST = 1
    SET = 2
    DICTIONARY = 3


@dataclass
class Dependency:
    """
    Represents a requirement for injection.
    """

    # Optional component name.
    component_name: Optional[str]

    # Component type.
    component_type: type

    # Type of requirement.
    dependency_type: DependencyType


def generate_dependency_list(c: Callable) -> List[Dependency]:
    """
    Generate a list of dependencies for a function or a method.

    :param c: Function (or class method) to be inspected.
    :return: List of dependencies.
    :raises InvalidStateException: If provided argument is not a class method or a function.
    """
    dependencies: List[Dependency] = []

    assert_true(callable(c), "Argument is expected to a callable function or class method.")
    assert_true(not inspect.isclass(c), "Argument cannot be a class (must either be function or class method).")

    sig: inspect.Signature = inspect.signature(c)
    for _, param_conf in sig.parameters.items():
        name: str = param_conf.name
        cls: type = param_conf.annotation if param_conf.annotation != inspect.Parameter.empty else object
        if name not in IGNORED_PARAMETERS_NAMES:
            dependencies.append(Dependency(name, cls, DependencyType.SIMPLE))

    return dependencies
