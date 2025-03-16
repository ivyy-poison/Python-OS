from python_os.process import Process
from typing import Any

import abc

class MemoryManager(abc.ABC):
    """
    Abstract base class for memory management strategies.
    """
    PAGE_SIZE = 4

    @abc.abstractmethod
    def allocate(self, process: Process, size: int) -> None:

        pass

    @abc.abstractmethod
    def deallocate(self, process: Process) -> None:

        pass

    @abc.abstractmethod
    def retrieve(self, process: Process, virtual_address: int) -> Any:
        pass




    
