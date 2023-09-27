from typing import List
from unittest import TestCase

from doze.di.container.dependency import Dependency, generate_dependency_list, DependencyType
from doze.ex import InvalidArgumentException


class TestRequirements(TestCase):
    """
    A collection of test cases for 'requirements' module.
    """

    def test_should_provide_empty_requirements_list(self):
        """
        Test should generate an empty requirements list for functions/methods without arguments.
        """

        class TestClass:

            def test_method(self):
                pass

        def test_func():
            pass

        empty_req_list: List[Dependency]

        # Testing synthetic class initializer.
        empty_req = generate_dependency_list(TestClass().__init__)
        self.assertTrue(len(empty_req) == 0)

        # Testing simple class method.
        empty_req = generate_dependency_list(TestClass().test_method)
        self.assertTrue(len(empty_req) == 0)

        # Testing straight forward function.
        empty_req = generate_dependency_list(test_func)
        self.assertTrue(len(empty_req) == 0)

    def test_should_fail_on_non_callable(self):
        """
        Test should fail when either a non-callable object is passed or if the callable is a class (a class with
        __call__ method).
        """

        class CallableClass:

            def __call__(self, *args, **kwargs):
                pass

        # Test an object which is not a callable.
        with self.assertRaises(InvalidArgumentException):
            # noinspection PyTypeChecker
            generate_dependency_list("this is not a callable !! It's a simple string !")

        # Test a callable class.
        with self.assertRaises(InvalidArgumentException):
            generate_dependency_list(CallableClass)

    def test_should_return_list_of_function_requirements(self):
        """
        Test should return list of function requirements.
        """

        def test_func(age: int, name: str):
            pass

        req: List[Dependency] = generate_dependency_list(test_func)

        self.assertEqual(req, [Dependency("age", int, DependencyType.SIMPLE),
                               Dependency("name", str, DependencyType.SIMPLE)])

    def test_should_exclude_reserved_arguments(self):
        """
        Test should ignore reserved arguments names, such as "self", "args", and "kwargs").
        """

        class TestClass:

            def test_method(self, name: str, *args, **kwargs):
                pass

        # The only requirement we expect to have is "name".
        req: List[Dependency] = generate_dependency_list(TestClass.test_method)
        self.assertEqual(req, [Dependency("name", str, DependencyType.SIMPLE)])
