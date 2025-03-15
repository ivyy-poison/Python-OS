import abc

class MallocAllocator(abc.ABC):
    """
    Abstract base class for memory allocation policies.
    """

    @abc.abstractmethod
    def allocate(self, size: int) -> int:
        """
        Allocate a block of memory of the given size.
        Returns the starting address of the allocated memory.
        """
        pass

    @abc.abstractmethod
    def deallocate(self, start: int, size: int) -> None:
        """
        Deallocate a block of memory starting at the given address.
        """
        pass