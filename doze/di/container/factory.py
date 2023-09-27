from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

from doze.di.container.ex import TypeMismatchException, UnknownComponentException

# Component type.
T = TypeVar('T')


class ComponentFactory(ABC, Generic[T]):

    def __init__(self, component_name: str, component_type: type):
        """
        Class initializer.

        :param component_name: Name of component.
        :param component_type: Type of component produced by this factory.
        """
        self._component_name: str = component_name
        self._component_type: type = component_type

        # Indicates if this factory is initialized and ready for use (or not).
        self._initialized: bool = False

        # Maintain list of __init__ components names for this factory.
        self._init_dependencies: List[str] = []

    def post_init(self):
        """
        A life-cycle callback initiated by the container to perform further initialization steps which are
        beyond those of the __init__ method.

        This callback is issued once during the component's lifecycle.
        """
        pass

    @abstractmethod
    def get_object(self) -> T:
        """
        :return: An instance of the component.
        """
        pass

    def get_component_type(self) -> type:
        """
        :return: Type of component provided by this factory.
        """
        return self._component_type

    # noinspection PyMethodMayBeStatic
    def get_init_dependencies(self) -> List[str]:
        """
        Provide list of dependencies required by this factory to create component.
        :return: List of requirements.
        """
        return self._init_dependencies

    def is_type_of(self, cls: type) -> bool:
        """
        Provide indication if this factory provides an object of a type which is either equal or descendant of
        a given type.

        :param cls: Class type to check against.
        :return: True if this factory provides a class that is either equal or a descendant or 'cls'. False if not.
        """
        return issubclass(self._component_type, cls)

    @property
    def is_initialized(self) -> bool:
        """
        Provide indication if this instance is initialized and ready for use.
        :return: True if factory is fully initialized, False if not.
        """
        return self._initialized
