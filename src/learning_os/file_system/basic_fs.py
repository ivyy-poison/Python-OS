import abc
import os
import json
import ijson
import time
from typing import List, Dict, Any

DEFAULT_TOTAL_BLOCKS = 128
DEFAULT_BLOCK_SIZE = 4096
DEFAULT_INODE_SIZE = 256
DEFAULT_TOTAL_INODES = 16

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


class BasicFileSystem:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

        if not os.path.exists(storage_path):
            self.__initialize_storage()

        self.superblock = self.__load_superblock()

    def __initialize_storage(self):
        super_block = {
            "block_size": DEFAULT_BLOCK_SIZE,
            "total_blocks": DEFAULT_TOTAL_BLOCKS,
            "max_inode_count": DEFAULT_TOTAL_INODES,
            "inode_bitmap_block": 1,
            "data_bitmap_block": 2,
            "inode_start": 3,
            "data_start": 4
        }

        storage_data = {
            "0": super_block,
            "1": [False] * DEFAULT_TOTAL_INODES,
            "2": [False] * DEFAULT_TOTAL_BLOCKS,
            "3": {},
            "4": {}
        }

        root_inode = DirectoryInode(0)
        # Store root inode in inode table (as key "0")
        storage_data["3"]["0"] = root_inode.to_dict()
        # Mark inode 0 as used
        storage_data["1"][0] = True

        # Persist the storage data as JSON.
        with open(self.storage_path, "w") as storage:
            json.dump(storage_data, storage, indent=4)
            storage.flush()
            os.fsync(storage.fileno())
            
        print("Storage initialized and root directory (inode 0) created.")

        with open(self.storage_path, "w") as storage:
            json.dump(storage_data, storage, indent=4)
            storage.flush()
            os.fsync(storage.fileno())

    def __load_superblock(self):
        with open(self.storage_path, "r") as storage:
            try:
                superblock_gen = ijson.items(storage, "0")
                superblock = next(superblock_gen)
                return superblock
            except StopIteration:
                raise Exception("Superblock (key '0') not found in storage!")
            
    def __load_inode_bitmap(self) -> List[bool]:
        with open(self.storage_path, "r") as storage:
            try:
                inode_bitmap_gen = ijson.items(storage, "1")
                inode_bitmap = next(inode_bitmap_gen)
                return inode_bitmap
            except StopIteration:
                raise Exception("Inode bitmap (key '1') not found in storage!")
        
    def __load_data_bitmap(self) -> List[bool]:
        with open(self.storage_path, "r") as storage:
            try:
                data_bitmap_gen = ijson.items(storage, "2")
                data_bitmap = next(data_bitmap_gen)
                return data_bitmap
            except StopIteration:
                raise Exception("Data bitmap (key '2') not found in storage!")
            
    
    def __read_storage(self) -> Dict[str, Any]:
        with open(self.storage_path, "r") as storage:
            return json.load(storage)

    def __persist_storage(self, storage_data: Dict[str, Any]) -> None:
        with open(self.storage_path, "w") as storage:
            json.dump(storage_data, storage, indent=4)
            storage.flush()
            os.fsync(storage.fileno())

    def __get_inode_table(self) -> Dict[str, Any]:
        storage_data = self.__read_storage()
        # If block "3" (inode table) isn't present, create it.
        if "3" not in storage_data:
            storage_data["3"] = {}
            self.__persist_storage(storage_data)
        return storage_data["3"]


    def create_directory(self, path: str) -> None:
        """
        Creates a new directory given an absolute path.
        If the parent directory doesn't exist, throw an exception.
        Otherwise, allocate a free inode, mark it in the bitmap,
        create a directory inode, add it to the inode table,
        update the parent directory's entries, and persist the changes.
        """
        # For simplicity, assume paths are like "/dir" or "/parent/child"
        if not path.startswith("/"):
            raise Exception("Path must be absolute and start with '/'")
        parts = path.strip("/").split("/")
        if not parts or parts[0] == "":
            raise Exception("Invalid path")

        # Read entire storage so we can update it.
        storage_data = self.__read_storage()
        inode_table: Dict[str, Any] = storage_data.get("3", {})

        # Find the parent directory inode.
        # If creating "/dir", the parent is root (inode 0)
        if len(parts) == 1:
            parent_inode_num = 0
            new_dir_name = parts[0]
        else:
            new_dir_name = parts[-1]
            # Traverse path parts to find parent's inode number.
            current_inode = inode_table.get("0")
            if current_inode is None:
                raise Exception("Root directory not found in inode table!")
            parent_inode_num = 0
            for part in parts[:-1]:
                # current_inode should be a directory.
                if current_inode["file_type"] != "directory":
                    raise Exception(f"Inode {parent_inode_num} is not a directory!")
                entries = current_inode.get("entries", {})
                if part not in entries:
                    raise Exception(f"Parent directory '{part}' does not exist!")
                parent_inode_num = entries[part]
                current_inode = inode_table.get(str(parent_inode_num))
                if current_inode is None:
                    raise Exception(f"Inode {parent_inode_num} not found in inode table!")

        # Check if new directory already exists in parent.
        parent_inode = inode_table.get(str(parent_inode_num))
        if new_dir_name in parent_inode.get("entries", {}):
            raise Exception(f"Directory '{new_dir_name}' already exists!")

        # Find first available inode from the inode bitmap.
        inode_bitmap: List[bool] = storage_data["1"]
        free_inode_num = None
        for i in range(len(inode_bitmap)):
            if not inode_bitmap[i]:
                free_inode_num = i
                break
        if free_inode_num is None:
            raise Exception("No free inodes available!")

        # Mark inode as used.
        inode_bitmap[free_inode_num] = True

        # Create the new directory inode.
        new_dir_inode = DirectoryInode(free_inode_num)
        inode_table[str(free_inode_num)] = new_dir_inode.to_dict()

        # Update parent's directory entries.
        parent_inode.setdefault("entries", {})[new_dir_name] = free_inode_num
        parent_inode["modified_at"] = time.time()

        # Persist changes back to storage.
        storage_data["1"] = inode_bitmap  # update bitmap
        storage_data["3"] = inode_table     # update inode table

        self.__persist_storage(storage_data)
        print(f"Directory '{path}' created with inode {free_inode_num}.")
        
    

def main():
    fs = BasicFileSystem("storage.json")
    fs.create_directory("/dir1")
    fs.create_directory("/dir1/dir2")
    fs.create_directory("/dir2")

if __name__ == "__main__":
    main()