import os
import json
import time
from typing import List, Dict, Tuple, Any
from learning_os.file_system.inode import DirectoryInode, RegularFileInode

DEFAULT_TOTAL_BLOCKS = 128
DEFAULT_BLOCK_SIZE = 4096
DEFAULT_INODE_SIZE = 256
DEFAULT_TOTAL_INODES = 16

class BasicFileSystem:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

        if not os.path.exists(storage_path):
            self.__initialize_storage()

        self.storage = self.__read_storage()

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

    def __allocate_inode(self) -> int:
        """
        Allocates a free inode from the inode bitmap.
        Returns the inode number.
        """
        inode_bitmap: List[bool] = self.__get_inode_bitmap()
        for i in range(len(inode_bitmap)):
            if not inode_bitmap[i]:
                inode_bitmap[i] = True
                self.__persist_storage()
                return i
        raise Exception("No free inodes available!")
    
    def __read_storage(self) -> Dict[str, Any]:
        with open(self.storage_path, "r") as storage:
            return json.load(storage)
        
    def __get_superblock(self) -> Dict[str, Any]:
        if "0" not in self.storage:
            raise Exception("Superblock (key '0') not found in storage!")
        
        return self.storage["0"]
    
    def __get_inode_bitmap(self) -> List[bool]:
        if "1" not in self.storage:
            raise Exception("Inode bitmap (key '1') not found in storage!")
        
        return self.storage["1"]
    
    def __get_data_bitmap(self) -> List[bool]:
        if "2" not in self.storage:
            raise Exception("Data bitmap (key '2') not found in storage!")
        
        return self.storage["2"]
    
    def __get_inode_table(self) -> Dict[str, Any]:
        if "3" not in self.storage:
            raise Exception("Inode table (key '3') not found in storage!")
        
        return self.storage["3"]

    def __get_data_table(self) -> Dict[str, Any]:
        if "4" not in self.storage:
            raise Exception("Data table (key '4') not found in storage!")
        
        return self.storage["4"]

    def __persist_storage(self) -> None:
        with open(self.storage_path, "w") as storage:
            json.dump(self.storage, storage, indent=4)
            storage.flush()
            os.fsync(storage.fileno())

    @staticmethod
    def __parse_path(path: str) -> Tuple[List, str]:
        if not path.startswith("/"):
            raise Exception("Path must be absolute and start with '/'")
        parts = path.strip("/").split("/")
        if not parts or parts[0] == "":
            raise Exception("Invalid path")
        
        parent_dir = parts[:-1]
        new_dir_name = parts[-1]
        return (parent_dir, new_dir_name)

    def __get_inode(self, path: List[str]) -> int:
        """
        Traverse the inode table to find the inode corresponding to the given path.
        """
        inode_table = self.__get_inode_table()
        current_inode_num = 0
        current_inode = inode_table.get(str(current_inode_num))
        
        for part in path:
            if current_inode is None:
                raise Exception(f"Parent directory '{part}' does not exist!")
            entries = current_inode.get("entries", {})
            if part not in entries:
                raise Exception(f"Parent directory '{part}' does not exist!")
            current_inode_num = entries[part]
            current_inode = inode_table.get(str(current_inode_num))
            if current_inode is None:
                raise Exception(f"Inode {current_inode_num} not found in inode table!")
        return current_inode_num

    def create_directory(self, path: str) -> None:
        """
        Creates a new directory given an absolute path.
        If the parent directory doesn't exist, throw an exception.
        Otherwise, allocate a free inode, mark it in the bitmap,
        create a directory inode, add it to the inode table,
        update the parent directory's entries, and persist the changes.
        """
        parent_dir, new_dir_name = self.__parse_path(path)

        inode_table = self.__get_inode_table()

        parent_inode_num = self.__get_inode(parent_dir)

        # Check if new directory already exists in parent.
        parent_inode = inode_table.get(str(parent_inode_num))
        if new_dir_name in parent_inode.get("entries", {}):
            return

        # Find first available inode from the inode bitmap.
        free_inode_num = self.__allocate_inode()

        # Create the new directory inode.
        new_dir_inode = DirectoryInode(free_inode_num)
        inode_table[str(free_inode_num)] = new_dir_inode.to_dict()

        # Update parent's directory entries.
        parent_inode.setdefault("entries", {})[new_dir_name] = free_inode_num
        parent_inode["modified_at"] = time.time()

        # Persist changes back to storage.
        self.__persist_storage()
        print(f"Directory '{path}' created with inode {free_inode_num}.")

    def create_file(self, path: str) -> None:
        """
        Creates a new file given an absolute path.
        If the parent directory doesn't exist, throw an exception.
        Otherwise, allocate a free inode, mark it in the bitmap,
        create a regular file inode, add it to the inode table,
        update the parent directory's entries, and persist the changes.
        """
        parent_dir, new_file_name = self.__parse_path(path)

        # Read entire storage so we can update it.
        inode_table: Dict[str, Any] = self.__get_inode_table()

        # Find the parent directory inode.
        # If creating "/file", the parent is root (inode 0)
        parent_inode_num = self.__get_inode(parent_dir)

        # Check if new file already exists in parent.
        parent_inode = inode_table.get(str(parent_inode_num))
        if new_file_name in parent_inode.get("entries", {}):
            return

        # Find first available inode from the inode bitmap.
        free_inode_num = self.__allocate_inode()

        # Create the new file inode.
        new_file_inode = RegularFileInode(free_inode_num)

        inode_table[str(free_inode_num)] = new_file_inode.to_dict()
        # Update parent's directory entries.
        parent_inode.setdefault("entries", {})[new_file_name] = free_inode_num
        parent_inode["modified_at"] = time.time()

        # Persist changes back to storage.
        self.__persist_storage()
        print(f"File '{path}' created with inode {free_inode_num}.")