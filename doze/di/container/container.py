from typing import Optional, List, Union, Self, Tuple

from doze.di.container.dependency import Dependency, generate_dependency_list
from doze.di.container.ex import UnknownComponentException, TooManyDefinitionsException
from doze.di.container.factories import StaticComponentFactory, SingletonComponentFactory
from doze.di.container.factory import ComponentFactory, T
from doze.di.container.name_resolution import ClassTypeToNameResolutionStrategy, \
    PascalToCamelCaseClassTypeResolverStrategy
from doze.di.container.repository import Repository
from doze.ex import InvalidArgumentException

# The container is also available for lookup inside the repository.
# This is the name of component assigned to the container.
CONTAINER_COMPONENT_NAME: str = "container"


class Container:
    """
    A container maintains the lifecycle of components. Each underlying implementation chooses how to register/maintain
    list of components (e.g.: from external configuration file, via programmable methods call, from database....).

    However, each component must at least support querying ('get' method) and checking availability ('exist' method).
    """

    def __init__(self):
        """
        Class initializer.
        """

        # Use to translate class name (e.g.: 'PrintService') into component name (e.g.: 'print_service').
        self._name_conversion: ClassTypeToNameResolutionStrategy = PascalToCamelCaseClassTypeResolverStrategy()

        self._repository = Repository()

        self.register_instance(self, CONTAINER_COMPONENT_NAME)

    def setup(self):
        """
        Perform setup procedure, as part of the initialization process.
        """

        # Call all factories' post initialization callbacks.
        for factory in self._repository.factories:
            factory.post_init()

    def get_component(self, key: Union[str, type[T]]) -> T:
        """
        Lookup a component by its name.

        :param key: Component key -- either component's name or component type.
        :return: Component matching the name.
        :raises UnknownComponentException: If component does not exist.
        """
        factory: Optional[ComponentFactory]

        if type(key) is str:
            # Lookup by component name.
            factory: ComponentFactory = self._repository.find_by_name(key)
            if not factory:
                raise UnknownComponentException(f"Unknown component -- {key}.")
        elif type(key) is type:
            # Quick check, to save search time.
            if not self._repository.exist(key):
                raise UnknownComponentException(f"Unknown component type: {key}.")

            # Lookup by component type.
            factories: List[Tuple[str, ComponentFactory]] = self._repository.find_by_type(key)

            # Raise error if we found too many matching components.
            # We are expected to return only 1.
            if len(factories) > 1:
                raise TooManyDefinitionsException(f"More than one components of type {key} were found (expected to "
                                                  f"have only one).")

            _, factory, = factories[0]
        else:
            # Caller provided unknown key type.
            # Perhaps we'll support other types of keys in the future.
            raise InvalidArgumentException(f"Unsupported key type: {key.__class__}. Expected either 'str' or 'type.")

        return factory.get_object()

    def exist(self, key: Union[str, type]) -> bool:
        """
        Check if a given component exist (either by name or by type).

        :param key: Either a component name or type to check with.
        :return: True if component exist, False if not.
        """
        return self._repository.exist(key)

    def register_type(self, component_type: type, component_name: Optional[str] = None) -> Self:
        """
        Register a new type of component.

        :param component_type: Type of component.
        :param component_name: Optional name for the component. If omitted, the container will generate an automatic
        name based on the component's type.
        :return: Self.
        :raises NameAlreadyDefinedException: If component by the same name is already registered.
        """
        if component_name is None:
            component_name = self._name_conversion.to_component_name(component_type)

        requirements: List[Dependency] = self._generate_component_requirements_list(component_type)
        factory: ComponentFactory = SingletonComponentFactory(component_name,
                                                              component_type,
                                                              self._repository,
                                                              requirements)
        self._repository.register_factory(component_name, factory)
        return self

    def register_types(self, first_arg, *rest_args) -> Self:
        """
        Register one or more types in bulk mode. The name of each component is derived from its type.

        :param first_arg: First component type (to make it mandatory to specify at least one component).
        :param rest_args: Rest of the components types. Optional.
        :return: Self
        :raises InvalidArgumentException: If one of the provided arguments is not a type.
        """
        # Iterate over all arguments and make sure all are types.
        all_args = [first_arg]
        all_args.extend(rest_args)

        for idx, arg in enumerate(all_args):
            if type(arg) != type:
                raise InvalidArgumentException(f"Invalid argument #{idx} -- expected a type, got a value.")

        for component_type in all_args:
            self.register_type(component_type)

        return self

    def register_instance(self, instance: any, component_name: str) -> Self:
        """
        Register an instance.

        :param instance: Instance to register.
        :param component_name: Name of component.
        :return: Self
        :raises NameAlreadyDefinedException: If component by the same name is already registered.
        """
        factory: ComponentFactory = StaticComponentFactory(component_name, self._repository, instance)
        self._repository.register_factory(component_name, factory)
        return self

    @staticmethod
    def _generate_component_requirements_list(component_type: type) -> List[Dependency]:
        """
        Generate a list of requirements for a component. The component's __init__ method is inspected for requirements.

        :param component_type: Type of component.
        :return: List of requirements.
        """
        return generate_dependency_list(component_type.__init__)
