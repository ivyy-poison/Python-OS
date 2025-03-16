import math
import struct
import abc
from typing import Dict, List
from python_os.memory.heap_allocator.malloc import MallocAllocator

class BuddyAllocator(MallocAllocator):
    HEADER_SIZE = 8  # 8 bytes to store block size

    def __init__(self, total_memory: int):
        # For buddy allocation, total_memory is assumed to be a power of 2.
        self.total_memory = total_memory
        self.memory = bytearray(total_memory)
        # Free lists mapped by block size (must be power of 2).
        self.free_lists: Dict[int, List[int]] = {}
        self.free_lists[total_memory] = [0]

    def malloc(self, size: int) -> int:
        # Include header size in allocation; round up to next power of 2.
        request = size + BuddyAllocator.HEADER_SIZE
        block_size = self._next_power_of_two(request)

        # Search for the first available block of at least 'block_size'
        candidate_size = block_size
        found_addr = None
        while candidate_size <= self.total_memory:
            if candidate_size in self.free_lists and self.free_lists[candidate_size]:
                found_addr = self.free_lists[candidate_size].pop(0)
                break
            candidate_size *= 2
        if found_addr is None:
            raise MemoryError("Not enough memory for allocation.")

        # If our found block is larger than needed, split recursively.
        while candidate_size > block_size:
            candidate_size //= 2
            buddy_addr = found_addr + candidate_size
            if candidate_size not in self.free_lists:
                self.free_lists[candidate_size] = []
            self.free_lists[candidate_size].append(buddy_addr)
        # Write the header: store the allocated block size.
        self.memory[found_addr:found_addr + BuddyAllocator.HEADER_SIZE] = struct.pack("Q", block_size)
        # Return pointer offset to after the header.
        return found_addr + BuddyAllocator.HEADER_SIZE

    def free(self, pointer: int) -> None:
        # Get the address where the block header starts.
        block_start = pointer - BuddyAllocator.HEADER_SIZE
        header_bytes = self.memory[block_start:block_start + BuddyAllocator.HEADER_SIZE]
        (block_size,) = struct.unpack("Q", header_bytes)

        addr = block_start
        size = block_size

        # Buddy coalescing: try to merge with buddy blocks recursively.
        while True:
            buddy = self._buddy_of(addr, size)
            free_candidates = self.free_lists.get(size, [])
            if buddy in free_candidates:
                # Buddy found—remove from free_list and merge the blocks.
                free_candidates.remove(buddy)
                addr = min(addr, buddy)
                size *= 2
            else:
                break

        if size not in self.free_lists:
            self.free_lists[size] = []
        self.free_lists[size].append(addr)

    def _next_power_of_two(self, x: int) -> int:
        """Return the next power of two equal to or greater than x."""
        return 1 << (x - 1).bit_length()

    def _buddy_of(self, addr: int, size: int) -> int:
        """Return the buddy address of the block starting at addr with size."""
        return addr ^ size