from abc import ABC, abstractmethod


class ClassTypeToNameResolutionStrategy(ABC):

    @abstractmethod
    def to_component_name(self, class_type: type) -> str:
        pass


class PascalToCamelCaseClassTypeResolverStrategy(ClassTypeToNameResolutionStrategy):
    """
    Following PEP-8 guidelines, this strategy converts a class type name (provided in Pascal case)
    to a component name, which is snake case, e.g.: ClassName -> class_name.
    """

    def to_component_name(self, class_type: type) -> str:
        """
        Converts a class type to component name.
        :param class_type: Class type, assumed to be in Pascal case.
        :return: Component name in snake-case.
        """
        class_name: str = class_type.__name__
        component_name: str = ""
        for ch in class_name:
            if ch.isupper():
                if len(component_name) > 0:
                    component_name += "_"
                ch = ch.lower()
            component_name += ch

        return component_name
