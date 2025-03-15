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
        block_start = pointer - FirstFitAllocator.HEADER_SIZE

        total_size_bytes = self.memory[block_start:block_start + FirstFitAllocator.HEADER_SIZE]
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

class FirstFitAllocator(XFitAllocator):
    """
    First-fit memory allocator.
    """

    def malloc(self, size: int) -> int:
        total_size = size + FirstFitAllocator.HEADER_SIZE

        for index, (free_start, free_size) in enumerate(self.free_list):
            if free_size >= total_size:
                alloc_start = free_start
                alloc_end = free_start + total_size

                # Write the block header (store total_size as an 8-byte value)
                self.memory[alloc_start:alloc_start + FirstFitAllocator.HEADER_SIZE] = struct.pack("Q", total_size)

                # Update free list: if block exactly fits, remove it; otherwise update its start and size.
                if free_size == total_size:
                    del self.free_list[index]
                else:
                    self.free_list[index] = (alloc_end, free_size - total_size)

                return alloc_start + FirstFitAllocator.HEADER_SIZE

        raise MemoryError("Not enough contiguous memory available.")
    
class BestFitAllocator(XFitAllocator):
    """
    Best-fit memory allocator.
    """

    def malloc(self, size: int) -> int:
        total_size = size + FirstFitAllocator.HEADER_SIZE
        best_fit_index = -1
        best_fit_size = float('inf')

        # Find the best fit block
        for index, (_, free_size) in enumerate(self.free_list):
            if free_size >= total_size and free_size < best_fit_size:
                best_fit_index = index
                best_fit_size = free_size

        if best_fit_index == -1:
            raise MemoryError("Not enough contiguous memory available.")

        alloc_start, _ = self.free_list[best_fit_index]
        alloc_end = alloc_start + total_size

        # Write the block header (store total_size as an 8-byte value)
        self.memory[alloc_start:alloc_start + FirstFitAllocator.HEADER_SIZE] = struct.pack("Q", total_size)

        # Update free list: if block exactly fits, remove it; otherwise update its start and size.
        if best_fit_size == total_size:
            del self.free_list[best_fit_index]
        else:
            self.free_list[best_fit_index] = (alloc_end, best_fit_size - total_size)

        return alloc_start + FirstFitAllocator.HEADER_SIZE
    
class WorstFitAllocator(XFitAllocator):
    """
    Worst-fit memory allocator.
    """

    def malloc(self, size: int) -> int:
        total_size = size + FirstFitAllocator.HEADER_SIZE
        worst_fit_index = -1
        worst_fit_size = -1

        # Find the worst fit block
        for index, (_, free_size) in enumerate(self.free_list):
            if free_size >= total_size and free_size > worst_fit_size:
                worst_fit_index = index
                worst_fit_size = free_size

        if worst_fit_index == -1:
            raise MemoryError("Not enough contiguous memory available.")

        alloc_start, _ = self.free_list[worst_fit_index]
        alloc_end = alloc_start + total_size

        self.memory[alloc_start:alloc_start + FirstFitAllocator.HEADER_SIZE] = struct.pack("Q", total_size)

        if worst_fit_size == total_size:
            del self.free_list[worst_fit_index]
        else:
            self.free_list[worst_fit_index] = (alloc_end, worst_fit_size - total_size)

        return alloc_start + FirstFitAllocator.HEADER_SIZE