from .simple.allocation_policy import AllocationPolicy as SimpleAllocationPolicy
from .simple.allocator import MemoryManager as SimpleMemoryManager
from .dynamic_allocation import (
    FirstFitAllocator,
    BestFitAllocator,
    WorstFitAllocator,
    XFitAllocator,
    MallocAllocator,
    BuddyAllocator
)

from .page_table_entry import PageTableEntry
from .page_table import PageTable