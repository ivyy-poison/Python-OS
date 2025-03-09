import abc
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
    def write_file(self, path: str, data: str) -> None:
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
    def create_directory(self, path: str) -> None:
        """
        Create a new directory in the file system.

        Args:
            path (str): The path of the directory to create.
        """
        pass

    @abc.abstractmethod
    def delete_directory(self, path: str) -> None:
        """
        Delete a directory from the file system.

        Args:
            path (str): The path of the directory to delete.
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
