class PageTableEntry:
    def __init__(self, page_number: int):
        self.page_number = page_number
        self.frame_number: int | None = None
        self.valid = False                      # Whether the page is valid
        self.dirty = False                      # Whether the page has been modified   
        self.present = False                    # Whether the page is present in memory
        self.write_allowed = False              # Whether the page is writable
        self.user_mode_allowed = False          # Whether the page is accessible in user mode

        ## Future: Few other bits to explore involve how they are stored in cache ##
