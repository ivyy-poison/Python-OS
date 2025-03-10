import abc

class Storage(abc.ABC):
    """
    Abstract base class for storage"
    """

    @abc.abstractmethod
    def write(self, block_number: int, data: str) -> None:
        """
        Write data to a specific block number.

        Args:
            block_number (int): The block number to write to.
            data (str): The data to write.
        """
        pass

    @abc.abstractmethod
    def read(self, block_number: int) -> str:
        """
        Read data from a specific block number.

        Args:
            block_number (int): The block number to read from.

        Returns:
            str: The data read from the block.
        """
        pass