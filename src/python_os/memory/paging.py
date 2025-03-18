from typing import Any, Optional
from python_os.memory import PageTable, PageTableEntry
from python_os.process import Process
from python_os.memory.paging import PagingManager, Frame
from python_os.process import Process

class Disk:
    def __init__(self):
        self.pages = {}
    
    def read_page(self, pid: int, page_number: int, page_size: int) -> bytes:
        """
        Simulate reading a page from disk.
        Returns a bytes object of length page_size.
        """
        key = (pid, page_number)

        if key not in self.pages:
            self.pages[key] = b'\x00' * page_size
        return self.pages[key]
    
    def write_page(self, pid: int, page_number: int, data: bytes) -> None:
        """
        Simulate writing a page to disk.
        """
        self.pages[(pid, page_number)] = data
class PageFaultHandler:
    def __init__(self, disk: Disk):
        self.disk = disk

    def handle_page_fault(self, process: Process, virtual_address: int, manager: PagingManager) -> Frame:
        """
        Handles page faults by allocating a RAM frame,
        reading the required page from disk, and populating the frame.
        Returns the allocated Frame.
        """
        # Allocate a free frame for the process.
        frame = manager.ram.allocate_page(process.pid)
        
        # Compute the page number from the virtual address.
        page_number = virtual_address // PagingManager.PAGE_SIZE
        
        # Simulate reading from disk (the Disk class knows the page_size)
        data = self.disk.read_page(process.pid, page_number, manager.ram.FRAME_SIZE)
        
        # Ensure that the data exactly fills the frame:
        if len(data) < manager.ram.FRAME_SIZE:
            data = data.ljust(manager.ram.FRAME_SIZE, b'\x00')
        frame.data[:] = data[:manager.ram.FRAME_SIZE]
        return frame

class PagingManager:
    PAGE_SIZE = 4

    def __init__(self, total_memory: int):
        self.total_memory = total_memory
        self.ram = Ram(size=1024)
        # Instantiate a Disk simulation and the dedicated page fault handler.
        self.disk = Disk()
        self.page_fault_handler = PageFaultHandler(self.disk)

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
            new_frame = self.page_fault_handler.handle_page_fault(process, virtual_address, self)
            page_table_entry.frame_number = new_frame.frame_number
            page_table_entry.is_present = True

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