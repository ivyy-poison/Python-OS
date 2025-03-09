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

    @classmethod
    @abc.abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> "Inode":
        """Load the inode metadata from a dictionary."""
        file_type = data.get("file_type")
        if file_type == "directory":
            return DirectoryInode.from_dict(data)    
        elif file_type == "file":
            return RegularFileInode.from_dict(data)
    
        raise ValueError(f"Unknown file type: {file_type}")

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
    
    @classmethod
    def from_dict(self, data: Dict[str, Any]) -> "DirectoryInode":
        """Load the inode metadata from a dictionary."""
        inode = DirectoryInode(inode_number=data["inode_number"])
        inode.file_type = data["file_type"]
        inode.created_at = data["created_at"]
        inode.modified_at = data["modified_at"]
        inode.entries = data["entries"]
        return inode

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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RegularFileInode":
        """Load the inode metadata from a dictionary."""
        inode = RegularFileInode(inode_number=data["inode_number"])
        inode.file_type = data["file_type"]
        inode.created_at = data["created_at"]
        inode.modified_at = data["modified_at"]
        inode.data = data["data"]
        inode.size = data["size"]

        return inode