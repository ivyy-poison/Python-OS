from python_os.memory import PageTableEntry

class PageTable:
    def __init__(self):
        self.memory_size = 1024     # 1024 bytes
        self.page_size = 16         # 16 bytes
        self.num_pages = self.memory_size // self.page_size

        self.page_table = [PageTableEntry(i) for i in range(self.num_pages)]

    def get_page_table_entry(self, page_number: int) -> PageTableEntry:
        if page_number < 0 or page_number >= self.num_pages:
            raise ValueError("Invalid page number")
        return self.page_table[page_number]
    
    def set_page_table_entry(self, page_number: int, entry: PageTableEntry):
        if page_number < 0 or page_number >= self.num_pages:
            raise ValueError("Invalid page number")
        self.page_table[page_number] = entry