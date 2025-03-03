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

DEFAULT_TOTAL_BLOCKS = 128
DEFAULT_BLOCK_SIZE = 4096
DEFAULT_INODE_SIZE = 256
DEFAULT_TOTAL_INODES = 16

class BasicFileSystem():
    def __init__(self, disk_path: str) -> None:
        self.disk_path = disk_path

        if not os.path.exists(disk_path):
            self.__initialise_disk()
        
        self.__load_disk()
        inode_bitmap = self.__load_inode_bitmap()
        print(inode_bitmap)

    def __initialise_disk(self) -> None:
        with open(self.disk_path, 'wb') as disk:
            disk.write(b'\0' * (DEFAULT_TOTAL_BLOCKS * DEFAULT_BLOCK_SIZE))
            disk.flush()
            os.fsync(disk.fileno())

        super_block = {
            "magic_number": "0xF5F5F5F5",         # Unique identifier for our file system
            "fs_version": "1.0",
            "block_size": DEFAULT_BLOCK_SIZE,
            "total_blocks": DEFAULT_TOTAL_BLOCKS,
            "max_inode_count": DEFAULT_TOTAL_INODES,
            "inode_bitmap_block": 1,
            "data_bitmap_block": 2,
            "inode_start": 4,
            "data_start": 8
        }

        data = json.dumps(super_block).encode("utf-8")
        # Pad with null bytes so that the total is exactly DEFAULT_BLOCK_SIZE bytes
        if len(data) < DEFAULT_BLOCK_SIZE:
            data += b'\0' * (DEFAULT_BLOCK_SIZE - len(data))
        
        with open("disk.img", "r+b") as disk:
            disk.seek(0)
            disk.write(data)
            disk.flush()
            os.fsync(disk.fileno())
        
         # Create an inode bitmap:
        # Calculate number of bytes needed to represent DEFAULT_INODE_COUNT bits.
        inode_bitmap_bytes = math.ceil( DEFAULT_TOTAL_INODES / 8)
        inode_bitmap = bytearray(inode_bitmap_bytes)  # all bits 0 (free)
        # Pad to fill a block.
        inode_bitmap += b'\0' * (DEFAULT_BLOCK_SIZE - len(inode_bitmap))
        inode_bitmap_offset = DEFAULT_BLOCK_SIZE * super_block["inode_bitmap_block"]
        with open(self.disk_path, "r+b") as disk:
            disk.seek(inode_bitmap_offset)
            disk.write(inode_bitmap)
            disk.flush()
            os.fsync(disk.fileno())
        print(f"Inode bitmap (size {DEFAULT_TOTAL_INODES} bits) initialized at block {super_block['inode_bitmap_block']}.")

        # Create a data bitmap:
        # Calculate number of bytes needed to represent DEFAULT_TOTAL_BLOCKS bits.
        data_bitmap_bytes = math.ceil(DEFAULT_TOTAL_BLOCKS / 8)
        data_bitmap = bytearray(data_bitmap_bytes)  # all bits 0 (free)
        # Pad to fill a block.
        data_bitmap += b'\0' * (DEFAULT_BLOCK_SIZE - len(data_bitmap))
        data_bitmap_offset = DEFAULT_BLOCK_SIZE * super_block["data_bitmap_block"]
        with open(self.disk_path, "r+b") as disk:
            disk.seek(data_bitmap_offset)
            disk.write(data_bitmap)
            disk.flush()
            os.fsync(disk.fileno())
        print(f"Data bitmap (size {DEFAULT_TOTAL_BLOCKS} bits) initialized at block {super_block['data_bitmap_block']}.")

    def __load_disk(self) -> None:
        # Your existing logic to load disk and superblock from disk_path.
        with open(self.disk_path, "rb") as disk:
            superblock_data = disk.read(DEFAULT_BLOCK_SIZE)
        try:
            json_str = superblock_data.rstrip(b'\0').decode("utf-8")
            self.superblock = json.loads(json_str)
        except Exception as e:
            raise Exception(f"Error reading superblock: {e}")
        print(f"Loaded disk with superblock: {self.superblock}")
    
    def __load_inode_bitmap(self) -> List[bool]:
        valid_inode_bytes = math.ceil(DEFAULT_TOTAL_INODES / 8)
        with open(self.disk_path, "rb") as disk:
            disk.seek(DEFAULT_BLOCK_SIZE * self.superblock["inode_bitmap_block"])
            inode_bitmap_data = disk.read(valid_inode_bytes)
        # Expand the valid bytes into individual bits.
        bits = []
        for byte in inode_bitmap_data:
            for i in range(8):
                if len(bits) < DEFAULT_TOTAL_INODES:
                    # Check bit i (least-significant-bit first)
                    bits.append(bool(byte & (1 << i)))
        return bits
    
    def __load_data_bitmap(self) -> List[bool]:
        valid_data_bytes = math.ceil(DEFAULT_TOTAL_BLOCKS / 8)
        with open(self.disk_path, "rb") as disk:
            disk.seek(DEFAULT_BLOCK_SIZE * self.superblock["data_bitmap_block"])
            data_bitmap_data = disk.read(valid_data_bytes)
        bits = []
        for byte in data_bitmap_data:
            for i in range(8):
                if len(bits) < DEFAULT_TOTAL_BLOCKS:
                    bits.append(bool(byte & (1 << i)))
        return bits
    
    def create_file(self, path: str) -> None:

        
if __name__ == "__main__":
    fs = BasicFileSystem("disk.img")
    print(fs.superblock)
        


# class BasicFileSystem(FileSystem):
#     """
#     A basic file system implementation that simulates a disk stored in a single file.
#     The disk starts with a superblock that contains metadata such as block size, 
#     total number of blocks, and inode count. Data will be stored in fixed-size 
#     blocks, and the superblock is stored in the first block.
#     """
#     def __init__(self, disk_path: str):
#         """
#         Initialize the file system with a disk file path.
        
#         Args:
#             disk_path (str): Path to the simulated disk file.
#         """
#         self.disk_path = disk_path
#         # Define parameters for our simulated disk.
#         self.block_size = 4096
#         self.total_blocks = 256    # For example, total blocks = 256
#         self.inode_count = 128
#         self.superblock = {}
        
#         if not os.path.exists(disk_path):
#             self._initialize_disk()
#         else:
#             self._load_disk()
    
#     def _initialize_disk(self):
#         """
#         Create a new disk file, initialize it with zeros and write the superblock.
#         """
#         # Create a file (using binary mode) of fixed size.
#         with open(self.disk_path, "wb") as f:
#             f.write(b'\x00' * (self.block_size * self.total_blocks))
        
#         # Setup a simple superblock. In real file systems, the superblock would include more details.
#         self.superblock = {
#             "block_size": self.block_size,
#             "total_blocks": self.total_blocks,
#             "inode_count": self.inode_count,
#             "free_blocks": list(range(1, self.total_blocks)),   # Block 0 reserved for superblock.
#             "files": {}  # Dictionary mapping file paths to metadata (e.g., starting block, size, etc.)
#         }
#         self._write_superblock()
#         print(f"Created new disk at {self.disk_path} with superblock: {self.superblock}")

#     def _load_disk(self):
#         """
#         Load the disk file and read the superblock from the first block.
#         """
#         with open(self.disk_path, "rb") as f:
#             superblock_data = f.read(self.block_size)
#         try:
#             # Remove trailing null bytes and decode the JSON string
#             json_str = superblock_data.rstrip(b'\x00').decode("utf-8")
#             self.superblock = json.loads(json_str)
#         except Exception as e:
#             raise Exception(f"Error reading superblock: {e}")
        
#         self.block_size = self.superblock.get("block_size", self.block_size)
#         self.total_blocks = self.superblock.get("total_blocks", self.total_blocks)
#         self.inode_count = self.superblock.get("inode_count", self.inode_count)
#         print(f"Loaded disk from {self.disk_path} with superblock: {self.superblock}")

#     def _write_superblock(self):
#         """
#         Write the current superblock configuration into the first block of the disk.
#         """
#         data = json.dumps(self.superblock).encode("utf-8")
#         # Pad the data to fit exactly one block.
#         if len(data) < self.block_size:
#             data += b'\x00' * (self.block_size - len(data))
#         with open(self.disk_path, "r+b") as f:
#             f.seek(0)
#             f.write(data)

#     def create_file(self, path: str) -> None:
#         """
#         Create a new file entry in the file system.
#         For simplicity, we register the file in the superblock.
#         """
#         if path in self.superblock["files"]:
#             raise Exception(f"File {path} already exists.")
#         # In a more advanced version, you would allocate an inode and starting block.
#         self.superblock["files"][path] = {
#             "size": 0,
#             "start_block": None,
#             "inodes": []
#         }
#         self._write_superblock()
#         print(f"File {path} created.")

#     def delete_file(self, path: str) -> None:
#         """
#         Delete a file entry from the file system.
#         """
#         if path not in self.superblock["files"]:
#             raise Exception(f"File {path} does not exist.")
#         del self.superblock["files"][path]
#         self._write_superblock()
#         print(f"File {path} deleted.")

#     def read_file(self, path: str, offset: int, size: int) -> bytes:
#         """
#         Simulate reading bytes from a file.
#         This simplified version just reads directly from the disk file starting at a computed offset.
#         """
#         if path not in self.superblock["files"]:
#             raise Exception(f"File {path} not found.")
#         # For demonstration, assume each file is stored contiguously after block 0.
#         # A real system would need to follow inode pointers.
#         start = (1 + list(self.superblock["files"]).index(path)) * self.block_size + offset
#         with open(self.disk_path, "rb") as f:
#             f.seek(start)
#             data = f.read(size)
#         print(f"Read {len(data)} bytes from file {path} starting at offset {offset}.")
#         return data

#     def write_file(self, path: str, data: bytes, offset: int) -> None:
#         """
#         Simulate writing bytes to a file.
#         This simple implementation writes directly into the disk file.
#         """
#         if path not in self.superblock["files"]:
#             raise Exception(f"File {path} not found.")
#         start = (1 + list(self.superblock["files"]).index(path)) * self.block_size + offset
#         with open(self.disk_path, "r+b") as f:
#             f.seek(start)
#             f.write(data)
#         # Update file size in superblock (naively)
#         file_info = self.superblock["files"][path]
#         file_info["size"] = max(file_info.get("size", 0), offset + len(data))
#         self._write_superblock()
#         print(f"Wrote {len(data)} bytes to file {path} at offset {offset}.")

#     def list_directory(self, path: str) -> List[str]:
#         """
#         Return a list of files (for simplicity, only the root directory is supported).
#         """
#         # In this simple file system, assume all files are in the root.
#         return list(self.superblock["files"].keys())

#     def open_file(self, path: str, mode: str) -> None:
#         """
#         Simulate opening a file.
#         Optionally, this could keep track of open handles.
#         """
#         if path not in self.superblock["files"]:
#             raise Exception(f"File {path} not found.")
#         print(f"File {path} opened in mode '{mode}'.")

#     def close_file(self, path: str) -> None:
#         """
#         Simulate closing a file.
#         """
#         if path not in self.superblock["files"]:
#             raise Exception(f"File {path} not found.")
#         print(f"File {path} closed.")