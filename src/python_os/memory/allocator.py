from python_os.process import Process
from python_os.memory import AllocationPolicy
from typing import Any, Dict, Tuple

import abc

class MemoryManager(abc.ABC):
    """
    Abstract base class for memory management strategies.
    """

    @abc.abstractmethod
    def allocate(self, process: Process, size: int) -> None:

        pass

    @abc.abstractmethod
    def deallocate(self, process: Process) -> None:

        pass

    @abc.abstractmethod
    def get_memory_usage(process: Process) -> Any:

        pass

PAGE_SIZE = 4

class BaseAndBoundManager(MemoryManager):
    def __init__(self, total_memory: int, allocation_policy: AllocationPolicy):
        self.total_memory = total_memory
        self.allocation_policy = allocation_policy
        self.memory = {}
        self.process_to_base_and_bound: Dict[int, Tuple[int, int]] = {}  # {process_pid: (base, bound)}

    def allocate(self, process: Process, size: int) -> None:
        """
        Allocate a block of memory for the given process using the provided allocation policy.
        """
        assert size % PAGE_SIZE == 0, f"Size allocated must be a multiple of {PAGE_SIZE}."

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

class SegmentedManager(MemoryManager):
    def __init__(self, total_memory: int, allocation_policy: AllocationPolicy):
        self.total_memory = total_memory
        self.allocation_policy = allocation_policy
        self.memory = {}
        self.process_to_segments: Dict[int, Dict[str, Tuple[int, int]]] = {} ## {process_pid: {segment_name: (base, size)}} 

    def allocate(self, process: Process, size: int) -> None:
        """
        Allocate a segment of memory for the given process.
        """

        ## Assume a model of a process having three segments: Code, heap, and stack.
        ## Also assume that the segments are of equal size.
        assert size % PAGE_SIZE == 0, f"Size allocated must be a multiple of {PAGE_SIZE}."
        assert size % 3 == 0, f"Size allocated must be a multiple of 3."

        if process.pid not in self.process_to_segments:
            self.process_to_segments[process.pid] = {}
        
        # ## Find free blocks
        for segment in ("code", "heap", "stack"):
            size_to_allocate = size // 3
            base = self.allocation_policy.allocate(size_to_allocate)
            bound = base + size_to_allocate

            self.process_to_segments[process.pid][segment] = (base, bound)
    
    def deallocate(self, process: Process) -> None:
        """
        Deallocate the segment of memory for the given process.
        """
        if process.pid not in self.process_to_segments:
            raise MemoryError("Segment does not exist for this process.")
        
        for segment_name, (base, bound) in self.process_to_segments[process.pid].items():
            size = bound - base
            self.allocation_policy.deallocate(base, size)
            ## Remove the segment from the allocation map
            del self.process_to_segments[process.pid][segment_name]
        
        if not self.process_to_segments[process.pid]:
            del self.process_to_segments[process.pid]

    def get_memory_usage(self, process: Process) -> Any:
        """
        Get the current memory usage for the given process.
        """
        if process.pid not in self.process_to_segments:
            raise MemoryError("Process does not have allocated memory.")
        
        return {
            segment_name: {
                "base": base,
                "size": size
            }
            for segment_name, (base, size) in self.process_to_segments[process.pid].items()
        }