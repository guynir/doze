from unittest import TestCase

from doze.di.container.container import Container
from doze.di.container.ex import UnknownComponentException, CyclicDependencyException


class SampleClass:
    """ Sample class for testing. """
    pass


class InjectableComponent:
    """ Sample class for testing. """

    def __init__(self, sample_class: SampleClass):
        self.val = sample_class


class InjectableContainer:
    """ Sample class for testing. """

    def __init__(self, container: Container):
        self.container: Container = container


class TestContainer(TestCase):
    """
    Collection of test cases for 'Container' and associated/helping classes.
    """

    def setUp(self) -> None:
        """ Test fixture -- create a new instance before each test is executed. """
        self.container = Container()

    def test_should_return_static_singleton(self):
        """
        Test should return the singleton instance registered in the container.
        """
        obj: str = "Hello, world !!!"
        self.container.register_instance(obj, "message")
        self.container.setup()

        result: str = self.container.get_component("message")
        self.assertEqual(obj, result)

    def test_should_return_dynamically_created_singleton(self):
        """
        Test should return a new instance of the component type registered.
        """
        self.container.register_type(SampleClass)
        self.container.setup()

        result: SampleClass = self.container.get_component(SampleClass)
        self.assertEqual(SampleClass, type(result))

    def test_should_not_find_any_match_by_name(self):
        """
        Test should raise an exception after requesting a non-existing component (denoted by its name).
        """
        with self.assertRaises(UnknownComponentException):
            self.container.setup()
            self.container.get_component("non_existing")

    def test_should_not_find_any_match_by_type(self):
        """
        Test should raise an exception after requesting a non-existing component (denoted by its type).
        """
        with self.assertRaises(UnknownComponentException):
            self.container.setup()
            self.container.get_component(SampleClass)

    def test_should_inject_component_by_name(self):
        """
        Test should instantiate all requirements and inject them into the requested component.
        Requirements are identified by name.
        """
        self.container.register_type(SampleClass, "sample_class")
        self.container.register_type(InjectableComponent)
        self.container.setup()

        result: InjectableComponent = self.container.get_component(InjectableComponent)

        self.assertEqual(type(result.val), SampleClass)

    def test_should_inject_component_by_type(self):
        """
        Test should instantiate all requirements and inject them into the requested component.
        Requirements are identified by type.
        """
        self.container.register_type(SampleClass, "abc")
        self.container.register_type(InjectableComponent)
        self.container.setup()

        result: InjectableComponent = self.container.get_component(InjectableComponent)

        self.assertEqual(type(result.val), SampleClass)

    def test_should_inject_container(self):
        """
        Test should inject the container itself to the component.
        """
        self.container.register_type(InjectableContainer)
        self.container.setup()

        result: InjectableContainer = self.container.get_component(InjectableContainer)

        self.assertEqual(result.container, self.container)

    def test_should_fail_on_cyclic_reference(self):
        """
        Test should raise an exception due to cyclic reference (class A -> class B -> class C -> class A).
        """

        class A:

            def __init__(self, b):
                pass

        class B:

            def __init__(self, c):
                pass

        class C:

            def __init__(self, a):
                pass

        # Register 3 components that reference one another.
        self.container.register_types(A, B, C).setup()

        # Requesting a component that generates cyclic reference should raise an exception.
        with self.assertRaises(CyclicDependencyException):
            self.container.get_component(A)

    def test_should_fail_on_cyclic_reference_container_lookup(self):
        """
        Test should fail for a class that lookup itself in a container during initialization.
        """

        class A:

            def __init__(self, container: Container):
                # Looking up myself during initialization should generate cyclic reference.
                container.get_component('a')

        self.container.register_type(A).setup()

        # Requesting a component that generates cyclic reference should raise an exception.
        with self.assertRaises(CyclicDependencyException):
            self.container.get_component(A)
