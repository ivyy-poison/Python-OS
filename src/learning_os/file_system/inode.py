import abc
import time
from typing import Dict, Any

class Inode(abc.ABC):
    def __init__(self, inode_number: int, file_type: str):
        self.inode_number = inode_number
        self.file_type = file_type  # either "directory" or "file"
        self.created_at = time.time()
        self.modified_at = time.time()

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the inode metadata to a dictionary."""
        pass

class DirectoryInode(Inode):
    def __init__(self, inode_number: int):
        super().__init__(inode_number, "directory")
        # Mapping file/directory name -> inode number.
        self.entries: Dict[str, int] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inode_number": self.inode_number,
            "file_type": self.file_type,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "entries": self.entries,
        }

class RegularFileInode(Inode):
    def __init__(self, inode_number: int):
        super().__init__(inode_number, "file")
        self.data: str = ""  # for a simple implementation, storing file content as a string
        self.size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inode_number": self.inode_number,
            "file_type": self.file_type,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "data": self.data,
            "size": self.size,
        }