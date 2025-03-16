import abc

class AllocationPolicy(abc.ABC):
    """
    Abstract base class for memory allocation policies.
    """

    @abc.abstractmethod
    def allocate(self, size: int) -> int:

        pass

    @abc.abstractmethod
    def deallocate(self, start: int, size: int) -> None:

        pass

PAGE_SIZE = 4

class FirstFit(AllocationPolicy):
    def __init__(self, total_memory: int, page_size: int = PAGE_SIZE):
        self.page_size = page_size
        self.total_memory = total_memory
        self.total_blocks = total_memory // page_size
        self.blocks_bitmap = [False] * self.total_blocks

    def allocate(self, size: int) -> int:
        """
        Allocate contiguous blocks for the given size using the first-fit strategy.
        Returns the starting base address of allocated memory.
        """
        if size % self.page_size != 0:
            raise ValueError(f"Size must be a multiple of page size ({self.page_size}).")
        num_blocks_needed = size // self.page_size

        start_block = None
        for i in range(self.total_blocks):
            if not self.blocks_bitmap[i]:
                if start_block is None:
                    start_block = i
                if i - start_block + 1 == num_blocks_needed:
                    # Found enough contiguous blocks. Mark them as allocated:
                    for j in range(start_block, start_block + num_blocks_needed):
                        self.blocks_bitmap[j] = True
                    base = start_block * self.page_size
                    return base
            else:
                start_block = None

        if start_block is None or (i - start_block + 1) < num_blocks_needed:
            raise MemoryError("Not enough contiguous memory blocks available.")
        

    def deallocate(self, start: int, size: int) -> None:
        """
        Deallocate contiguous blocks starting at the given base address.
        """
        if start % self.page_size != 0:
            raise ValueError(f"Start address must be a multiple of page size ({self.page_size}).")
        if size % self.page_size != 0:
            raise ValueError(f"Size must be a multiple of page size ({self.page_size}).")
        
        start_block = start // self.page_size
        num_blocks = size // self.page_size

        if start_block < 0 or start_block + num_blocks > self.total_blocks:
            raise ValueError("Address range out of bounds.")

        for i in range(start_block, start_block + num_blocks):
            self.blocks_bitmap[i] = False
