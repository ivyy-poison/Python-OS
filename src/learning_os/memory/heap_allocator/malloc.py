import abc
import struct

from typing import Tuple, List

class MallocAllocator(abc.ABC):
    """
    Abstract base class for memory allocation policies.
    """

    @abc.abstractmethod
    def malloc(self, size: int) -> int:
        """
        Allocate a block of memory of the given size.
        Returns the starting address of the allocated memory.
        """
        pass

    @abc.abstractmethod
    def free(self, pointer: int) -> None:
        """
        Deallocate a block of memory starting at the given address.
        """
        pass

class XFitAllocator(MallocAllocator):

    HEADER_SIZE = 8

    def __init__(self, total_memory: int):
        self.total_available_memory = total_memory
        self.memory = bytearray(total_memory)
        self.free_list: List[Tuple[int, int]] = [(0, total_memory)]  

    def free(self, pointer: int) -> None:
        block_start = pointer - XFitAllocator.HEADER_SIZE

        total_size_bytes = self.memory[block_start:block_start + XFitAllocator.HEADER_SIZE]
        (total_size,) = struct.unpack("Q", total_size_bytes)

        # Create a free block tuple for the deallocated region
        freed_block = (block_start, total_size)
        self.free_list.append(freed_block)

        # Coalesce free list: sort the free list by start address and merge contiguous blocks.
        self.free_list.sort(key=lambda x: x[0])
        coalesced = []
        current_start, current_size = self.free_list[0]
        for next_start, next_size in self.free_list[1:]:
            if current_start + current_size == next_start:
                current_size += next_size
            else:
                coalesced.append((current_start, current_size))
                current_start, current_size = next_start, next_size
        coalesced.append((current_start, current_size))
        self.free_list = coalesced
    