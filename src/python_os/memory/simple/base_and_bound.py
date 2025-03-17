from python_os.process import Process
from python_os.memory import SimpleAllocationPolicy, SimpleMemoryManager
from typing import Any, Dict, Tuple

class BaseAndBoundManager(SimpleMemoryManager):
    def __init__(self, total_memory: int, allocation_policy: SimpleAllocationPolicy):
        self.total_memory = total_memory
        self.allocation_policy = allocation_policy
        self.memory = {}
        self.process_to_base_and_bound: Dict[int, Tuple[int, int]] = {}  # {process_pid: (base, bound)}

    def allocate(self, process: Process, size: int) -> None:
        """
        Allocate a block of memory for the given process using the provided allocation policy.
        """
        assert size % SimpleMemoryManager.PAGE_SIZE == 0, f"Size allocated must be a multiple of {SimpleMemoryManager.PAGE_SIZE}."

        if process.pid in self.process_to_base_and_bound:
            raise MemoryError("Process already has allocated memory.")

        base = self.allocation_policy.allocate(size)
        bound = base + size
        self.process_to_base_and_bound[process.pid] = (base, bound)

    def deallocate(self, process: Process) -> None:
        """
        Deallocate the memory block for the given process using the provided allocation policy.
        """
        if process.pid not in self.process_to_base_and_bound:
            raise MemoryError("Process does not have allocated memory.")

        base, bound = self.process_to_base_and_bound[process.pid]
        size = bound - base
        self.allocation_policy.deallocate(base, size)
        del self.process_to_base_and_bound[process.pid]

    def get_memory_usage(self, process: Process) -> Any:
        """
        Get the current memory usage for the given process.
        """
        if process.pid not in self.process_to_base_and_bound:
            raise MemoryError("Process does not have allocated memory.")

        base, bound = self.process_to_base_and_bound[process.pid]
        return {
            "base": base,
            "bound": bound,
            "size": bound - base
        }
    
    def retrieve(self, process: Process, virtual_address: int) -> Any:
        """
        Retrieve the value at the given virtual address for the specified process.
        """
        if process.pid not in self.process_to_base_and_bound:
            raise MemoryError("Process does not have allocated memory.")

        base, bound = self.process_to_base_and_bound[process.pid]
        size = bound - base

        if virtual_address >= size:
            raise MemoryError("Virtual address is out of bounds.")

        return self.memory.get(base + virtual_address, None)