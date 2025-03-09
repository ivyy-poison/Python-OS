import abc
import json
import math
import os
from typing import List

class FileSystem(abc.ABC):
    """
    Abstract interface for a simulated file system.
    """

    @abc.abstractmethod
    def create_file(self, path: str) -> None:
        """
        Create a new file in the file system.

        Args:
            path (str): The path of the file to create.
        """
        pass

    @abc.abstractmethod
    def delete_file(self, path: str) -> None:
        """
        Delete a file from the file system.

        Args:
            path (str): The path of the file to delete.
        """
        pass

    @abc.abstractmethod
    def read_file(self, path: str, offset: int, size: int) -> bytes:
        """
        Read data from a file starting at the specified offset.

        Args:
            path (str): The file path.
            offset (int): The byte offset to start reading from.
            size (int): Number of bytes to read.

        Returns:
            bytes: The data read from the file.
        """
        pass

    @abc.abstractmethod
    def write_file(self, path: str, data: bytes, offset: int) -> None:
        """
        Write bytes to a file starting at the specified offset.
        May trigger block allocations or update write-ahead logs depending on the implementation.

        Args:
            path (str): The file path.
            data (bytes): The data to write.
            offset (int): The starting byte offset for the write.
        """
        pass

    @abc.abstractmethod
    def list_directory(self, path: str) -> List[str]:
        """
        List all files and directories inside a given directory.

        Args:
            path (str): The directory whose contents will be listed.

        Returns:
            List[str]: A list of file and directory names.
        """
        pass

    @abc.abstractmethod
    def open_file(self, path: str, mode: str) -> None:
        """
        Open a file with a given mode (e.g., 'r' for read, 'w' for write, etc.).
        This can be used to track open handles or set file-specific state.

        Args:
            path (str): The file path.
            mode (str): Mode in which to open the file.
        """
        pass

    @abc.abstractmethod
    def close_file(self, path: str) -> None:
        """
        Close an open file, releasing any resources or locks.

        Args:
            path (str): The file path.
        """
        pass
    

# class BasicFileSystem():
#     def __init__(self, disk_path: str) -> None:
#         self.disk_path = disk_path

#         if not os.path.exists(disk_path):
#             self.__initialise_disk()
        
#         self.__load_disk()
#         inode_bitmap = self.__load_inode_bitmap()
#         print(inode_bitmap)

#     def __initialise_disk(self) -> None:
#         with open(self.disk_path, 'wb') as disk:
#             disk.write(b'\0' * (DEFAULT_TOTAL_BLOCKS * DEFAULT_BLOCK_SIZE))
#             disk.flush()
#             os.fsync(disk.fileno())

#         super_block = {
#             "block_size": DEFAULT_BLOCK_SIZE,
#             "total_blocks": DEFAULT_TOTAL_BLOCKS,
#             "max_inode_count": DEFAULT_TOTAL_INODES,
#             "inode_bitmap_block": 1,
#             "data_bitmap_block": 2,
#             "inode_start": 4,
#             "data_start": 8
#         }

#         data = json.dumps(super_block).encode("utf-8")
#         # Pad with null bytes so that the total is exactly DEFAULT_BLOCK_SIZE bytes
#         if len(data) < DEFAULT_BLOCK_SIZE:
#             data += b'\0' * (DEFAULT_BLOCK_SIZE - len(data))
        
#         with open("disk.img", "r+b") as disk:
#             disk.seek(0)
#             disk.write(data)
#             disk.flush()
#             os.fsync(disk.fileno())
        
#          # Create an inode bitmap:
#         # Calculate number of bytes needed to represent DEFAULT_INODE_COUNT bits.
#         inode_bitmap_bytes = math.ceil( DEFAULT_TOTAL_INODES / 8)
#         inode_bitmap = bytearray(inode_bitmap_bytes)  # all bits 0 (free)
#         # Pad to fill a block.
#         inode_bitmap += b'\0' * (DEFAULT_BLOCK_SIZE - len(inode_bitmap))
#         inode_bitmap_offset = DEFAULT_BLOCK_SIZE * super_block["inode_bitmap_block"]
#         with open(self.disk_path, "r+b") as disk:
#             disk.seek(inode_bitmap_offset)
#             disk.write(inode_bitmap)
#             disk.flush()
#             os.fsync(disk.fileno())
#         print(f"Inode bitmap (size {DEFAULT_TOTAL_INODES} bits) initialized at block {super_block['inode_bitmap_block']}.")

#         # Create a data bitmap:
#         # Calculate number of bytes needed to represent DEFAULT_TOTAL_BLOCKS bits.
#         data_bitmap_bytes = math.ceil(DEFAULT_TOTAL_BLOCKS / 8)
#         data_bitmap = bytearray(data_bitmap_bytes)  # all bits 0 (free)
#         # Pad to fill a block.
#         data_bitmap += b'\0' * (DEFAULT_BLOCK_SIZE - len(data_bitmap))
#         data_bitmap_offset = DEFAULT_BLOCK_SIZE * super_block["data_bitmap_block"]
#         with open(self.disk_path, "r+b") as disk:
#             disk.seek(data_bitmap_offset)
#             disk.write(data_bitmap)
#             disk.flush()
#             os.fsync(disk.fileno())
#         print(f"Data bitmap (size {DEFAULT_TOTAL_BLOCKS} bits) initialized at block {super_block['data_bitmap_block']}.")

#     def __load_disk(self) -> None:
#         # Your existing logic to load disk and superblock from disk_path.
#         with open(self.disk_path, "rb") as disk:
#             superblock_data = disk.read(DEFAULT_BLOCK_SIZE)
#         try:
#             json_str = superblock_data.rstrip(b'\0').decode("utf-8")
#             self.superblock = json.loads(json_str)
#         except Exception as e:
#             raise Exception(f"Error reading superblock: {e}")
#         print(f"Loaded disk with superblock: {self.superblock}")
    
#     def __load_inode_bitmap(self) -> List[bool]:
#         valid_inode_bytes = math.ceil(DEFAULT_TOTAL_INODES / 8)
#         with open(self.disk_path, "rb") as disk:
#             disk.seek(DEFAULT_BLOCK_SIZE * self.superblock["inode_bitmap_block"])
#             inode_bitmap_data = disk.read(valid_inode_bytes)
#         # Expand the valid bytes into individual bits.
#         bits = []
#         for byte in inode_bitmap_data:
#             for i in range(8):
#                 if len(bits) < DEFAULT_TOTAL_INODES:
#                     # Check bit i (least-significant-bit first)
#                     bits.append(bool(byte & (1 << i)))
#         return bits
    
#     def __load_data_bitmap(self) -> List[bool]:
#         valid_data_bytes = math.ceil(DEFAULT_TOTAL_BLOCKS / 8)
#         with open(self.disk_path, "rb") as disk:
#             disk.seek(DEFAULT_BLOCK_SIZE * self.superblock["data_bitmap_block"])
#             data_bitmap_data = disk.read(valid_data_bytes)
#         bits = []
#         for byte in data_bitmap_data:
#             for i in range(8):
#                 if len(bits) < DEFAULT_TOTAL_BLOCKS:
#                     bits.append(bool(byte & (1 << i)))
#         return bits
    
#     def create_file(self, path: str) -> None:
#         pass

        
