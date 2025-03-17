from typing import Any, Dict, Optional
from python_os.memory import MemoryManager, PageTable, PageTableEntry
from python_os.process import Process

class PagingManager:
    PAGE_SIZE = 4

    def __init__(self, total_memory: int):
        self.total_memory = total_memory
        self.ram = Ram(size=1024)

    def retrieve(self, process: Process, virtual_address: int) -> Any:
        """
        Retrieve the value at the given virtual address for the specified process.
        """        
        process_page_table: PageTable = process.page_table

        page_number = virtual_address // PagingManager.PAGE_SIZE
        offset = virtual_address % PagingManager.PAGE_SIZE

        page_table_entry: PageTableEntry = process_page_table.get_page_table_entry(page_number)
        
        if not page_table_entry.is_valid:
            raise MemoryError("Page is not valid.")
        
        if not page_table_entry.is_present:
            new_frame_num = self.ram.allocate_page(process.pid)
            ## TODO: Simulate reading from the disk
            page_table_entry.frame_number = new_frame_num

        frame_number = page_table_entry.frame_number
        return self.ram.get(frame_number)
    
class Frame:
    def __init__(self, frame_number: int):
        self.frame_number = frame_number
        self.size = Ram.FRAME_SIZE
        self.data: bytearray = bytearray(self.size)
        self.current_pid: Optional[int] = None

class Ram:
    FRAME_SIZE = 4

    def __init__(self, size: int):
        self.size = size
        self.num_frames = size // Ram.FRAME_SIZE
        self.frames = [Frame(i) for i in range(self.num_frames)]

    def allocate_free_frame(self) -> Optional[Frame]:
        """
        Allocate a free frame in RAM.
        """
        for frame in self.frames:
            if frame.current_pid is None:
                return frame
        return None
        
    def allocate_page(self, pid: int) -> Frame:
        """
        Allocate a page in RAM using the specified allocation policy.
        """
        frame = self.allocate_free_frame()
        if frame is None:
            raise MemoryError("No available frames.")
        assert frame.current_pid is None, "Frame is already allocated."
        frame.current_pid = pid
        return frame
    
    def get(self, frame_number: int) -> Any:
        """
        Retrieve the value from the specified frame.
        """
        if frame_number < 0 or frame_number >= self.num_frames:
            raise ValueError("Invalid frame number.")
        
        return self.frames[frame_number].data
    


