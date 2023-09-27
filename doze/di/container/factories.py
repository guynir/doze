import threading
from abc import ABC
from typing import Optional, Tuple, Dict

from doze.assertions import assert_state
from doze.di.container.dependency import Dependency
from doze.di.container.ex import *
from doze.di.container.factory import ComponentFactory, T
from doze.di.container.repository import Repository
from doze.ex import InvalidStateException


class DependencyCyclicDetector:
    """
    Tracks dependencies graph during component creation to detect cyclic references.
    """

    __context: Dict[int, List[str]] = {}

    def __init__(self, component_name: str):
        self._component_name: str = component_name

    def push(self, dependency_name: str):
        """
        Push dependency name into the buffer of the current context. If the name already exists, raises
        exception.

        :param dependency_name: Dependency to add.
        :raises CyclicDependencyException: If a cyclic reference detected within the graph.
        """
        context: List[str] = self._get_context()
        if dependency_name in context:
            index_of_dependency: int = context.index(dependency_name)
            cyclic_list: List[str] = context[index_of_dependency:]
            cyclic_list.append(dependency_name)
            message = f"Cyclic dependency detected: {' -> '.join(cyclic_list)}"
            raise CyclicDependencyException(message, cyclic_list)

        context.append(dependency_name)

    def pop(self, dependency_name: str):
        """
        Pop a dependency from the stack.

        :param dependency_name: Dependency name.
        :raises InvalidStateException: If the current item in the context to pop does not match 'dependency_name'.
        """
        context: List[str] = self._get_context()
        if not context:
            raise InvalidStateException("Invalid request to pop dependency from stack (stack is empty).")

        popped_dep_name: str = context.pop()
        if popped_dep_name != dependency_name:
            raise InvalidStateException(f"Invalid ")

    def __enter__(self):
        """
        Upon entrance to the protected block, register the requesting component.
        """
        self.push(self._component_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Upload leaving the protected block, de-register the requesting component.
        :param exc_type: Type of exception (ignored).
        :param exc_val: Exception instance (ignored).
        :param exc_tb: Exception trace back (ignored).
        :return:
        """
        self.pop(self._component_name)

    @staticmethod
    def _get_context() -> List[str]:
        """
        :return: Context of current thread. If no such context exist yet -- create a new one.
        """
        thread_id: int = threading.get_ident()
        context: List[str]

        if thread_id in DependencyCyclicDetector.__context:
            context = DependencyCyclicDetector.__context[thread_id]
        else:
            DependencyCyclicDetector.__context[thread_id] = context = []

        return context


class AbstractComponentFactory(ComponentFactory[T], ABC):
    """
    Abstract component factory is a small extension to the component factory. It adds a reference to the repository,
    so each factory can perform a lookup other factories it may depend on.

    The reason for its existence
    is the fact that Python does not support mutual reference (ComponentFactory class referencing Repository class
    and vise versa).
    """

    def __init__(self, component_name: str, component_type: type, repository: Repository):
        """
        Class initializer.

        :param component_name: Component name.
        :param component_type: Type of component this factory produces.
        :param repository: A reference to factories repository.
        """
        super().__init__(component_name, component_type)

        self.repository: Repository = repository

        self._initialized: bool = False

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def _set_initialized(self):
        """
        Mark this factory as initialized and ready for use.
        """
        self._initialized = True

    def _assert_initialized(self):
        """
        Makes sure that this factory is initialized (checks the 'is_initialized' property).
        If factory is not initialized, raises exception.

        :raises InvalidStateException: If factory is not initialized.
        """
        assert_state(self._initialized, "Factory not initialized.")

    def __repr__(self):
        return f"[{self.__class__.__name__}] Component type: {self.get_component_type().__name__}"


class StaticComponentFactory(AbstractComponentFactory[T]):
    """
    A static component factory is a simple factory that is initialized with a predefined/pre-created object. The factory
    will always return this instance.
    """

    def __init__(self, component_name: str, repository: Repository, instance: T):
        """
        Class initializer.

        :param component_name: Component name.
        :param repository: Repository to lookup other factories in.
        :param instance: A singleton instance this factory provides.
        """
        super().__init__(component_name, type(instance), repository)

        # The singleton instance provided by this factory.
        self._instance: T = instance

        # This factory is always ready for work !
        self._set_initialized()

    def get_object(self) -> T:
        return self._instance


class AbstractCreatingComponentFactory(AbstractComponentFactory[T], ABC):
    """
    Common parent for factories that creates new objects, such as singleton factory and prototype factory.
    """

    def __init__(self, component_name: str,
                 component_type: type,
                 repository: Repository,
                 requirements: List[Dependency]):
        super().__init__(component_name, component_type, repository)

        # List of requirements for this component.
        self._requirements: List[Dependency] = requirements

        # Maintain the list of components factories required to initialize the component provided by this factory.
        # It is initially set to 'None' but is populated by 'post_init'.
        self._init_factories: Optional[List[ComponentFactory]] = None

    def post_init(self):
        self._init_factories = []

        for idx, req in enumerate(self._requirements):
            name: Optional[str] = None
            factory: Optional[ComponentFactory] = None
            if req.component_name is not None:
                name = req.component_name
                factory = self.repository.find_by_name(req.component_name)
                if factory is not None and not factory.is_type_of(req.component_type):
                    raise TypeMismatchException(f"{self.get_component_type().__name__} (parameter #{idx}) -- "
                                                f"expected requirement of type {req.component_type.__name__} but "
                                                f"got {factory.__class__.__name__}.")

            if factory is None:
                factories: List[Tuple[str, ComponentFactory]] = self.repository.find_by_type(req.component_type)
                if len(factories) == 0:
                    raise UnknownComponentException(f"Unknown component type: {req.component_type}")

                if len(factories) > 1:
                    raise TooManyDefinitionsException(f"Non unique: Component of type "
                                                      f"'{req.component_type.__name__}' has more than 1 "
                                                      f"definition.")

                name, factory = factories[0]

            if factory is None:
                raise UnknownComponentException(f"Unknown component type: {req.component_type}")

            self._init_factories.append(factory)
            self._init_dependencies.append(name)

        # We're ready !
        self._set_initialized()

    def _create_component(self) -> T:
        """
        Creates a new instance of the component.
        """

        with DependencyCyclicDetector(self._component_name):
            # Make sure we are actually ready for creating new component.
            self._assert_initialized()

            # Given all factories -- generate components that are required by this component.
            args: List[any] = [f.get_object() for f in self._init_factories]
            return self._component_type(*args)


class SingletonComponentFactory(AbstractCreatingComponentFactory[T]):
    """
    A factory that provides a singleton component. The first call will create the component. All further requests
    will return the same instance.
    """

    def __init__(self, component_name: str,
                 component_type: type,
                 repository: Repository,
                 requirements: List[Dependency]):
        super().__init__(component_name, component_type, repository, requirements)

        # Singleton.
        self._instance: T = None

    def get_object(self) -> T:
        # If singleton instance not yet created -- lazy create it.
        if self._instance is None:
            self._instance = self._create_component()

        return self._instance


class PrototypeComponentFactory(AbstractCreatingComponentFactory[T]):
    """
    A factory that creates a new component each time it is called.
    """

    def __init__(self, component_name: str,
                 component_type: type,
                 repository: Repository,
                 requirements: List[Dependency]):
        super().__init__(component_name, component_type, repository, requirements)

    def get_object(self) -> T:
        """
        Creates a new component each call.
        :return: New component.
        """
        return self._create_component()
