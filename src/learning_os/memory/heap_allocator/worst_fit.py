import struct

from typing import Tuple, List
from learning_os.memory import XFitAllocator

class WorstFitAllocator(XFitAllocator):
    """
    Worst-fit memory allocator.
    """

    def malloc(self, size: int) -> int:
        total_size = size + XFitAllocator.HEADER_SIZE
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

        self.memory[alloc_start:alloc_start + XFitAllocator.HEADER_SIZE] = struct.pack("Q", total_size)

        if worst_fit_size == total_size:
            del self.free_list[worst_fit_index]
        else:
            self.free_list[worst_fit_index] = (alloc_end, worst_fit_size - total_size)

        return alloc_start + XFitAllocator.HEADER_SIZE