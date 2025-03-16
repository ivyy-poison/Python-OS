from python_os.process import Process
from python_os.memory import AllocationPolicy, MemoryManager
from typing import Any, Dict, Tuple

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
        assert size % MemoryManager.PAGE_SIZE == 0, f"Size allocated must be a multiple of {MemoryManager.PAGE_SIZE}."
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
    
    def retrieve(self, process: Process, virtual_address: int) -> Any:
        """
        Retrieve the value at the given virtual address for the specified process.
        """
        if process.pid not in self.process_to_segments:
            raise MemoryError("Process does not have allocated memory.")
        
        total_process_address_space = sum(
            bound - base for base, bound in self.process_to_segments[process.pid].values()
        )
        if virtual_address >= total_process_address_space:
            raise MemoryError("Virtual address is out of bounds.")
        
        ## Find the segment that contains the virtual address
        segment_size = total_process_address_space // 3
        segment_index = virtual_address // segment_size
        segment_name = ["code", "heap", "stack"][segment_index]

        base, _ = self.process_to_segments[process.pid][segment_name]
        offset = virtual_address % segment_size
        return self.memory.get(base + offset, None)