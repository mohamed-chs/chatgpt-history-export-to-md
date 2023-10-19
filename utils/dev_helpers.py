"""Helper functions for development."""

# pyright: reportGeneralTypeIssues=false
# pyright: reportInvalidTypeVarUse=false

from typing import Any, TypeVar

ClassT = TypeVar("ClassT", bound=type)


def track_instances(cls: ClassT) -> ClassT:
    """Decorate a class to track the number of instances created from it. Helps identify memory leaks."""

    cls.instance_count = 0

    original_init = cls.__init__

    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        """Modified initializer to track instance count."""
        original_init(self, *args, **kwargs)
        self.__class__.instance_count += 1

    cls.__init__ = new_init

    cls.__del__ = lambda self: print(
        f"\nInstance {id(self)} of {self.__class__.__name__} is being deleted."
    )

    return cls


def print_instance_count(cls: ClassT) -> None:
    """Print the instance count of a class."""
    count = getattr(cls, "instance_count", 0)
    print(f"{cls.__name__} has {count} instances.")
