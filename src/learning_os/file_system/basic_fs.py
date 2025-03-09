import os
import json
import math
import time
from typing import List, Dict, Tuple, Any
from learning_os.file_system.inode import DirectoryInode, RegularFileInode, Inode
from learning_os.file_system import FileSystem

DEFAULT_TOTAL_BLOCKS = 128
DEFAULT_BLOCK_SIZE = 10
DEFAULT_TOTAL_INODES = 16

class BasicFileSystem(FileSystem):
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

        if not os.path.exists(storage_path):
            self.__initialize_storage()

        self.storage = self.__read_storage()
        
        superblock = self.__get_superblock()

        self.block_size = superblock["block_size"]
        self.total_blocks = superblock["total_blocks"]
        self.max_inode_count = superblock["max_inode_count"]
        self.inode_bitmap_block = superblock["inode_bitmap_block"]
        self.data_bitmap_block = superblock["data_bitmap_block"]
        self.inode_start = superblock["inode_start"]
        self.data_start = superblock["data_start"]

    def __initialize_storage(self):
        """
        Initializes the storage with a superblock, inode bitmap, data bitmap, and an empty inode table. 
        This method will also creates the root directory inode as part of the initialisation process.
        """
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
            0: super_block,
            1: [False] * DEFAULT_TOTAL_INODES,
            2: [False] * DEFAULT_TOTAL_BLOCKS,
            3: {},
        }

        ## Creation of the root inode
        root_inode = DirectoryInode(0)
        storage_data[3]["0"] = root_inode.to_dict()
        storage_data[1][0] = True
        ## Creation of the root inode

        # Persist the storage data as JSON.
        with open(self.storage_path, "w") as storage:
            json.dump(storage_data, storage, indent=4)
            storage.flush()
            os.fsync(storage.fileno())
            
        print("Storage initialized and root directory (inode 0) created.")    

    def __read_storage(self) -> Dict[str, Any]:
        """
        Reads the storage from the JSON file and returns it as a dictionary.
        """
        with open(self.storage_path, "r") as storage:
            return json.load(storage)

    def __persist_storage(self) -> None:
        """
        Persists the current state of the storage to the JSON file.
        This method is called after every change made to the in-memory copy of the storage in order
        to sync the changes to the persistent storage.
        """
        with open(self.storage_path, "w") as storage:
            json.dump(self.storage, storage, indent=4)
            storage.flush()
            os.fsync(storage.fileno())

    def __get_inode_bitmap(self) -> List[bool]:
        """
        Retrieves the inode bitmap from the storage.
        
        The inode bitmap is a list of booleans where each index represents an inode.
        If the inode is allocated, the value is True; otherwise, it is False.
        """
        if str(self.inode_bitmap_block) not in self.storage:
            raise Exception(f"Inode bitmap (key {self.inode_bitmap_block}) not found in storage!")
        
        return self.storage[str(self.inode_bitmap_block)]

    def __allocate_inode_from_bitmap(self) -> int:
        """
        Allocates a free inode from the inode bitmap and marks it as used.

        Returns:
        int: The allocated inode number.

        Raises:
        Exception: If no free inodes are available.
        """
        inode_bitmap: List[bool] = self.__get_inode_bitmap()
        for i in range(self.max_inode_count):
            if not inode_bitmap[i]:
                inode_bitmap[i] = True
                return i
        raise Exception("No free inodes available!")
    
    def __deallocate_inode_to_bitmap(self, inode_num: int) -> None:
        """
        Deallocates an inode and marks it as free in the inode bitmap.

        Args:
        inode_num (int): The inode number to deallocate.

        Raises:
        Exception: If the inode number is invalid or if the inode is already free.
        """
        inode_bitmap: List[bool] = self.__get_inode_bitmap()
        if inode_num < 0 or inode_num >= len(inode_bitmap):
            raise Exception("Invalid inode number!")
        if not inode_bitmap[inode_num]:
            raise Exception("Inode is already free!")
        inode_bitmap[inode_num] = False
     
    def __get_superblock(self) -> Dict[str, Any]:
        """
        Retrieves the superblock from the storage.
        
        The superblock contains metadata about the filesystem, including block size,
        total blocks, inode bitmap block, data bitmap block, inode start, and data start.

        Returns:
        Dict[str, Any]: The superblock data.

        Raises:
        Exception: If the superblock is not found in the storage.
        """
        SUPERBLOCK = 0
        if str(SUPERBLOCK) not in self.storage:
            raise Exception("Superblock (key '0') not found in storage!")
        
        return self.storage[str(SUPERBLOCK)]
    
    def __get_data_bitmap(self) -> List[bool]:
        """
        Retrieves the data bitmap from the storage.
        
        The data bitmap is a list of booleans where each index represents a data block.
        If the block is allocated, the value is True; otherwise, it is False.
        
        Returns:
        List[bool]: The data bitmap.
        """
        if str(self.data_bitmap_block) not in self.storage:
            raise Exception(f"Data bitmap (key {self.data_bitmap_block}) not found in storage!")
        
        return self.storage[str(self.data_bitmap_block)]
    
    def __allocate_block_from_bitmap(self) -> int:
        """
        Allocates a free data block from the data bitmap and marks it as used.

        Returns:
        int: The allocated block number.

        Raises:
        Exception: If no free blocks are available.
        """
        data_bitmap: List[bool] = self.__get_data_bitmap()
        for i in range(self.total_blocks):
            if not data_bitmap[i]:
                data_bitmap[i] = True
                return i
        raise Exception("No free blocks available!")

    def __deallocate_block_to_bitmap(self, block_num: int) -> None:
        """
        Deallocates a block and marks it as free in the data bitmap. 

        Args:
        block_num (int): The block number to deallocate.

        Raises:
        Exception: If the block number is invalid or if the block is already free.
        """
        data_bitmap: List[bool] = self.__get_data_bitmap()
        if block_num < 0 or block_num >= len(data_bitmap):
            raise Exception("Invalid block number!")
        if not data_bitmap[block_num]:
            raise Exception("Block is already free!")
        data_bitmap[block_num] = False

    def __get_inode_table(self) -> Dict[str, Any]:
        """
        Retrieves the inode table from the storage.
        
        The inode table is a dictionary where the keys are inode numbers and the values are inode data.
        
        Returns:
        Dict[str, Any]: The inode table data.
        
        Raises:
        Exception: If the inode table is not found in the storage."""
        if str(self.inode_start) not in self.storage:
            raise Exception(f"Inode table (key f{self.inode_start}) not found in storage!")
        
        return self.storage[str(self.inode_start)]

    def __get_inode(self, path: List[str]) -> Inode:
        """
        Traverse the inode table to find the inode corresponding to the given path.

        Args:
        path (List[str]): The path to the inode.

        Returns:
        Inode: The inode object corresponding to the path.

        Raises:
        Exception: If the path is invalid or if the inode does not exist.
        """
        ROOT_BLOCK = 0
        inode_table = self.__get_inode_table()
        current_inode_num = ROOT_BLOCK
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

        return Inode.from_dict(current_inode)
    
    def __get_inode_by_number(self, inode_num: int) -> Inode:
        """
        Retrieve an inode by its number from the inode table.

        Args:
        inode_num (int): The inode number to retrieve.

        Returns:
        Inode: The inode object corresponding to the inode number.

        Raises:
        Exception: If the inode number is invalid or if the inode does not exist.
        """
        inode_table = self.__get_inode_table()
        inode_data = inode_table.get(str(inode_num))
        if inode_data is None:
            raise Exception(f"Inode {inode_num} not found in inode table!")
        return Inode.from_dict(inode_data)

    def __update_inode_table(self, inode: Inode) -> None:
        """
        Update the inode table with the given inode.

        Args:
        inode (Inode): The inode object to update.
        """
        inode_table = self.__get_inode_table()
        inode_table[str(inode.inode_number)] = inode.to_dict()

    def __delete_inode_from_table(self, inode_num: int) -> None:
        """
        Delete an inode from the inode table.

        Args:
        inode_num (int): The inode number to delete.

        Raises:
        Exception: If the inode number is invalid or if the inode does not exist.
        """
        inode_table = self.__get_inode_table()
        if str(inode_num) in inode_table:
            del inode_table[str(inode_num)]
        else:
            raise Exception(f"Inode {inode_num} not found in inode table!")

    @staticmethod
    def __parse_path(path: str) -> Tuple[List, str]:
        """
        Helper method to parse a given path into its components.
        
        Args:
        path (str): The path to parse.
        
        Returns:
        Tuple[List, str]: A tuple containing the parent directory and the new file's name.
        """
        if not path.startswith("/"):
            raise Exception("Path must be absolute and start with '/'")
        parts = path.strip("/").split("/")
        if not parts or parts[0] == "":
            raise Exception("Invalid path")
        
        parent_dir = parts[:-1]
        new_dir_name = parts[-1]
        return (parent_dir, new_dir_name)

    def __create_inode(self, path: str, inode_type: str) -> None:
        """
        Creates a new inode (directory or file) given an absolute path.
        If the parent directory doesn't exist, throw an exception.
        Otherwise, allocate a free inode, mark it in the bitmap,
        create the inode, add it to the inode table,
        update the parent directory's entries, and persist the changes.

        Args:
        path (str): The absolute path where the inode will be created.
        inode_type (str): The type of inode to create ("directory" or "file").

        Raises:
        Exception: If the parent directory doesn't exist or if the inode type is invalid.
        """
        parent_dir, new_name = self.__parse_path(path)
        parent_inode: Inode = self.__get_inode(parent_dir)
        
        assert isinstance(parent_inode, DirectoryInode), "Parent inode must be a directory"

        if new_name in parent_inode.entries:
            return

        # Create the new inode.
        free_inode_num = self.__allocate_inode_from_bitmap()
        if inode_type == "directory":
            new_inode = DirectoryInode(free_inode_num)
        elif inode_type == "file":
            new_inode = RegularFileInode(free_inode_num)
        else:
            raise Exception("Invalid inode type")

        self.__update_inode_table(new_inode)

        parent_inode.entries[new_name] = free_inode_num
        parent_inode.modified_at = time.time()

        self.__update_inode_table(parent_inode)

        self.__persist_storage()
        print(f"{inode_type.capitalize()} '{path}' created with inode {free_inode_num}.")

    def create_directory(self, path: str) -> None:
        """
        Creates a new directory given an absolute path.
        
        Args:
        path (str): The absolute path where the directory will be created.
        """
        self.__create_inode(path, "directory")

    def create_file(self, path: str) -> None:
        """
        Creates a new file given an absolute path.
        
        Args:
        path (str): The absolute path where the file will be created.
        """
        self.__create_inode(path, "file")

    def __delete_inode(self, path: str, inode_type: str) -> None:
        """
        Deletes an inode (directory or file) given an absolute path.
        If the inode doesn't exist, throw an exception.
        Otherwise, mark it as free in the bitmap,
        remove it from the inode table,
        update the parent directory's entries, and persist the changes.

        Args:
        path (str): The absolute path of the inode to delete.
        inode_type (str): The type of inode to delete ("directory" or "file").

        Raises:
        Exception: If the inode doesn't exist or if the inode type is invalid.
        """
        parent_dir, name = self.__parse_path(path)
        parent_inode: Inode = self.__get_inode(parent_dir)
        
        assert isinstance(parent_inode, DirectoryInode), "Parent inode must be a directory"
    
        if name not in parent_inode.entries:
            raise Exception(f"{inode_type.capitalize()} '{path}' does not exist!")
    
        # Delete the inode.
        inode_num = parent_inode.entries[name]
        inode_to_delete = self.__get_inode_by_number(inode_num)
    
        if inode_type == "directory":
            assert isinstance(inode_to_delete, DirectoryInode), "Inode type mismatch"
            if inode_to_delete.entries:
                raise Exception(f"Directory '{path}' is not empty and cannot be deleted!")
        elif inode_type == "file":
            assert isinstance(inode_to_delete, RegularFileInode), "Inode type mismatch"
            blocks = inode_to_delete.data.values()
            for block_num in blocks:
                self.__free_data_block(block_num)
                self.__deallocate_block_to_bitmap(block_num)
        else:
            raise Exception("Invalid inode type")
    
        # Remove the inode from the inode table.
        self.__delete_inode_from_table(inode_num)
        
        # Mark the inode as free in the bitmap.
        self.__deallocate_inode_to_bitmap(inode_num)
    
        # Remove from parent directory's entries.
        del parent_inode.entries[name]
        parent_inode.modified_at = time.time()
        self.__update_inode_table(parent_inode)
    
        self.__persist_storage()
        print(f"{inode_type.capitalize()} '{path}' deleted.")

    def delete_file(self, path: str) -> None:
        """
        Deletes a file given an absolute path.
        
        Args:
        path (str): The absolute path of the file to delete.
        """
        self.__delete_inode(path, "file")

    def delete_directory(self, path: str) -> None:
        """
        Deletes a directory given an absolute path.
        
        Args:
        path (str): The absolute path of the directory to delete.
        """
        self.__delete_inode(path, "directory")

    def __write_to_data_block(self, block_num: int, data: str) -> None:
        """
        Write data to a specific block number.

        Args:
        block_num (int): The block number to write to.
        data (str): The data to write.
        """
        superblock = self.__get_superblock()
        data_start = superblock["data_start"]
        self.storage[str(block_num + data_start)] = data

    def __read_from_data_block(self, block_num: int) -> str:
        """
        Read data from a specific block number.

        Args:
        block_num (int): The data block number to read from.

        Returns:
        str: The data read from the data block.
        """
        superblock = self.__get_superblock()
        data_start = superblock["data_start"]
        return self.storage.get(str(block_num + data_start), "")
    
    def __free_data_block(self, block_num: int) -> None:
        """
        Free a specific data block.

        Args:
        block_num (int): The data block number to free.
        """
        superblock = self.__get_superblock()
        data_start = superblock["data_start"]
        del self.storage[block_num + data_start]

    def write_file(self, file_path: str, data: str) -> None:
        """
        Write data to a file at the specified path.
        If the file doesn't exist, throw an exception.
        Otherwise, allocate blocks as needed and persist the changes.

        Args:
        file_path (str): The absolute path of the file to write to.
        data (str): The data to write to the file.

        Raises:
        Exception: If the file doesn't exist or if the inode type is invalid.
        """
        parent_dir, name = self.__parse_path(file_path)
        parent_inode = self.__get_inode(parent_dir)
        assert isinstance(parent_inode, DirectoryInode), "Parent inode must be a directory"
    
        if name not in parent_inode.entries:
            raise Exception(f"File '{file_path}' does not exist!")
    
        # Get the inode for the file.
        file_inode: Inode = self.__get_inode_by_number(parent_inode.entries[name])
        
        if not isinstance(file_inode, RegularFileInode):
            raise Exception(f"'{file_path}' is not a regular file!")
    
        # Allocate blocks for the data.
        total_blocks_needed = math.ceil(len(data) / self.block_size)
        blocks_to_allocate = []
    
        for _ in range(total_blocks_needed):
            block_num = self.__allocate_block_from_bitmap()
            blocks_to_allocate.append(block_num)
    
        # Write data to the allocated blocks.
        for i, block_num in enumerate(blocks_to_allocate):
            start = i * self.block_size
            end = start + self.block_size
            file_inode.data[block_num] = block_num
            data_chunk = data[start:end]
            self.__write_to_data_block(block_num, data_chunk)
    
        file_inode.size += len(data)
        file_inode.modified_at = time.time()
    
        # Update the inode table and persist changes.
        self.__update_inode_table(file_inode)
        self.__persist_storage()

    def read_file(self, file_path: str, offset: int, size: int) -> str:
        """
        Read data from a file at the specified path.
        If the file doesn't exist, throw an exception.
        Otherwise, read the data from the allocated blocks.

        Args:
        file_path (str): The absolute path of the file to read from.
        offset (int): The byte offset to start reading from.
        size (int): The number of bytes to read.

        Returns:
        str: The data read from the file.

        Raises:
        Exception: If the file doesn't exist or if the inode type is invalid.
        """
        parent_dir, name = self.__parse_path(file_path)
        parent_inode = self.__get_inode(parent_dir)
        
        assert isinstance(parent_inode, DirectoryInode), "Parent inode must be a directory"
    
        if name not in parent_inode.entries:
            raise Exception(f"File '{file_path}' does not exist!")
    
        # Get the inode for the file.
        file_inode: Inode = self.__get_inode_by_number(parent_inode.entries[name])
        
        if not isinstance(file_inode, RegularFileInode):
            raise Exception(f"'{file_path}' is not a regular file!")
    
        # Read data from the allocated blocks.
        data = ""
    
        for block_num in file_inode.data.values():
            block_data = self.__read_from_data_block(block_num)
            data += block_data
    
        result = data[offset:offset + size]
        print(f"Read {len(result)} bytes from '{file_path}' starting at offset {offset}. Result: {result}")
        return result
    
    def list_directory(self, path: str) -> List[str]:
        """
        List the contents of a directory at the specified path.
        If the directory doesn't exist, throw an exception.

        Args:
        path (str): The absolute path of the directory to list.

        Returns:
        List[str]: A list of entries in the directory.

        Raises:
        Exception: If the directory doesn't exist or if the inode type is invalid.
        """
        parent_dir, name = self.__parse_path(path)
        parent_inode = self.__get_inode(parent_dir)
        
        assert isinstance(parent_inode, DirectoryInode), "Parent inode must be a directory"
    
        if name not in parent_inode.entries:
            raise Exception(f"Directory '{path}' does not exist!")
    
        # Get the inode for the directory.
        dir_inode: Inode = self.__get_inode_by_number(parent_inode.entries[name])
        
        if not isinstance(dir_inode, DirectoryInode):
            raise Exception(f"'{path}' is not a directory!")
    
        directories = list(dir_inode.entries.keys())
        print(f"Contents of directory '{path}': {directories}")
        return directories