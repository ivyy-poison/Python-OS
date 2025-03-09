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
