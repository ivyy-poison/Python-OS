import struct

from typing import Tuple, List
from learning_os.memory import XFitAllocator

class BestFitAllocator(XFitAllocator):
    """
    Best-fit memory allocator.
    """

    def malloc(self, size: int) -> int:
        total_size = size + XFitAllocator.HEADER_SIZE
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
        self.memory[alloc_start:alloc_start + XFitAllocator.HEADER_SIZE] = struct.pack("Q", total_size)

        # Update free list: if block exactly fits, remove it; otherwise update its start and size.
        if best_fit_size == total_size:
            del self.free_list[best_fit_index]
        else:
            self.free_list[best_fit_index] = (alloc_end, best_fit_size - total_size)

        return alloc_start + XFitAllocator.HEADER_SIZE