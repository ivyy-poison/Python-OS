import struct

from typing import Tuple, List
from learning_os.memory import XFitAllocator

class FirstFitAllocator(XFitAllocator):
    """
    First-fit memory allocator.
    """

    def malloc(self, size: int) -> int:
        total_size = size + XFitAllocator.HEADER_SIZE

        for index, (free_start, free_size) in enumerate(self.free_list):
            if free_size >= total_size:
                alloc_start = free_start
                alloc_end = free_start + total_size

                # Write the block header (store total_size as an 8-byte value)
                self.memory[alloc_start:alloc_start + XFitAllocator.HEADER_SIZE] = struct.pack("Q", total_size)

                # Update free list: if block exactly fits, remove it; otherwise update its start and size.
                if free_size == total_size:
                    del self.free_list[index]
                else:
                    self.free_list[index] = (alloc_end, free_size - total_size)

                return alloc_start + XFitAllocator.HEADER_SIZE

        raise MemoryError("Not enough contiguous memory available.")