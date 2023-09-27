from typing import List, Dict, Optional, Set, Union, Tuple

from doze.di.container.ex import NameAlreadyDefinedException
from doze.di.container.factory import ComponentFactory
from doze.ex import InvalidArgumentException


class Repository:
    """
    The repository maintains factories and allows quick lookup facilities to factories.
    """

    def __init__(self):
        """
        Class initializer.
        """

        # List of all available factories.
        self.factories: List[ComponentFactory] = []

        # Dictionary of factories, mapped by name.
        self.factory_by_name: Dict[str, ComponentFactory] = {}

        # A quick lookup set of all known component types.
        self.available_component_types: Set[type] = set()

    def find_by_name(self, component_name: str) -> Optional[ComponentFactory]:
        """
        Find a component factory by name.

        :param component_name: Name to look by.
        :return: Component factory matching name or None if no such factory found.
        """
        return self.factory_by_name.get(component_name, None)

    def find_by_type(self, component_type: type) -> List[Tuple[str, ComponentFactory]]:
        """
        Find all component factories supporting a given type.

        :param component_type: Component type to look by.
        :return: List of tuples of names / factories of the given type. If no such factory found, an empty list is
        returned.
        """
        return [(fp[0], fp[1]) for fp in self.factory_by_name.items() if fp[1].is_type_of(component_type)]

    def register_factory(self, component_name: str, factory: ComponentFactory):
        """
        Register a new factory in this repository.

        :param component_name: Name of component the factory produces.
        :param factory: Factory to register.
        :raises NameAlreadyDefinedException: If a component factory with the same name already registered.
        """
        if component_name in self.factory_by_name:
            raise NameAlreadyDefinedException(f"Component by the name '{component_name}' already defined in "
                                              f"repository.")

        self.factory_by_name[component_name] = factory
        self.factories.append(factory)
        self.available_component_types.add(factory.get_component_type())

    def exist(self, key: Union[str, type]) -> bool:
        """
        Check if a given factory, denoted either by name or type, exist in this repostory.
        :param key: Key to look by. It may be either string or type of component.
        :return: True if factory exist, False if not.
        :raises InvalidArgumentException: If key is not of either string or type.
        """
        if type(key) is str:
            return key in self.factory_by_name
        elif type(key) is type:
            return key in self.available_component_types
        else:
            raise InvalidArgumentException(f"Unsupported key type: {key.__name__}.")
